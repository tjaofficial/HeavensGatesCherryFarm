function getCSRFToken() {
    const csrfInput = document.querySelector("input[name='csrfmiddlewaretoken']");
    if (csrfInput) {
        return csrfInput.value;
    }

    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : "";
}

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return null;
}

function showStoreToast(message, isError = false) {
    const toast = document.getElementById("storeToast");

    if (!toast) {
        alert(message);
        return;
    }

    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("show");

    clearTimeout(window.storeToastTimer);

    window.storeToastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2800);
}

function showToast(message, isError = false) {
    showStoreToast(message, isError);
}

function changeProductQty(scope, productId, change) {
    const input = document.getElementById(`qty-${scope}-${productId}`);

    if (!input) {
        console.warn(`Quantity input not found: qty-${scope}-${productId}`);
        return;
    }

    const min = parseInt(input.getAttribute("min") || "1", 10);
    const max = input.getAttribute("max") ? parseInt(input.getAttribute("max"), 10) : null;

    let value = parseInt(input.value || "1", 10);

    if (Number.isNaN(value)) {
        value = 1;
    }

    value += change;

    if (value < min) value = min;
    if (max !== null && value > max) value = max;

    input.value = value;
}

function getProductQty(scope, productId) {
    const input = document.getElementById(`qty-${scope}-${productId}`);

    if (!input) {
        return 1;
    }

    let value = parseInt(input.value || "1", 10);

    if (Number.isNaN(value) || value < 1) {
        value = 1;
    }

    const max = input.getAttribute("max") ? parseInt(input.getAttribute("max"), 10) : null;

    if (max !== null && value > max) {
        value = max;
        input.value = max;
    }

    return value;
}

function getSelectedVariantId(productId) {
    const variantSelect = document.getElementById(`variant-${productId}`);

    if (!variantSelect) {
        return "";
    }

    return variantSelect.value || "";
}

function updateCartCounter(count) {
    const cartCountEls = document.querySelectorAll(
        "#cartCounter, #cartCount, .cart-counter, .cart-count, [data-cart-count]"
    );

    cartCountEls.forEach(el => {
        el.textContent = count;
    });
}

function addToCart(productId, scope = "card") {
    const quantity = getProductQty(scope, productId);
    const variantId = getSelectedVariantId(productId);
    const csrfToken = getCookie("csrftoken") || getCSRFToken();

    const variantSelect = document.getElementById(`variant-${productId}`);

    if (variantSelect && !variantId) {
        showStoreToast("Please choose an option first.", true);
        return;
    }

    fetch(window.location.pathname, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
            product_id: productId,
            variant_id: variantId,
            quantity: quantity,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            showStoreToast(data.message || "Could not add item to cart.", true);
            return;
        }

        showStoreToast(data.message || "Added to cart.");

        if (data.cartCount !== undefined) {
            updateCartCounter(data.cartCount);
        }

        closeQuickView();
    })
    .catch(error => {
        console.error("Add to cart error:", error);
        showStoreToast("Something went wrong adding this item.", true);
    });
}

function openQuickView(productId) {
    const modal = document.getElementById(`quick-view-${productId}`);

    if (!modal) {
        console.error(`Quick view modal not found for product ID: ${productId}`);
        return;
    }

    modal.classList.add("active");
    document.body.style.overflow = "hidden";
}

function closeQuickView() {
    document.querySelectorAll(".quick-view-modal.active").forEach(modal => {
        modal.classList.remove("active");
    });

    document.body.style.overflow = "";
}

function setupStoreSearch() {
    const searchInput = document.getElementById("storeSearch");
    const productCards = document.querySelectorAll(".product-card");

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("input", function () {
        const searchValue = this.value.trim().toLowerCase();

        productCards.forEach(card => {
            const productName = card.dataset.productName || "";
            const shouldShow = productName.includes(searchValue);

            card.style.display = shouldShow ? "" : "none";
        });
    });
}

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeQuickView();
    }
});

document.addEventListener("DOMContentLoaded", function () {
    setupStoreSearch();
});

/*
    Make functions available for inline onclick="" handlers.
    This matters because your template calls these directly.
*/
window.changeProductQty = changeProductQty;
window.addToCart = addToCart;
window.openQuickView = openQuickView;
window.closeQuickView = closeQuickView;