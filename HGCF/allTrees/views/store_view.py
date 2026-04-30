from django.shortcuts import render, redirect, get_object_or_404 #type: ignore
from ..models import mainStore_products, cart_items
from ..forms import mainStore_products_form, ProductVariantFormSet
from django.http import JsonResponse #type: ignore
import json
import stripe
from django.conf import settings
from django.db.models import Q #type: ignore
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required #type: ignore
from django.views.decorators.http import require_http_methods, require_POST #type: ignore
from django.core.exceptions import ObjectDoesNotExist #type: ignore
from django.views.decorators.csrf import csrf_exempt #type: ignore
from ..models import mainStore_products, cart_items, mainStore_product_variants, StoreOrder, StoreOrderItem
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_or_create_cart_session_key(request):
    """
    Ensures guest users have a session key we can attach cart items to.
    """
    if not request.session.session_key:
        request.session.create()

    return request.session.session_key

def get_cart_filter(request):
    """
    Returns the right cart filter depending on whether the customer is logged in.
    """
    if request.user.is_authenticated:
        return {
            "user": request.user
        }

    session_key = get_or_create_cart_session_key(request)

    return {
        "user__isnull": True,
        "session_key": session_key
    }

def get_cart_items_for_request(request):
    return cart_items.objects.filter(
        **get_cart_filter(request)
    ).select_related(
        "product",
        "variant"
    )

def get_cart_count(request):
    items = get_cart_items_for_request(request)
    return sum(item.quantity for item in items)

@require_http_methods(["GET", "POST"])
def store_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False

    allProducts = mainStore_products.objects.filter(
        is_active=True,
        is_active_online=True,
        show_in_store=True
    ).order_by("store_display_order", "product_name")

    if request.method == "POST":
        try:
            json_data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "Invalid request data."
            }, status=400)

        product_id = json_data.get("product_id")
        variant_id = json_data.get("variant_id")

        if not product_id:
            return JsonResponse({
                "success": False,
                "message": "Missing product ID."
            }, status=400)

        try:
            product = mainStore_products.objects.get(
                pk=product_id,
                is_active=True,
                is_active_online=True,
                show_in_store=True
            )
        except mainStore_products.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": "Product not found."
            }, status=404)

        variant = None

        product_has_variants = product.variants.filter(
            is_active=True,
            is_active_online=True
        ).exists()

        if product_has_variants:
            if not variant_id:
                return JsonResponse({
                    "success": False,
                    "message": "Please select a size or option before adding this item."
                }, status=400)

            try:
                variant = mainStore_product_variants.objects.get(
                    pk=variant_id,
                    product=product,
                    is_active=True,
                    is_active_online=True
                )
            except mainStore_product_variants.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": "Selected size or option is not available."
                }, status=404)

        cart_owner = {}

        if request.user.is_authenticated:
            cart_owner["user"] = request.user
            cart_owner["session_key"] = None
        else:
            cart_owner["user"] = None
            cart_owner["session_key"] = get_or_create_cart_session_key(request)

        cart_item, item_created = cart_items.objects.get_or_create(
            product=product,
            variant=variant,
            **cart_owner,
            defaults={"quantity": 1}
        )

        if not item_created:
            cart_item.quantity += 1
            cart_item.save(update_fields=["quantity"])

        cart_count = get_cart_count(request)

        item_name = product.product_name

        if variant:
            item_name = f"{product.product_name} - {variant.get_variant_label()}"

        return JsonResponse({
            "success": True,
            "message": f"{item_name} added to your cart.",
            "cartCount": cart_count,
            "productId": product.id,
            "variantId": variant.id if variant else None
        })

    cart_count = 0

    if request.user.is_authenticated:
        cart_count = sum(
            item.quantity for item in cart_items.objects.filter(user=request.user)
        )

    return render(request, "store/store.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "allProducts": allProducts,
        "cart_count": cart_count,
    })

@require_http_methods(["GET", "POST"])
def addProduct_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    if request.method == "POST":
        productForm = mainStore_products_form(request.POST, request.FILES)

        if productForm.is_valid():
            product = productForm.save()

            variantFormset = ProductVariantFormSet(
                request.POST,
                instance=product,
                prefix="variants"
            )

            if variantFormset.is_valid():
                variantFormset.save()
                return redirect("store")
            else:
                product.delete()
        else:
            variantFormset = ProductVariantFormSet(
                request.POST,
                prefix="variants"
            )

    else:
        productForm = mainStore_products_form()
        variantFormset = ProductVariantFormSet(prefix="variants")

    return render(request, "store/addProduct.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "productForm": productForm,
        "variantFormset": variantFormset,
    })

def cart_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False

    cartItems = get_cart_items_for_request(request).order_by("-created_at")

    cart_subtotal = Decimal("0.00")
    cart_count = 0

    for item in cartItems:
        cart_subtotal += item.get_total()
        cart_count += item.quantity

    return render(request, "store/cart.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "cartItems": cartItems,
        "cart_subtotal": cart_subtotal,
        "cart_count": cart_count,
    })

@require_http_methods(["POST"])
def update_cart_item(request):
    try:
        json_data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid request data."
        }, status=400)

    cart_item_id = json_data.get("cart_item_id")
    quantity = json_data.get("quantity")

    if not cart_item_id:
        return JsonResponse({
            "success": False,
            "message": "Missing cart item."
        }, status=400)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return JsonResponse({
            "success": False,
            "message": "Invalid quantity."
        }, status=400)

    if quantity < 1:
        return JsonResponse({
            "success": False,
            "message": "Quantity must be at least 1."
        }, status=400)

    try:
        cart_item = cart_items.objects.select_related(
            "product",
            "variant"
        ).get(
            id=cart_item_id,
            **get_cart_filter(request)
        )
    except cart_items.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Cart item not found."
        }, status=404)

    cart_item.quantity = quantity
    cart_item.save(update_fields=["quantity"])

    cartItems = get_cart_items_for_request(request)

    cart_subtotal = Decimal("0.00")
    cart_count = 0

    for item in cartItems:
        cart_subtotal += item.get_total()
        cart_count += item.quantity

    return JsonResponse({
        "success": True,
        "message": "Cart updated.",
        "itemTotal": f"{cart_item.get_total():.2f}",
        "cartSubtotal": f"{cart_subtotal:.2f}",
        "cartCount": cart_count,
    })

@require_http_methods(["POST"])
def remove_cart_item(request):
    try:
        json_data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid request data."
        }, status=400)

    cart_item_id = json_data.get("cart_item_id")

    if not cart_item_id:
        return JsonResponse({
            "success": False,
            "message": "Missing cart item."
        }, status=400)

    try:
        cart_item = cart_items.objects.get(
            id=cart_item_id,
            **get_cart_filter(request)
        )
    except cart_items.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Cart item not found."
        }, status=404)

    cart_item.delete()

    cartItems = get_cart_items_for_request(request)

    cart_subtotal = Decimal("0.00")
    cart_count = 0

    for item in cartItems:
        cart_subtotal += item.get_total()
        cart_count += item.quantity

    return JsonResponse({
        "success": True,
        "message": "Item removed from cart.",
        "cartSubtotal": f"{cart_subtotal:.2f}",
        "cartCount": cart_count,
    })

def build_cart_line_items(cartItems):
    line_items = []

    for item in cartItems:
        price = item.get_price()

        unit_amount = int(price * Decimal("100"))

        product_name = item.get_item_name()

        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product_name,
                    "description": "Heaven’s Gates Cherry Farm",
                },
                "unit_amount": unit_amount,
            },
            "quantity": item.quantity,
        })

    return line_items

def decimal_to_cents(amount):
    amount = Decimal(amount or "0.00")
    cents = (amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)

def build_cart_line_items(cartItems):
    line_items = []

    for item in cartItems:
        unit_price = item.get_price()
        product_name = item.get_item_name()
        unit_amount = decimal_to_cents(unit_price)

        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product_name,
                    "description": "Heaven’s Gates Cherry Farm",
                },
                "unit_amount": unit_amount,
            },
            "quantity": item.quantity,
        })

    return line_items

def create_pending_order_from_cart(request, cartItems):
    with transaction.atomic():
        session_key = request.session.session_key

        order = StoreOrder.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            status="pending",
            fulfillment_type="pickup",
        )

        subtotal = Decimal("0.00")

        for cart_item in cartItems:
            unit_price = cart_item.get_price()
            line_total = unit_price * cart_item.quantity

            product = cart_item.product
            variant = cart_item.variant

            StoreOrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                product_name=product.product_name,
                variant_name=variant.get_variant_label() if variant else None,
                sku=variant.sku if variant and variant.sku else product.sku,
                unit_price=unit_price,
                quantity=cart_item.quantity,
                line_total=line_total,
                unit_label=product.get_unit_display_label() if hasattr(product, "get_unit_display_label") else None,
            )

            subtotal += line_total

        order.subtotal = subtotal
        order.total = subtotal
        order.save(update_fields=["subtotal", "total"])

        return order

def cart_requires_shipping(cartItems):
    for item in cartItems:
        fulfillment_type = getattr(item.product, "fulfillment_type", "")

        if fulfillment_type in ["shipping_only", "pickup_or_shipping", "local_delivery"]:
            return True

    return False

@require_POST
def create_checkout_session_view(request):
    if not settings.STRIPE_SECRET_KEY:
        return JsonResponse({
            "success": False,
            "message": "Stripe secret key is not configured."
        }, status=500)

    if not request.session.session_key:
        request.session.create()

    cartItems = get_cart_items_for_request(request)

    if not cartItems.exists():
        return JsonResponse({
            "success": False,
            "message": "Your cart is empty."
        }, status=400)

    line_items = build_cart_line_items(cartItems)

    try:
        order = create_pending_order_from_cart(request, cartItems)

        checkout_payload = {
            "mode": "payment",
            "line_items": line_items,
            "payment_method_collection": "if_required",

            "customer_email": request.user.email if request.user.is_authenticated and request.user.email else None,

            "name_collection": {
                "individual": {
                    "enabled": True,
                    "optional": False,
                },
            },

            "phone_number_collection": {
                "enabled": True,
            },

            "billing_address_collection": "required",

            "success_url": request.build_absolute_uri(
                f"/checkout/success/?order_id={order.id}&session_id={{CHECKOUT_SESSION_ID}}"
            ),
            "cancel_url": request.build_absolute_uri("/cart/"),

            "metadata": {
                "order_id": str(order.id),
                "cart_session_key": request.session.session_key or "",
                "user_id": str(request.user.id) if request.user.is_authenticated else "",
            },

            "payment_intent_data": {
                "metadata": {
                    "order_id": str(order.id),
                }
            }
        }

        if cart_requires_shipping(cartItems):
            checkout_payload["shipping_address_collection"] = {
                "allowed_countries": ["US"],
            }

        checkout_session = stripe.checkout.Session.create(**checkout_payload)

        order.stripe_checkout_session_id = checkout_session.id
        order.save(update_fields=["stripe_checkout_session_id"])

        return JsonResponse({
            "success": True,
            "checkoutUrl": checkout_session.url
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)

def checkout_success_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False

    order_id = request.GET.get("order_id")
    session_id = request.GET.get("session_id")

    order = None

    if order_id:
        order = get_object_or_404(StoreOrder, id=order_id)

    return render(request, "store/checkout_success.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "order": order,
        "session_id": session_id,
    })

@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    if not endpoint_secret:
        return HttpResponse("Webhook secret not configured.", status=500)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )
    except ValueError:
        return HttpResponse("Invalid payload.", status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature.", status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        handle_checkout_session_completed(session)

    return HttpResponse(status=200)

def stripe_obj_get(obj, key, default=None):
    """
    Safely gets values from StripeObject or dict-like objects.
    StripeObject does not always support .get().
    """
    try:
        value = obj[key]
    except (KeyError, TypeError, AttributeError):
        value = getattr(obj, key, default)

    if value is None:
        return default

    return value


def split_name(full_name):
    if not full_name:
        return "", ""

    parts = full_name.strip().split()

    if len(parts) == 1:
        return parts[0], ""

    return parts[0], " ".join(parts[1:])


def save_address_to_order(order, prefix, address_data, name=None):
    if not address_data:
        return []

    update_fields = []

    field_map = {
        "line1": f"{prefix}_line1",
        "line2": f"{prefix}_line2",
        "city": f"{prefix}_city",
        "state": f"{prefix}_state",
        "postal_code": f"{prefix}_postal_code",
        "country": f"{prefix}_country",
    }

    if name:
        setattr(order, f"{prefix}_name", name)
        update_fields.append(f"{prefix}_name")

    for stripe_key, model_field in field_map.items():
        value = stripe_obj_get(address_data, stripe_key)

        if value:
            setattr(order, model_field, value)
            update_fields.append(model_field)

    return update_fields


def handle_checkout_session_completed(session):
    metadata = stripe_obj_get(session, "metadata", {}) or {}
    order_id = stripe_obj_get(metadata, "order_id")

    if not order_id:
        print("Stripe webhook completed but no order_id metadata found.")
        return

    try:
        order = StoreOrder.objects.get(id=order_id)
    except StoreOrder.DoesNotExist:
        print(f"Stripe webhook completed but StoreOrder {order_id} was not found.")
        return

    if order.status == "paid":
        print(f"Order {order.id} already marked paid. Skipping duplicate webhook.")
        return

    customer_details = stripe_obj_get(session, "customer_details", {}) or {}

    customer_email = (
        stripe_obj_get(customer_details, "email")
        or stripe_obj_get(session, "customer_email")
        or order.customer_email
    )

    customer_name = (
        stripe_obj_get(customer_details, "name")
        or order.customer_name
    )

    customer_phone = (
        stripe_obj_get(customer_details, "phone")
        or order.customer_phone
    )

    first_name, last_name = split_name(customer_name)

    update_fields = [
        "status",
        "paid_at",
        "customer_email",
        "customer_name",
        "customer_first_name",
        "customer_last_name",
        "customer_phone",
        "stripe_payment_intent_id",
    ]

    order.status = "paid"
    order.paid_at = timezone.now()
    order.customer_email = customer_email
    order.customer_name = customer_name
    order.customer_first_name = first_name
    order.customer_last_name = last_name
    order.customer_phone = customer_phone
    order.stripe_payment_intent_id = (
        stripe_obj_get(session, "payment_intent")
        or order.stripe_payment_intent_id
    )

    # Billing address
    billing_address = stripe_obj_get(customer_details, "address")
    update_fields += save_address_to_order(
        order,
        "billing",
        billing_address,
        name=customer_name
    )

    # Shipping address
    shipping_details = stripe_obj_get(session, "shipping_details", {}) or {}
    shipping_address = stripe_obj_get(shipping_details, "address")
    shipping_name = stripe_obj_get(shipping_details, "name")

    update_fields += save_address_to_order(
        order,
        "shipping",
        shipping_address,
        name=shipping_name
    )

    order.save(update_fields=list(set(update_fields)))

    if order.user:
        cart_items.objects.filter(user=order.user).delete()
    elif order.session_key:
        cart_items.objects.filter(
            user__isnull=True,
            session_key=order.session_key
        ).delete()

    reduce_inventory_for_order(order)

    print(f"Order {order.id} marked paid from Stripe webhook.")

def reduce_inventory_for_order(order):
    for item in order.items.select_related("product", "variant"):
        if item.variant and item.variant.track_inventory and item.variant.inventory_total is not None:
            item.variant.inventory_total -= item.quantity

            if item.variant.inventory_total < 0:
                item.variant.inventory_total = 0

            item.variant.save(update_fields=["inventory_total"])

        elif item.product and item.product.track_inventory and item.product.inventory_total is not None:
            item.product.inventory_total -= item.quantity

            if item.product.inventory_total < 0:
                item.product.inventory_total = 0

            item.product.save(update_fields=["inventory_total"])


