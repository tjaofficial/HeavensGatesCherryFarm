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

async function addToCart(productId) {
    const variantSelect = document.getElementById(`variant-${productId}`);
    let variantId = null;

    if (variantSelect) {
        variantId = variantSelect.value;

        if (!variantId) {
            showStoreToast("Please select a size or option first.", true);
            return;
        }
    }

    try {
        const response = await fetch(window.location.pathname, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                product_id: productId,
                variant_id: variantId
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showStoreToast(data.message || "Could not add item to cart.", true);
            return;
        }

        showStoreToast(data.message || "Item added to cart.");
        updateCartCounter(data.cartCount);
    } catch (error) {
        console.error("Add to cart error:", error);
        showStoreToast("Something went wrong adding this item.", true);
    }
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

function setupStoreSearch() {
    const searchInput = document.getElementById("storeSearch");
    const productCards = document.querySelectorAll(".product-card");

    if (!searchInput) return;

    searchInput.addEventListener("input", function () {
        const searchValue = this.value.trim().toLowerCase();

        productCards.forEach(card => {
            const productName = card.dataset.productName || "";
            const shouldShow = productName.includes(searchValue);

            card.style.display = shouldShow ? "" : "none";
        });
    });
}

function updateCartCounter(count) {
    const cartCounter = document.getElementById("cartCounter");

    if (!cartCounter) return;

    cartCounter.textContent = count;
}

document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
        closeQuickView();
    }
});

document.addEventListener("DOMContentLoaded", function () {
    setupStoreSearch();
});