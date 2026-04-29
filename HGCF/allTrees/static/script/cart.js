function getCSRFToken() {
    const csrfInput = document.querySelector("input[name='csrfmiddlewaretoken']");
    if (csrfInput) {
        return csrfInput.value;
    }

    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookieValue ? cookieValue.split("=")[1] : "";
}

function changeQuantity(cartItemId, amount) {
    const quantityInput = document.getElementById(`quantity-${cartItemId}`);

    if (!quantityInput) return;

    let currentQuantity = parseInt(quantityInput.value || "1", 10);
    let newQuantity = currentQuantity + amount;

    if (newQuantity < 1) {
        newQuantity = 1;
    }

    quantityInput.value = newQuantity;

    updateCartItem(cartItemId);
}

async function updateCartItem(cartItemId) {
    const quantityInput = document.getElementById(`quantity-${cartItemId}`);

    if (!quantityInput) return;

    const quantity = quantityInput.value;

    try {
        const response = await fetch("/cart/update/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                cart_item_id: cartItemId,
                quantity: quantity
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showCartToast(data.message || "Could not update cart.", true);
            return;
        }

        const itemTotal = document.getElementById(`item-total-${cartItemId}`);
        const cartSubtotal = document.getElementById("cartSubtotal");
        const cartCount = document.getElementById("cartCount");

        if (itemTotal) {
            itemTotal.textContent = `$${data.itemTotal}`;
        }

        if (cartSubtotal) {
            cartSubtotal.textContent = `$${data.cartSubtotal}`;
        }

        if (cartCount) {
            cartCount.textContent = data.cartCount;
        }

        showCartToast("Cart updated.");

    } catch (error) {
        console.error("Update cart error:", error);
        showCartToast("Something went wrong updating the cart.", true);
    }
}

async function removeCartItem(cartItemId) {
    try {
        const response = await fetch("/cart/remove/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                cart_item_id: cartItemId
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showCartToast(data.message || "Could not remove item.", true);
            return;
        }

        const cartItem = document.getElementById(`cart-item-${cartItemId}`);
        const cartSubtotal = document.getElementById("cartSubtotal");
        const cartCount = document.getElementById("cartCount");

        if (cartItem) {
            cartItem.remove();
        }

        if (cartSubtotal) {
            cartSubtotal.textContent = `$${data.cartSubtotal}`;
        }

        if (cartCount) {
            cartCount.textContent = data.cartCount;
        }

        showCartToast("Item removed.");

        if (parseInt(data.cartCount, 10) === 0) {
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }

    } catch (error) {
        console.error("Remove cart error:", error);
        showCartToast("Something went wrong removing the item.", true);
    }
}

function showCartToast(message, isError = false) {
    const toast = document.getElementById("storeToast");

    if (!toast) {
        alert(message);
        return;
    }

    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("show");

    clearTimeout(window.cartToastTimer);

    window.cartToastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2400);
}

async function startCheckout() {
    try {
        const response = await fetch("/checkout/create-session/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showCartToast(data.message || "Could not start checkout.", true);
            return;
        }

        window.location.href = data.checkoutUrl;

    } catch (error) {
        console.error("Checkout error:", error);
        showCartToast("Something went wrong starting checkout.", true);
    }
}