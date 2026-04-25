from .models import cart_items


def cart_context(request):
    cart_count = 0

    if request.user.is_authenticated:
        items = cart_items.objects.filter(user=request.user)
        cart_count = sum(item.quantity for item in items)

    elif request.session.session_key:
        items = cart_items.objects.filter(
            user__isnull=True,
            session_key=request.session.session_key
        )
        cart_count = sum(item.quantity for item in items)

    return {
        "global_cart_count": cart_count
    }