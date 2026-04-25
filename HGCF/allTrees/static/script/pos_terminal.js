const state = {
    products: [],
    filteredProducts: [],
    cart: [],
    currentSaleId: null,
    currentSaleNumber: null,
    readers: [],
    cardPollInterval: null,
    pendingResetAfterReceipt: false,
};

const els = {
    productGrid: document.getElementById("productGrid"),
    productSearch: document.getElementById("productSearch"),
    cartItems: document.getElementById("cartItems"),
    subtotalDisplay: document.getElementById("subtotalDisplay"),
    taxDisplay: document.getElementById("taxDisplay"),
    totalDisplay: document.getElementById("totalDisplay"),
    createSaleBtn: document.getElementById("createSaleBtn"),
    cashSaleBtn: document.getElementById("cashSaleBtn"),
    cardSaleBtn: document.getElementById("cardSaleBtn"),
    cancelCardPaymentBtn: document.getElementById("cancelCardPaymentBtn"),
    clearCartBtn: document.getElementById("clearCartBtn"),
    saleStatusBox: document.getElementById("saleStatusBox"),
    customerName: document.getElementById("customerName"),
    customerEmail: document.getElementById("customerEmail"),
    saleNotes: document.getElementById("saleNotes"),
    readerSelect: document.getElementById("readerSelect"),
    refreshReadersBtn: document.getElementById("refreshReadersBtn"),
    receiptModal: document.getElementById("receiptModal"),
    receiptBackdrop: document.getElementById("receiptBackdrop"),
    closeReceiptModalBtn: document.getElementById("closeReceiptModalBtn"),
    receiptDoneBtn: document.getElementById("receiptDoneBtn"),
    receiptSaleNumber: document.getElementById("receiptSaleNumber"),
    receiptPaymentMethod: document.getElementById("receiptPaymentMethod"),
    receiptStatus: document.getElementById("receiptStatus"),
    receiptCustomer: document.getElementById("receiptCustomer"),
    receiptCompletedAt: document.getElementById("receiptCompletedAt"),
    receiptItems: document.getElementById("receiptItems"),
    receiptSubtotal: document.getElementById("receiptSubtotal"),
    receiptTax: document.getElementById("receiptTax"),
    receiptTotal: document.getElementById("receiptTotal"),
    receiptCashReceived: document.getElementById("receiptCashReceived"),
    receiptCashChange: document.getElementById("receiptCashChange"),
    receiptStripeLink: document.getElementById("receiptStripeLink"),
};

function getCSRFToken() {
    const tokenTag = document.querySelector('meta[name="csrf-token"]');
    return tokenTag ? tokenTag.getAttribute("content") : "";
}

function money(value) {
    const num = Number(value || 0);
    return `$${num.toFixed(2)}`;
}

function isReceiptOpen() {
    return !els.receiptModal.classList.contains("hidden");
}

function showStatus(message, type = "success") {
    els.saleStatusBox.classList.remove("hidden", "success", "error");
    els.saleStatusBox.classList.add(type);
    els.saleStatusBox.textContent = message;
}

function clearStatus() {
    els.saleStatusBox.classList.add("hidden");
    els.saleStatusBox.classList.remove("success", "error");
    els.saleStatusBox.textContent = "";
}

function formatPaymentMethod(value) {
    if (!value) return "—";

    const map = {
        cash: "Cash",
        card: "Card",
        tap_to_pay: "Tap to Pay",
        manual_card: "Manual Card",
        other: "Other",
    };

    return map[value] || value;
}

function formatDateTime(value) {
    if (!value) return "—";
    try {
        return new Date(value).toLocaleString();
    } catch (e) {
        return value;
    }
}

function openReceiptModal() {
    els.receiptModal.classList.remove("hidden");
    updateButtons();
}

function closeReceiptModal() {
    els.receiptModal.classList.add("hidden");
    updateButtons();

    if (state.pendingResetAfterReceipt) {
        state.pendingResetAfterReceipt = false;
        resetPOS();
    }
}

function escapeHtml(value) {
    return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function fetchProducts() {
    const response = await fetch(window.POS_CONFIG.productsUrl);
    const data = await response.json();

    if (!data.success) {
        throw new Error(data.message || "Could not load products.");
    }

    state.products = data.products || [];
    state.filteredProducts = [...state.products];
    renderProducts();
}

async function fetchReaders() {
    try {
        const response = await fetch(window.POS_CONFIG.readersUrl);
        const data = await response.json();

        if (!data.success) {
            showStatus(data.message || "Could not load readers.", "error");
            return;
        }

        state.readers = data.readers || [];
        renderReaders();
    } catch (error) {
        showStatus("Error loading readers.", "error");
    }
}

function renderReaders() {
    if (!els.readerSelect) return;

    const options = ['<option value="">Select reader...</option>'];

    state.readers.forEach(reader => {
        const label = reader.label || reader.serial_number || reader.id;
        const status = reader.status ? ` (${reader.status})` : "";
        options.push(`<option value="${reader.id}">${escapeHtml(label)}${escapeHtml(status)}</option>`);
    });

    els.readerSelect.innerHTML = options.join("");
}

function renderProducts() {
    if (!state.filteredProducts.length) {
        els.productGrid.innerHTML = `<div class="emptyState">No POS products found.</div>`;
        return;
    }

    els.productGrid.innerHTML = state.filteredProducts.map(product => `
        <div class="productCard" data-product-id="${product.id}">
            <h3>${escapeHtml(product.product_name)}</h3>
            <p>${escapeHtml(product.description || "No description")}</p>
            <div class="productMeta">
                <span class="priceTag">${money(product.price)}</span>
                <span class="unitBadge">${product.unit_type === "weight" ? "By Weight" : "Each"}</span>
            </div>
        </div>
    `).join("");

    document.querySelectorAll(".productCard").forEach(card => {
        card.addEventListener("click", () => {
            const productId = Number(card.dataset.productId);
            addProductToCart(productId);
        });
    });
}

function addProductToCart(productId) {
    clearStatus();
    const product = state.products.find(p => p.id === productId);
    if (!product) return;

    const existing = state.cart.find(item => item.product_id === productId && product.unit_type !== "weight");

    if (existing && product.unit_type !== "weight") {
        existing.quantity = Number(existing.quantity) + 1;
    } else if (product.unit_type === "weight") {
        state.cart.push({
            product_id: productId,
            quantity: 1,
            weight_amount: 1,
            custom_price: "",
        });
    } else {
        state.cart.push({
            product_id: productId,
            quantity: 1,
            custom_price: "",
        });
    }

    renderCart();
    calculateTotals();
}

function renderCart() {
    if (!state.cart.length) {
        els.cartItems.innerHTML = `<div class="emptyState">No items added yet.</div>`;
        updateButtons();
        return;
    }

    els.cartItems.innerHTML = state.cart.map((item, index) => {
        const product = state.products.find(p => p.id === item.product_id);
        if (!product) return "";

        const isWeight = product.unit_type === "weight";
        const allowCustomPrice = product.allow_custom_price;

        return `
            <div class="cartItem">
                <div class="cartTopRow">
                    <div>
                        <h3 class="cartTitle">${escapeHtml(product.product_name)}</h3>
                        <div>${money(product.price)}</div>
                    </div>
                    <button type="button" class="removeBtn" data-index="${index}">Remove</button>
                </div>

                <div class="cartControls">
                    ${
                        isWeight
                        ? `
                        <div>
                            <label>Weight Amount</label>
                            <input type="number" step="0.01" min="0.01" class="weightInput" data-index="${index}" value="${item.weight_amount ?? 1}">
                        </div>
                        `
                        : `
                        <div>
                            <label>Quantity</label>
                            <input type="number" step="1" min="1" class="qtyInput" data-index="${index}" value="${item.quantity ?? 1}">
                        </div>
                        `
                    }

                    ${
                        allowCustomPrice
                        ? `
                        <div>
                            <label>Custom Price (optional)</label>
                            <input type="number" step="0.01" min="0" class="customPriceInput" data-index="${index}" value="${item.custom_price ?? ""}">
                        </div>
                        `
                        : ""
                    }
                </div>
            </div>
        `;
    }).join("");

    document.querySelectorAll(".removeBtn").forEach(btn => {
        btn.addEventListener("click", () => {
            const index = Number(btn.dataset.index);
            state.cart.splice(index, 1);
            renderCart();
            calculateTotals();
        });
    });

    document.querySelectorAll(".qtyInput").forEach(input => {
        input.addEventListener("input", () => {
            const index = Number(input.dataset.index);
            state.cart[index].quantity = Math.max(1, Number(input.value || 1));
            calculateTotals();
        });
    });

    document.querySelectorAll(".weightInput").forEach(input => {
        input.addEventListener("input", () => {
            const index = Number(input.dataset.index);
            state.cart[index].weight_amount = Math.max(0.01, Number(input.value || 1));
            calculateTotals();
        });
    });

    document.querySelectorAll(".customPriceInput").forEach(input => {
        input.addEventListener("input", () => {
            const index = Number(input.dataset.index);
            state.cart[index].custom_price = input.value;
            calculateTotals();
        });
    });

    updateButtons();
}

function renderReceiptModal(sale) {
    els.receiptSaleNumber.textContent = sale.sale_number || "Receipt";
    els.receiptPaymentMethod.textContent = formatPaymentMethod(sale.payment_method);
    els.receiptStatus.textContent = sale.status || "—";
    els.receiptCustomer.textContent = sale.customer_name || sale.customer_email || "Walk-in Customer";
    els.receiptCompletedAt.textContent = formatDateTime(sale.completed_at || sale.created_at);

    els.receiptSubtotal.textContent = money(sale.subtotal);
    els.receiptTax.textContent = money(sale.tax_amount);
    els.receiptTotal.textContent = money(sale.total);
    els.receiptCashReceived.textContent = sale.cash_received ? money(sale.cash_received) : "—";
    els.receiptCashChange.textContent = sale.cash_change ? money(sale.cash_change) : "—";

    if (sale.stripe_receipt_url) {
        els.receiptStripeLink.href = sale.stripe_receipt_url;
        els.receiptStripeLink.classList.remove("hidden");
    } else {
        els.receiptStripeLink.href = "#";
        els.receiptStripeLink.classList.add("hidden");
    }

    if (!sale.items || !sale.items.length) {
        els.receiptItems.innerHTML = `<div class="emptyState">No receipt items found.</div>`;
    } else {
        els.receiptItems.innerHTML = sale.items.map(item => `
            <div class="receiptItem">
                <div class="receiptItemTop">
                    <div class="receiptItemName">${escapeHtml(item.product_name)}</div>
                    <div><strong>${money(item.line_subtotal)}</strong></div>
                </div>
                <div class="receiptItemMeta">
                    Qty/Weight: ${escapeHtml(item.weight_amount || item.quantity || "1")} • Unit Price: ${money(item.unit_price)}
                </div>
            </div>
        `).join("");
    }

    openReceiptModal();
}

async function showCompletedSaleReceipt(saleId) {
    try {
        const response = await fetch(`${window.POS_CONFIG.saleDetailUrlBase}${saleId}/`);
        const data = await response.json();

        if (!data.success || !data.sale) {
            showStatus("Sale completed, but receipt details could not be loaded.", "error");
            return;
        }

        renderReceiptModal(data.sale);
    } catch (error) {
        showStatus("Sale completed, but receipt failed to load.", "error");
    }
}

async function calculateTotals() {
    if (!state.cart.length) {
        els.subtotalDisplay.textContent = "$0.00";
        els.taxDisplay.textContent = "$0.00";
        els.totalDisplay.textContent = "$0.00";
        updateButtons();
        return;
    }

    try {
        const response = await fetch(window.POS_CONFIG.calculateTotalsUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                items: state.cart,
            }),
        });

        const data = await response.json();

        if (!data.success) {
            showStatus(data.message || "Could not calculate totals.", "error");
            return;
        }

        els.subtotalDisplay.textContent = money(data.subtotal);
        els.taxDisplay.textContent = money(data.tax_amount);
        els.totalDisplay.textContent = money(data.total);
    } catch (error) {
        showStatus("Error calculating totals.", "error");
    }

    updateButtons();
}

function updateButtons() {
    const hasCart = state.cart.length > 0;
    const hasSale = !!state.currentSaleId;
    const hasReader = !!(els.readerSelect && els.readerSelect.value);
    const receiptOpen = isReceiptOpen();

    els.createSaleBtn.disabled = receiptOpen || !hasCart;
    els.cashSaleBtn.disabled = receiptOpen || !hasSale;
    els.cardSaleBtn.disabled = receiptOpen || !(hasSale && hasReader);
    els.cancelCardPaymentBtn.disabled = receiptOpen || !hasSale;
    els.clearCartBtn.disabled = receiptOpen;
}

async function createSale() {
    clearStatus();

    if (!state.cart.length) {
        showStatus("Add at least one item first.", "error");
        return;
    }

    try {
        const response = await fetch(window.POS_CONFIG.createSaleUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                items: state.cart,
                customer_name: els.customerName.value.trim(),
                customer_email: els.customerEmail.value.trim(),
                notes: els.saleNotes.value.trim(),
            }),
        });

        const data = await response.json();

        if (!data.success) {
            showStatus(data.message || "Could not create sale.", "error");
            return;
        }

        state.currentSaleId = data.sale_id;
        state.currentSaleNumber = data.sale_number;
        updateButtons();
        showStatus(`Sale ${data.sale_number} created. Ready for payment.`, "success");
    } catch (error) {
        showStatus("Error creating sale.", "error");
    }
}

async function completeCashSale() {
    clearStatus();

    if (!state.currentSaleId) {
        showStatus("Create the sale first.", "error");
        return;
    }

    const totalText = els.totalDisplay.textContent.replace("$", "");
    const suggestedTotal = Number(totalText || 0).toFixed(2);
    const cashReceived = window.prompt(`Cash received? Total is $${suggestedTotal}`, suggestedTotal);

    if (cashReceived === null) return;

    try {
        const response = await fetch(`${window.POS_CONFIG.cashCompleteUrlBase}${state.currentSaleId}/complete-cash/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                cash_received: cashReceived,
            }),
        });

        const data = await response.json();

        if (!data.success) {
            showStatus(data.message || "Could not complete cash sale.", "error");
            return;
        }

        showStatus(`Cash sale complete. Change due: ${money(data.cash_change)}`, "success");
        state.pendingResetAfterReceipt = true;
        await showCompletedSaleReceipt(state.currentSaleId);
    } catch (error) {
        showStatus("Error completing cash sale.", "error");
    }
}

async function startCardPayment() {
    clearStatus();

    if (!state.currentSaleId) {
        showStatus("Create the sale first.", "error");
        return;
    }

    const readerId = els.readerSelect ? els.readerSelect.value : "";
    if (!readerId) {
        showStatus("Select a reader first.", "error");
        return;
    }

    try {
        const response = await fetch(`${window.POS_CONFIG.saleDetailUrlBase}${state.currentSaleId}/start-card-payment/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
                reader_id: readerId,
            }),
        });

        const data = await response.json();

        if (!data.success) {
            showStatus(data.message || "Could not start card payment.", "error");
            return;
        }

        showStatus("Card payment sent to reader. Waiting for customer...", "success");
        pollCardPaymentStatus();
    } catch (error) {
        showStatus("Error starting card payment.", "error");
    }
}

function pollCardPaymentStatus() {
    if (state.cardPollInterval) {
        clearInterval(state.cardPollInterval);
    }

    state.cardPollInterval = setInterval(async () => {
        if (!state.currentSaleId) return;

        try {
            const response = await fetch(`${window.POS_CONFIG.saleDetailUrlBase}${state.currentSaleId}/card-payment-status/`);
            const data = await response.json();

            if (!data.success) return;

            if (data.payment_status === "completed") {
                const completedSaleId = state.currentSaleId;

                clearInterval(state.cardPollInterval);
                state.cardPollInterval = null;
                state.pendingResetAfterReceipt = true;
                showStatus("Card payment completed successfully.", "success");
                await showCompletedSaleReceipt(completedSaleId);
            } else if (data.payment_status === "failed" || data.payment_status === "canceled") {
                clearInterval(state.cardPollInterval);
                state.cardPollInterval = null;
                showStatus(`Card payment ${data.payment_status}.`, "error");
            }
        } catch (error) {
            console.error(error);
        }
    }, 2500);
}

async function cancelCardPayment() {
    clearStatus();

    if (!state.currentSaleId) {
        showStatus("No active sale to cancel payment for.", "error");
        return;
    }

    try {
        const response = await fetch(`${window.POS_CONFIG.saleDetailUrlBase}${state.currentSaleId}/cancel-card-payment/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
        });

        const data = await response.json();

        if (!data.success) {
            showStatus(data.message || "Could not cancel card payment.", "error");
            return;
        }

        if (state.cardPollInterval) {
            clearInterval(state.cardPollInterval);
            state.cardPollInterval = null;
        }

        showStatus("Card payment canceled.", "success");
    } catch (error) {
        showStatus("Error canceling card payment.", "error");
    }
}

function resetPOS() {
    state.cart = [];
    state.currentSaleId = null;
    state.currentSaleNumber = null;
    state.pendingResetAfterReceipt = false;

    if (state.cardPollInterval) {
        clearInterval(state.cardPollInterval);
        state.cardPollInterval = null;
    }

    els.customerName.value = "";
    els.customerEmail.value = "";
    els.saleNotes.value = "";

    renderCart();
    calculateTotals();
}

function filterProducts() {
    const term = els.productSearch.value.trim().toLowerCase();

    if (!term) {
        state.filteredProducts = [...state.products];
    } else {
        state.filteredProducts = state.products.filter(product => {
            return (
                (product.product_name || "").toLowerCase().includes(term) ||
                (product.description || "").toLowerCase().includes(term) ||
                (product.sku || "").toLowerCase().includes(term)
            );
        });
    }

    renderProducts();
}

function bindEvents() {
    els.productSearch.addEventListener("input", filterProducts);

    els.clearCartBtn.addEventListener("click", () => {
        state.cart = [];
        state.currentSaleId = null;
        state.currentSaleNumber = null;
        clearStatus();
        renderCart();
        calculateTotals();
    });

    if (els.readerSelect) {
        els.readerSelect.addEventListener("change", updateButtons);
    }

    if (els.refreshReadersBtn) {
        els.refreshReadersBtn.addEventListener("click", fetchReaders);
    }

    els.createSaleBtn.addEventListener("click", createSale);
    els.cashSaleBtn.addEventListener("click", completeCashSale);
    els.cardSaleBtn.addEventListener("click", startCardPayment);
    els.cancelCardPaymentBtn.addEventListener("click", cancelCardPayment);

    if (els.closeReceiptModalBtn) {
        els.closeReceiptModalBtn.addEventListener("click", closeReceiptModal);
    }

    if (els.receiptDoneBtn) {
        els.receiptDoneBtn.addEventListener("click", closeReceiptModal);
    }

    if (els.receiptBackdrop) {
        els.receiptBackdrop.addEventListener("click", closeReceiptModal);
    }
}

async function initPOS() {
    bindEvents();
    renderCart();
    await fetchProducts();
    await fetchReaders();
    await calculateTotals();
}

initPOS();