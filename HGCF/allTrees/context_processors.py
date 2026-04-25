from .models import cart_items


def cart_context(request):
    cart_count = 0

    if request.user.is_authenticated:
        cart_count = sum(
            item.quantity for item in cart_items.objects.filter(user=request.user)
        )

    return {
        "global_cart_count": cart_count
    }