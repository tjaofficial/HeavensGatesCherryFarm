function getField(selector) {
    return document.querySelector(selector);
}

function getAllFields(selector) {
    return Array.from(document.querySelectorAll(selector));
}

function setHidden(elements, shouldHide) {
    elements.forEach((element) => {
        if (!element) return;
        element.classList.toggle("is-hidden", shouldHide);
    });
}

function setupImagePreview() {
    const imageInput = getField("input[type='file'][name='mainImage']");
    const previewBox = getField("#imagePreviewBox");
    const previewImage = getField("#imagePreview");

    if (!imageInput || !previewBox || !previewImage) return;

    imageInput.addEventListener("change", function () {
        const file = this.files && this.files[0];

        if (!file) {
            previewBox.classList.remove("has-image");
            previewImage.src = "";
            return;
        }

        const reader = new FileReader();

        reader.onload = function (event) {
            previewImage.src = event.target.result;
            previewBox.classList.add("has-image");
        };

        reader.readAsDataURL(file);
    });
}

function setupConditionalSections() {
    const onSale = getField("input[name='on_sale']");
    const trackInventory = getField("input[name='track_inventory']");
    const preorder = getField("input[name='pre_order']");
    const seasonal = getField("input[name='is_seasonal']");
    const limitPerOrder = getField("input[name='limit_per_order']");

    const saleFields = getAllFields(".sale-field");
    const inventoryFields = getAllFields(".inventory-field");
    const preorderFields = getAllFields(".preorder-field");
    const seasonalFields = getAllFields(".seasonal-field");
    const limitFields = getAllFields(".limit-field");

    function refresh() {
        setHidden(saleFields, onSale && !onSale.checked);
        setHidden(inventoryFields, trackInventory && !trackInventory.checked);
        setHidden(preorderFields, preorder && !preorder.checked);
        setHidden(seasonalFields, seasonal && !seasonal.checked);
        setHidden(limitFields, limitPerOrder && !limitPerOrder.checked);
    }

    [onSale, trackInventory, preorder, seasonal, limitPerOrder].forEach((field) => {
        if (!field) return;
        field.addEventListener("change", refresh);
    });

    refresh();
}

function setupVariantBuilder() {
    const addVariantBtn = getField("#addVariantBtn");
    const variantList = getField("#variantList");
    const emptyTemplate = getField("#emptyVariantTemplate");
    const totalFormsInput = getField("input[name='variants-TOTAL_FORMS']");

    if (!addVariantBtn || !variantList || !emptyTemplate || !totalFormsInput) return;

    addVariantBtn.addEventListener("click", function () {
        const formIndex = parseInt(totalFormsInput.value, 10);
        let templateHtml = emptyTemplate.innerHTML;

        const regex = new RegExp("__prefix__", "g");
        templateHtml = templateHtml.replace(regex, formIndex);

        const tempWrapper = document.createElement("div");
        tempWrapper.innerHTML = templateHtml.trim();

        const newVariantCard = tempWrapper.firstElementChild;

        variantList.appendChild(newVariantCard);

        totalFormsInput.value = formIndex + 1;

        setupNewVariantRemoveButtons();
    });

    setupNewVariantRemoveButtons();
}

function setupNewVariantRemoveButtons() {
    const removeButtons = getAllFields(".remove-new-variant");

    removeButtons.forEach((button) => {
        if (button.dataset.bound === "true") return;

        button.dataset.bound = "true";

        button.addEventListener("click", function () {
            const card = this.closest(".variant-card");
            if (!card) return;

            card.remove();
            rebuildVariantIndexes();
        });
    });
}

function rebuildVariantIndexes() {
    const cards = getAllFields("#variantList .variant-card");
    const totalFormsInput = getField("input[name='variants-TOTAL_FORMS']");

    if (!totalFormsInput) return;

    cards.forEach((card, index) => {
        const fields = card.querySelectorAll("input, select, textarea, label");

        fields.forEach((field) => {
            ["name", "id", "for"].forEach((attr) => {
                const value = field.getAttribute(attr);
                if (!value) return;

                const updated = value.replace(/variants-\d+-/g, `variants-${index}-`);
                field.setAttribute(attr, updated);
            });
        });
    });

    totalFormsInput.value = cards.length;
}

function setupAutoSaleCalculation() {
    const priceInput = getField("input[name='price']");
    const discountInput = getField("input[name='sale_percentage']");
    const salePriceInput = getField("input[name='sale_price']");

    if (!priceInput || !discountInput || !salePriceInput) return;

    function calculateSalePrice() {
        const price = parseFloat(priceInput.value);
        const discount = parseFloat(discountInput.value);

        if (isNaN(price) || isNaN(discount)) return;
        if (discount <= 0 || discount > 100) return;

        const salePrice = price - (price * (discount / 100));
        salePriceInput.value = salePrice.toFixed(2);
    }

    discountInput.addEventListener("input", calculateSalePrice);
}

document.addEventListener("DOMContentLoaded", function () {
    setupImagePreview();
    setupConditionalSections();
    setupVariantBuilder();
    setupAutoSaleCalculation();
});