from decimal import Decimal, ROUND_HALF_UP
import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
import stripe # type: ignore
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from ..models import (
    mainStore_products,
    POSSession,
    POSSale,
    POSSaleItem,
    POSPaymentEvent
)

TAX_RATE = Decimal("0.06")
stripe.api_key = settings.STRIPE_SECRET_KEY

def _money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _generate_sale_number():
    now = timezone.localtime()
    prefix = now.strftime("POS-%Y%m%d")
    last_sale = POSSale.objects.filter(
        sale_number__startswith=prefix
    ).order_by("-id").first()

    if last_sale:
        try:
            last_number = int(last_sale.sale_number.split("-")[-1])
        except Exception:
            last_number = 0
    else:
        last_number = 0

    next_number = last_number + 1
    return f"{prefix}-{str(next_number).zfill(4)}"

def _serialize_product(product):
    return {
        "id": product.id,
        "product_name": product.product_name,
        "sku": product.sku,
        "description": product.description,
        "price": str(product.get_active_price()),
        "regular_price": str(product.price),
        "sale_price": str(product.sale_price) if product.sale_price is not None else None,
        "on_sale": product.on_sale,
        "track_inventory": product.track_inventory,
        "inventory_total": product.inventory_total,
        "inventory_status": product.inventory_status,
        "unit_type": product.unit_type,
        "allow_custom_price": product.allow_custom_price,
        "pos_display_order": product.pos_display_order,
        "mainImage": product.mainImage.url if product.mainImage else None,
    }

def _get_or_create_open_session(user):
    open_session = POSSession.objects.filter(status="open").order_by("-opened_at").first()
    if open_session:
        return open_session

    return POSSession.objects.create(
        status="open",
        opened_by=user if user.is_authenticated else None,
        opening_cash=Decimal("0.00"),
    )

def _build_cart_totals(items):
    subtotal = Decimal("0.00")
    normalized_items = []

    for item in items:
        product_id = item.get("product_id")
        quantity = Decimal(str(item.get("quantity", 1)))
        custom_price = item.get("custom_price")
        weight_amount = item.get("weight_amount")

        product = get_object_or_404(
            mainStore_products,
            id=product_id,
            is_active=True,
            is_active_offline=True
        )

        if custom_price not in [None, ""]:
            if not product.allow_custom_price:
                raise ValueError(f"{product.product_name} does not allow custom pricing.")
            unit_price = _money(str(custom_price))
        else:
            unit_price = _money(product.get_active_price())

        if product.unit_type == "weight":
            if weight_amount in [None, ""]:
                raise ValueError(f"{product.product_name} requires a weight amount.")
            quantity = Decimal(str(weight_amount))

        line_subtotal = _money(unit_price * quantity)
        subtotal += line_subtotal

        normalized_items.append({
            "product": product,
            "product_name_snapshot": product.product_name,
            "sku_snapshot": product.sku,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_subtotal": line_subtotal,
            "sold_by_weight": product.unit_type == "weight",
            "weight_amount": quantity if product.unit_type == "weight" else None,
        })

    tax_amount = _money(subtotal * TAX_RATE)
    total = _money(subtotal + tax_amount)

    return {
        "items": normalized_items,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total": total,
    }

def _get_terminal_location_id():
    location_id = getattr(settings, "STRIPE_TERMINAL_LOCATION_ID", "")
    if not location_id:
        raise ValueError("STRIPE_TERMINAL_LOCATION_ID is not configured.")
    return location_id

def _create_terminal_payment_intent_for_sale(sale):
    amount_cents=int((sale.total * Decimal("100")).quantize(Decimal("1")))

    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency=getattr(settings, "STRIPE_TERMINAL_CURRENCY", "usd"),
        capture_method="automatic",
        payment_method_types=["card_present"],
        metadata={
            "source": "allTrees_pos",
            "sale_id": str(sale.id),
            "sale_number": sale.sale_number,
        },
    )
    return intent

def _apply_inventory_deductions_for_sale(sale):
    for item in sale.items.select_related("product").all():
        product = item.product
        if not product:
            continue

        if product.track_inventory and product.inventory_total is not None:
            deduction_amount = int(item.quantity)
            product.inventory_total = max(0, product.inventory_total - deduction_amount)

            if product.inventory_total <= 0:
                product.inventory_status = "out_of_stock"
            else:
                product.inventory_status = "in_stock"

            product.save(update_fields=["inventory_total", "inventory_status"])

def _sync_sale_from_payment_intent(sale, intent):
    latest_charge = getattr(intent, "latest_charge", None)
    receipt_url = None
    charge_id = None

    if latest_charge:
        receipt_url = getattr(latest_charge, "receipt_url", None)
        charge_id = getattr(latest_charge, "id", None)

    sale.stripe_payment_status = getattr(intent, "status", None)

    if intent.status == "succeeded":
        was_completed = sale.status == "completed"

        sale.payment_method = "card"
        sale.payment_status = "completed"
        sale.status = "completed"
        sale.completed_at = sale.completed_at or timezone.now()
        sale.stripe_charge_id = charge_id
        sale.stripe_receipt_url = receipt_url

        if not was_completed:
            _apply_inventory_deductions_for_sale(sale)

    elif intent.status == "canceled":
        sale.payment_status = "canceled"

    elif intent.status in ["requires_payment_method"]:
        sale.payment_status = "failed"

    else:
        sale.payment_status = "processing"

    sale.save(update_fields=[
        "payment_method",
        "payment_status",
        "status",
        "completed_at",
        "stripe_payment_status",
        "stripe_charge_id",
        "stripe_receipt_url",
    ])

@login_required
@require_GET
def pos_terminal_page(request):
    session = _get_or_create_open_session(request.user)
    noFooter = True
    smallHeader = True
    sideBar = True

    return render(request, "pos/pos_terminal.html", {
        "page_title": "Farm POS",
        "tax_rate": str(TAX_RATE),
        "open_session": session,
        'noFooter': noFooter, 
        'smallHeader': smallHeader,
        'sideBar': sideBar,
    })

@login_required
@require_GET
def pos_products_api(request):
    products = mainStore_products.objects.filter(
        is_active=True,
        is_active_offline=True
    ).order_by("pos_display_order", "product_name")

    data = [_serialize_product(product) for product in products]
    return JsonResponse({
        "success": True,
        "products": data,
    })

@login_required
@require_POST
def pos_calculate_totals_api(request):
    try:
        payload = json.loads(request.body)
        items = payload.get("items", [])

        if not items:
            return JsonResponse({
                "success": False,
                "message": "No cart items were provided."
            }, status=400)

        totals = _build_cart_totals(items)

        response_items = []
        for item in totals["items"]:
            response_items.append({
                "product_id": item["product"].id,
                "product_name": item["product_name_snapshot"],
                "sku": item["sku_snapshot"],
                "quantity": str(item["quantity"]),
                "unit_price": str(item["unit_price"]),
                "line_subtotal": str(item["line_subtotal"]),
                "sold_by_weight": item["sold_by_weight"],
                "weight_amount": str(item["weight_amount"]) if item["weight_amount"] is not None else None,
            })

        return JsonResponse({
            "success": True,
            "items": response_items,
            "subtotal": str(totals["subtotal"]),
            "tax_amount": str(totals["tax_amount"]),
            "total": str(totals["total"]),
        })

    except ValueError as e:
        return JsonResponse({
            "success": False,
            "message": str(e),
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Unable to calculate totals: {str(e)}",
        }, status=500)

@login_required
@require_POST
@transaction.atomic
def pos_create_sale_api(request):
    try:
        payload = json.loads(request.body)
        items = payload.get("items", [])
        customer_name = payload.get("customer_name")
        customer_email = payload.get("customer_email")
        notes = payload.get("notes")

        if not items:
            return JsonResponse({
                "success": False,
                "message": "Cannot create a sale with no items."
            }, status=400)

        totals = _build_cart_totals(items)
        session = _get_or_create_open_session(request.user)

        sale = POSSale.objects.create(
            sale_number=_generate_sale_number(),
            session=session,
            status="open",
            subtotal=totals["subtotal"],
            tax_amount=totals["tax_amount"],
            total=totals["total"],
            customer_name=customer_name,
            customer_email=customer_email,
            notes=notes,
            created_by=request.user,
        )

        for item in totals["items"]:
            POSSaleItem.objects.create(
                sale=sale,
                product=item["product"],
                product_name_snapshot=item["product_name_snapshot"],
                sku_snapshot=item["sku_snapshot"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                line_subtotal=item["line_subtotal"],
                sold_by_weight=item["sold_by_weight"],
                weight_amount=item["weight_amount"],
            )

        return JsonResponse({
            "success": True,
            "sale_id": sale.id,
            "sale_number": sale.sale_number,
            "subtotal": str(sale.subtotal),
            "tax_amount": str(sale.tax_amount),
            "total": str(sale.total),
            "message": "Sale created successfully.",
        })

    except ValueError as e:
        return JsonResponse({
            "success": False,
            "message": str(e),
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Unable to create sale: {str(e)}",
        }, status=500)

@login_required
@require_GET
def pos_sale_detail_api(request, sale_id):
    sale = get_object_or_404(POSSale, id=sale_id)

    items = []
    for item in sale.items.all().order_by("id"):
        items.append({
            "id": item.id,
            "product_id": item.product.id if item.product else None,
            "product_name": item.product_name_snapshot,
            "sku": item.sku_snapshot,
            "quantity": str(item.quantity),
            "unit_price": str(item.unit_price),
            "line_subtotal": str(item.line_subtotal),
            "sold_by_weight": item.sold_by_weight,
            "weight_amount": str(item.weight_amount) if item.weight_amount is not None else None,
        })

    return JsonResponse({
        "success": True,
        "sale": {
            "id": sale.id,
            "sale_number": sale.sale_number,
            "status": sale.status,
            "payment_method": sale.payment_method,
            "subtotal": str(sale.subtotal),
            "tax_amount": str(sale.tax_amount),
            "total": str(sale.total),
            "cash_received": str(sale.cash_received) if sale.cash_received is not None else None,
            "cash_change": str(sale.cash_change) if sale.cash_change is not None else None,
            "customer_name": sale.customer_name,
            "customer_email": sale.customer_email,
            "notes": sale.notes,
            "created_at": sale.created_at.isoformat() if sale.created_at else None,
            "completed_at": sale.completed_at.isoformat() if sale.completed_at else None,
            "items": items,
        }
    })

@login_required
@require_POST
@transaction.atomic
def pos_complete_cash_sale_api(request, sale_id):
    sale = get_object_or_404(POSSale, id=sale_id)

    if sale.status != "open":
        return JsonResponse({
            "success": False,
            "message": "Only open sales can be completed."
        }, status=400)

    try:
        payload = json.loads(request.body)
        cash_received = _money(str(payload.get("cash_received", "0.00")))

        if cash_received < sale.total:
            return JsonResponse({
                "success": False,
                "message": "Cash received is less than the total."
            }, status=400)

        cash_change = _money(cash_received - sale.total)

        _apply_inventory_deductions_for_sale(sale)

        sale.payment_method = "cash"
        sale.cash_received = cash_received
        sale.cash_change = cash_change
        sale.status = "completed"
        sale.completed_at = timezone.now()
        sale.save(update_fields=[
            "payment_method",
            "cash_received",
            "cash_change",
            "status",
            "completed_at",
        ])

        return JsonResponse({
            "success": True,
            "message": "Cash sale completed successfully.",
            "sale_id": sale.id,
            "sale_number": sale.sale_number,
            "payment_method": sale.payment_method,
            "cash_received": str(sale.cash_received),
            "cash_change": str(sale.cash_change),
            "status": sale.status,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Unable to complete cash sale: {str(e)}"
        }, status=500)
    
@login_required
@require_GET
def pos_terminal_readers_api(request):
    try:
        location_id = _get_terminal_location_id()

        readers = stripe.terminal.Reader.list(
            location=location_id,
            limit=100
        )

        reader_data = []
        for reader in readers.auto_paging_iter():
            reader_data.append({
                "id": reader.id,
                "label": getattr(reader, "label", None),
                "device_type": getattr(reader, "device_type", None),
                "status": getattr(reader, "status", None),
                "location": reader.location if hasattr(reader, "location") else None,
                "serial_number": getattr(reader, "serial_number", None),
            })

        return JsonResponse({
            "success": True,
            "readers": reader_data,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Unable to load readers: {str(e)}",
        }, status=500)

@login_required
@require_POST
@transaction.atomic
def pos_start_card_payment_api(request, sale_id):
    sale = get_object_or_404(POSSale, id=sale_id)

    if sale.status != "open":
        return JsonResponse({
            "success": False,
            "message": "Only open sales can start card payment."
        }, status=400)

    try:
        payload = json.loads(request.body)
        reader_id = payload.get("reader_id")

        if not reader_id:
            return JsonResponse({
                "success": False,
                "message": "reader_id is required."
            }, status=400)

        location_id = _get_terminal_location_id()

        if not sale.stripe_payment_intent_id:
            intent = _create_terminal_payment_intent_for_sale(sale)
            sale.stripe_payment_intent_id = intent.id
        else:
            intent = stripe.PaymentIntent.retrieve(sale.stripe_payment_intent_id)

        stripe.terminal.Reader.process_payment_intent(
            reader_id,
            payment_intent=intent.id
        )

        sale.payment_method = "card"
        sale.payment_status = "processing"
        sale.stripe_terminal_reader_id = reader_id
        sale.stripe_terminal_location_id = location_id
        sale.stripe_payment_status = getattr(intent, "status", None)
        sale.save(update_fields=[
            "stripe_payment_intent_id",
            "payment_method",
            "payment_status",
            "stripe_terminal_reader_id",
            "stripe_terminal_location_id",
            "stripe_payment_status",
        ])

        POSPaymentEvent.objects.create(
            sale=sale,
            provider="stripe",
            event_type="reader_process_payment_intent_started",
            external_id=intent.id,
            payload_json={
                "reader_id": reader_id,
                "payment_intent_id": intent.id,
            }
        )

        return JsonResponse({
            "success": True,
            "message": "Card payment started on reader.",
            "sale_id": sale.id,
            "sale_number": sale.sale_number,
            "reader_id": reader_id,
            "payment_intent_id": intent.id,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Unable to start card payment: {str(e)}",
        }, status=500)

@login_required
@require_GET
def pos_card_payment_status_api(request, sale_id):
    sale = get_object_or_404(POSSale, id=sale_id)

    if not sale.stripe_payment_intent_id:
        return JsonResponse({
            "success": False,
            "message": "This sale has no Stripe payment intent."
        }, status=400)

    try:
        intent = stripe.PaymentIntent.retrieve(
            sale.stripe_payment_intent_id,
            expand=["latest_charge"]
        )

        _sync_sale_from_payment_intent(sale, intent)

        return JsonResponse({
            "success": True,
            "sale_id": sale.id,
            "sale_number": sale.sale_number,
            "payment_status": sale.payment_status,
            "stripe_payment_status": sale.stripe_payment_status,
            "stripe_charge_id": sale.stripe_charge_id,
            "stripe_receipt_url": sale.stripe_receipt_url,
            "sale_status": sale.status,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Unable to check card payment status: {str(e)}",
        }, status=500)

@login_required
@require_POST
@transaction.atomic
def pos_cancel_card_payment_api(request, sale_id):
    sale = get_object_or_404(POSSale, id=sale_id)

    if not sale.stripe_payment_intent_id:
        return JsonResponse({
            "success": False,
            "message": "No Stripe payment intent found for this sale."
        }, status=400)

    try:
        intent = stripe.PaymentIntent.cancel(sale.stripe_payment_intent_id)

        sale.payment_status = "canceled"
        sale.stripe_payment_status = intent.status
        sale.save(update_fields=["payment_status", "stripe_payment_status"])

        POSPaymentEvent.objects.create(
            sale=sale,
            provider="stripe",
            event_type="payment_intent_canceled",
            external_id=intent.id,
            payload_json={"status": intent.status}
        )

        return JsonResponse({
            "success": True,
            "message": "Card payment canceled.",
            "payment_intent_id": intent.id,
            "stripe_payment_status": intent.status,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Unable to cancel card payment: {str(e)}",
        }, status=500)

@csrf_exempt
@require_POST
def stripe_terminal_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=webhook_secret
            )
        else:
            event = json.loads(payload.decode("utf-8"))
    except ValueError:
        return JsonResponse({
            "success": False,
            "message": "Invalid payload."
        }, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({
            "success": False,
            "message": "Invalid Stripe signature."
        }, status=400)

    event_type = event.get("type")
    event_data = event.get("data", {})
    event_object = event_data.get("object", {})

    payment_intent_id = event_object.get("id")
    sale = None

    if payment_intent_id:
        sale = POSSale.objects.filter(
            stripe_payment_intent_id=payment_intent_id
        ).first()

    if sale:
        POSPaymentEvent.objects.create(
            sale=sale,
            provider="stripe",
            event_type=event_type,
            external_id=payment_intent_id,
            payload_json=event_object
        )

        try:
            if event_type in [
                "payment_intent.succeeded",
                "payment_intent.payment_failed",
                "payment_intent.canceled",
                "payment_intent.processing",
                "payment_intent.requires_action",
                "payment_intent.amount_capturable_updated",
            ]:
                intent = stripe.PaymentIntent.retrieve(
                    payment_intent_id,
                    expand=["latest_charge"]
                )
                _sync_sale_from_payment_intent(sale, intent)

        except Exception as e:
            POSPaymentEvent.objects.create(
                sale=sale,
                provider="stripe",
                event_type="webhook_sync_error",
                external_id=payment_intent_id,
                payload_json={
                    "error": str(e),
                    "source_event": event_type,
                }
            )

            return JsonResponse({
                "success": False,
                "message": f"Webhook received but sync failed: {str(e)}"
            }, status=500)

    return JsonResponse({
        "success": True
    })


