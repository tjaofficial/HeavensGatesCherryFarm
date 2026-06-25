const state = {
    products: [],
    filteredProducts: [],
    reservations: [],
    cart: [],
    currentSaleId: null,
    currentSaleNumber: null,
    selectedReservationId: null,
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
    openStripeManualChargeBtn: document.getElementById("openStripeManualChargeBtn"),
    manualCardSaleBtn: document.getElementById("manualCardSaleBtn"),
    cardSaleBtn: document.getElementById("cardSaleBtn"),
    cancelCardPaymentBtn: document.getElementById("cancelCardPaymentBtn"),
    clearCartBtn: document.getElementById("clearCartBtn"),
    saleStatusBox: document.getElementById("saleStatusBox"),

    reservationCustomerSelect: document.getElementById("reservationCustomerSelect"),
    customerName: document.getElementById("customerName"),
    customerEmail: document.getElementById("customerEmail"),
    customerPhone: document.getElementById("customerPhone"),
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

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];

    for (let cookie of cookies) {
        cookie = cookie.trim();

        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }

    return "";
}

function getCSRFToken() {
    const tokenTag = document.querySelector('meta[name="csrf-token"]');

    if (tokenTag && tokenTag.getAttribute("content")) {
        return tokenTag.getAttribute("content");
    }

    return getCookie("csrftoken");
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

function setVisible(element, shouldShow) {
    if (!element) return;
    element.classList.toggle("hidden", !shouldShow);
}

function setDisabled(element, shouldDisable) {
    if (!element) return;
    element.disabled = shouldDisable;
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

function openStripeManualCharge() {
    if (!state.currentSaleId) {
        showStatus("Start checkout before opening Stripe card charge.", "error");
        return;
    }

    const totalText = els.totalDisplay ? els.totalDisplay.textContent : "$0.00";
    const saleNumber = state.currentSaleNumber || "Current POS Sale";

    const copyText = `${saleNumber} - Total: ${totalText}`;

    if (navigator.clipboard) {
        navigator.clipboard.writeText(copyText).catch(() => {});
    }

    showStatus(
        `Stripe opened. Charge ${totalText}, then return and click Mark Card Paid.`,
        "info"
    );

    window.open(
        window.POS_CONFIG.stripeDashboardUrl || "https://dashboard.stripe.com/payments",
        "_blank",
        "noopener,noreferrer"
    );
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

async function fetchTodayReservations() {
    if (!window.POS_CONFIG.todayReservationsUrl) return;

    try {
        const response = await fetch(window.POS_CONFIG.todayReservationsUrl);
        const data = await response.json();

        if (!data.success) {
            showStatus(data.message || "Could not load today's reservations.", "error");
            return;
        }

        state.reservations = data.reservations || [];
        renderReservationOptions();
    } catch (error) {
        showStatus("Error loading today's reservations.", "error");
    }
}

function renderReservationOptions() {
    if (!els.reservationCustomerSelect) return;

    const options = [
        `<option value="">Walk-in / Type Manually</option>`
    ];

    state.reservations.forEach(reservation => {
        const label = `${reservation.slot_label} — ${reservation.full_name} — Party of ${reservation.party_size}`;
        const status = reservation.status ? ` (${reservation.status})` : "";

        options.push(`
            <option value="${reservation.id}">
                ${escapeHtml(label + status)}
            </option>
        `);
    });

    els.reservationCustomerSelect.innerHTML = options.join("");
}

function handleReservationCustomerChange() {
    if (!els.reservationCustomerSelect) return;

    const reservationId = els.reservationCustomerSelect.value;

    if (!reservationId) {
        state.selectedReservationId = null;

        if (els.customerPhone) {
            els.customerPhone.value = "";
        }

        return;
    }

    const reservation = state.reservations.find(item => String(item.id) === String(reservationId));

    if (!reservation) {
        state.selectedReservationId = null;
        return;
    }

    state.selectedReservationId = reservation.id;
    els.customerName.value = reservation.full_name || "";
    els.customerEmail.value = reservation.email || "";

    if (els.customerPhone) {
        els.customerPhone.value = reservation.phone || "";
    }

    showStatus(`Reservation selected: ${reservation.full_name}`, "success");
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

function isWeightProduct(product) {
    return ["weight", "lb", "oz"].includes(product.unit_type);
}

function safeNumber(value) {
    const num = Number(value);

    if (Number.isNaN(num)) {
        return 0;
    }

    return num;
}

function lbsOzToLbs(lbs, oz) {
    const pounds = safeNumber(lbs);
    const ounces = safeNumber(oz);

    return pounds + (ounces / 16);
}

function roundWeight(value) {
    return Math.round(value * 100) / 100;
}

function ensureWeightRows(item) {
    if (!item.weight_rows || !Array.isArray(item.weight_rows) || !item.weight_rows.length) {
        item.weight_rows = [
            {
                gross_lbs: "",
                gross_oz: "",
                container_lbs: "",
                container_oz: "",
            }
        ];
    }

    return item.weight_rows;
}

function calculateWeightRowsTotal(item) {
    const rows = ensureWeightRows(item);

    let total = 0;

    rows.forEach(row => {
        const grossWeight = lbsOzToLbs(row.gross_lbs, row.gross_oz);
        const containerWeight = lbsOzToLbs(row.container_lbs, row.container_oz);
        const netWeight = Math.max(0, grossWeight - containerWeight);

        total += netWeight;
    });

    return roundWeight(total);
}

function updateWeightFromRows(index) {
    const item = state.cart[index];
    if (!item) return;

    const totalWeight = calculateWeightRowsTotal(item);

    item.weight_amount = totalWeight;
    item.quantity = totalWeight;

    const finalInput = document.querySelector(`.weightInput[data-index="${index}"]`);

    if (finalInput) {
        finalInput.value = totalWeight || "";
    }

    calculateTotals();
}

function getUnitLabel(product) {
    const labels = {
        each: "Each",
        lb: "Per lb",
        oz: "Per oz",
        quart: "Per quart",
        pint: "Per pint",
        half_pint: "Per half pint",
        bushel: "Per bushel",
        bunch: "Per bunch",
        bag: "Per bag",
        box: "Per box",
        jar: "Per jar",
        bundle: "Per bundle",
        custom: "Custom",
    };

    return labels[product.unit_type] || product.unit_type || "Each";
}

function renderProducts() {
    if (!state.filteredProducts.length) {
        els.productGrid.innerHTML = `<div class="emptyState">No POS products found.</div>`;
        return;
    }

    els.productGrid.innerHTML = state.filteredProducts.map(product => {
        const imageHtml = product.mainImage
            ? `<img class="productImage" src="${escapeHtml(product.mainImage)}" alt="${escapeHtml(product.product_name)}">`
            : `<div class="productImagePlaceholder">🍓</div>`;

        const saleHtml = product.on_sale
            ? `<span class="saleBadge">Sale</span>`
            : "";

        const stockHtml = product.inventory_status
            ? `<span class="stockBadge ${escapeHtml(product.inventory_status)}">${escapeHtml(product.inventory_status.replaceAll("_", " "))}</span>`
            : "";

        return `
            <button type="button" class="productCard" data-product-id="${product.id}">
                <div class="productImageWrap">
                    ${imageHtml}
                    ${saleHtml}
                </div>

                <div class="productCardBody">
                    <h3>${escapeHtml(product.product_name)}</h3>

                    <p>${escapeHtml(product.description || "Farm product")}</p>

                    <div class="productMeta">
                        <span class="priceTag">${money(product.price)}</span>
                        <span class="unitBadge">${escapeHtml(getUnitLabel(product))}</span>
                    </div>

                    <div class="productBottomMeta">
                        ${product.sku ? `<small>SKU: ${escapeHtml(product.sku)}</small>` : `<small>No SKU</small>`}
                        ${stockHtml}
                    </div>
                </div>
            </button>
        `;
    }).join("");

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

    const isWeight = isWeightProduct(product);

    const existing = state.cart.find(item => {
        return item.product_id === productId && !isWeight;
    });

    if (existing && !isWeight) {
        existing.quantity = Number(existing.quantity) + 1;
    } else if (isWeight) {
        state.cart.push({
            product_id: productId,
            quantity: 1,
            weight_amount: 1,
            custom_price: "",
            weight_rows: [
                {
                    gross_lbs: "",
                    gross_oz: "",
                    container_lbs: "",
                    container_oz: "",
                }
            ],
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

        const isWeight = isWeightProduct(product);
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
                        <div class="weightCalculatorBox">
                            <label>Weight Calculator</label>

                            ${ensureWeightRows(item).map((row, rowIndex) => `
                                <div class="weightRow">
                                    <div class="weightRowHeader">
                                        <strong>Container ${rowIndex + 1}</strong>

                                        ${
                                            ensureWeightRows(item).length > 1
                                            ? `<button type="button" class="removeWeightRowBtn" data-index="${index}" data-row-index="${rowIndex}">Remove</button>`
                                            : ""
                                        }
                                    </div>

                                    <div class="weightGrid">
                                        <div>
                                            <label>Strawberries + Container</label>
                                            <div class="lbsOzRow">
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    min="0"
                                                    class="weightCalcInput"
                                                    data-index="${index}"
                                                    data-row-index="${rowIndex}"
                                                    data-field="gross_lbs"
                                                    value="${row.gross_lbs ?? ""}"
                                                    placeholder="0"
                                                >
                                                <span>lbs</span>

                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    min="0"
                                                    class="weightCalcInput"
                                                    data-index="${index}"
                                                    data-row-index="${rowIndex}"
                                                    data-field="gross_oz"
                                                    value="${row.gross_oz ?? ""}"
                                                    placeholder="0"
                                                >
                                                <span>oz</span>
                                            </div>
                                        </div>

                                        <div>
                                            <label>Container Weight</label>
                                            <div class="lbsOzRow">
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    min="0"
                                                    class="weightCalcInput"
                                                    data-index="${index}"
                                                    data-row-index="${rowIndex}"
                                                    data-field="container_lbs"
                                                    value="${row.container_lbs ?? ""}"
                                                    placeholder="0"
                                                >
                                                <span>lbs</span>

                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    min="0"
                                                    class="weightCalcInput"
                                                    data-index="${index}"
                                                    data-row-index="${rowIndex}"
                                                    data-field="container_oz"
                                                    value="${row.container_oz ?? ""}"
                                                    placeholder="0"
                                                >
                                                <span>oz</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join("")}

                            <button type="button" class="addWeightRowBtn" data-index="${index}">
                                + Add Another Container
                            </button>

                            <div class="manualWeightBox">
                                <label>Final Sale Weight / Quantity</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0.01"
                                    class="weightInput"
                                    data-index="${index}"
                                    value="${item.weight_amount ?? item.quantity ?? 1}"
                                >
                                <small>
                                    This fills automatically from the calculator, but you can also type the final weight manually.
                                </small>
                            </div>
                        </div>
                        `
                        : `
                        <div>
                            <label>Quantity</label>
                            <input
                                type="number"
                                step="1"
                                min="1"
                                class="qtyInput"
                                data-index="${index}"
                                value="${item.quantity ?? 1}"
                            >
                        </div>
                        `
                    }

                    ${
                        allowCustomPrice
                        ? `
                        <div>
                            <label>Custom Price (optional)</label>
                            <input
                                type="number"
                                step="0.01"
                                min="0"
                                class="customPriceInput"
                                data-index="${index}"
                                value="${item.custom_price ?? ""}"
                            >
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

    document.querySelectorAll(".weightCalcInput").forEach(input => {
        input.addEventListener("input", () => {
            const index = Number(input.dataset.index);
            const rowIndex = Number(input.dataset.rowIndex);
            const field = input.dataset.field;

            const item = state.cart[index];
            if (!item) return;

            const rows = ensureWeightRows(item);

            if (!rows[rowIndex]) return;

            rows[rowIndex][field] = input.value;

            updateWeightFromRows(index);
        });
    });

    document.querySelectorAll(".addWeightRowBtn").forEach(btn => {
        btn.addEventListener("click", () => {
            const index = Number(btn.dataset.index);

            const item = state.cart[index];
            if (!item) return;

            const rows = ensureWeightRows(item);

            rows.push({
                gross_lbs: "",
                gross_oz: "",
                container_lbs: "",
                container_oz: "",
            });

            renderCart();
            calculateTotals();
        });
    });

    document.querySelectorAll(".removeWeightRowBtn").forEach(btn => {
        btn.addEventListener("click", () => {
            const index = Number(btn.dataset.index);
            const rowIndex = Number(btn.dataset.rowIndex);

            const item = state.cart[index];
            if (!item) return;

            const rows = ensureWeightRows(item);

            if (rows.length > 1) {
                rows.splice(rowIndex, 1);
            }

            renderCart();
            updateWeightFromRows(index);
        });
    });

    document.querySelectorAll(".weightInput").forEach(input => {
        input.addEventListener("input", () => {
            const index = Number(input.dataset.index);
            const weight = Math.max(0.01, Number(input.value || 1));

            state.cart[index].weight_amount = weight;
            state.cart[index].quantity = weight;

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
    const receiptOpen = isReceiptOpen();

    /*
        Step 1:
        No sale created yet. Show only Start Checkout.
    */
    setVisible(els.createSaleBtn, !hasSale);
    setDisabled(els.createSaleBtn, receiptOpen || !hasCart);

    /*
        Step 2:
        Sale has been created. Show payment options.
    */
    setVisible(els.cashSaleBtn, hasSale);
    setVisible(els.openStripeManualChargeBtn, hasSale);
    setVisible(els.manualCardSaleBtn, hasSale);

    /*
        Hide actual reader buttons for now until the M2 mobile bridge is built.
    */
    setVisible(els.cardSaleBtn, false);
    setVisible(els.cancelCardPaymentBtn, false);

    setDisabled(els.cashSaleBtn, receiptOpen || !hasSale);
    setDisabled(els.openStripeManualChargeBtn, receiptOpen || !hasSale);
    setDisabled(els.manualCardSaleBtn, receiptOpen || !hasSale);

    setDisabled(els.cardSaleBtn, true);
    setDisabled(els.cancelCardPaymentBtn, true);

    /*
        Once a sale exists, do not let them clear/change the ticket casually.
    */
    setDisabled(els.clearCartBtn, receiptOpen || hasSale);
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
                upick_reservation_id: state.selectedReservationId,
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

        const customerText = data.customer_name ? ` for ${data.customer_name}` : "";
        showStatus(`Ticket ${data.sale_number} started. Choose cash or card payment.`, "success");
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
async function completeManualCardSale() {
    if (!state.currentSaleId) {
        showStatus("Start checkout before marking a card sale paid.", "error");
        return;
    }

    const confirmPaid = window.confirm(
        "Only click OK after the card was successfully charged in Stripe. Do not enter card numbers into this POS."
    );

    if (!confirmPaid) return;

    const stripeReference = window.prompt(
        "Optional: enter Stripe payment/charge reference. Do NOT enter the card number."
    ) || "";

    try {
        showStatus("Marking card sale as paid...", "info");

        const completedSaleId = state.currentSaleId;

        const response = await fetch(
            `${window.POS_CONFIG.manualCardCompleteUrlBase}${completedSaleId}/manual-card-complete/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    stripe_reference: stripeReference
                })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            showStatus(data.message || "Could not mark card sale paid.", "error");
            return;
        }

        showStatus(`Card sale ${data.sale_number} marked paid.`, "success");

        state.pendingResetAfterReceipt = true;
        await showCompletedSaleReceipt(completedSaleId);

    } catch (error) {
        console.error("Manual card sale error:", error);
        showStatus("Error marking card sale paid.", "error");
    }
}
function resetPOS() {
    state.cart = [];
    state.currentSaleId = null;
    state.currentSaleNumber = null;
    state.selectedReservationId = null;
    state.pendingResetAfterReceipt = false;

    if (state.cardPollInterval) {
        clearInterval(state.cardPollInterval);
        state.cardPollInterval = null;
    }

    if (els.reservationCustomerSelect) {
        els.reservationCustomerSelect.value = "";
    }

    els.customerName.value = "";
    els.customerEmail.value = "";

    if (els.customerPhone) {
        els.customerPhone.value = "";
    }

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

    if (els.reservationCustomerSelect) {
        els.reservationCustomerSelect.addEventListener("change", handleReservationCustomerChange);
    }

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

    if (els.openStripeManualChargeBtn) {
        els.openStripeManualChargeBtn.addEventListener("click", openStripeManualCharge);
    }

    if (els.manualCardSaleBtn) {
        els.manualCardSaleBtn.addEventListener("click", completeManualCardSale);
    }
}

async function initPOS() {
    bindEvents();
    renderCart();

    await fetchTodayReservations();
    await fetchProducts();

    if (
        window.POS_CONFIG.readersUrl &&
        els.readerSelect &&
        !els.readerSelect.classList.contains("hidden")
    ) {
        await fetchReaders();
    }

    await calculateTotals();
}

initPOS();