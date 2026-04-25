from django.shortcuts import render, redirect #type: ignore
from ..models import mainStore_products, cart_items
from ..forms import mainStore_products_form, ProductVariantFormSet
from django.http import JsonResponse #type: ignore
import json
from django.db.models import Q #type: ignore
from decimal import Decimal
from django.contrib.auth.decorators import login_required #type: ignore
from django.views.decorators.http import require_http_methods #type: ignore
from django.core.exceptions import ObjectDoesNotExist #type: ignore
from ..models import mainStore_products, cart_items, mainStore_product_variants

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