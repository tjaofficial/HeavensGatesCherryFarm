function getStoryCSRFToken(form = null) {
    if (form) {
        const csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");

        if (csrfInput) {
            return csrfInput.value;
        }
    }

    const csrfInput = document.querySelector("input[name='csrfmiddlewaretoken']");

    if (csrfInput) {
        return csrfInput.value;
    }

    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookieValue ? decodeURIComponent(cookieValue.split("=")[1]) : "";
}

function setupStoryTimelineReveal() {
    const items = document.querySelectorAll(".timeline-item, .value-card, .story-message, .visit-section, .newsletter-card");

    if (!("IntersectionObserver" in window)) {
        items.forEach(item => item.classList.add("visible"));
        return;
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    }, {
        threshold: 0.15
    });

    items.forEach(item => observer.observe(item));
}

function setupStoryPhotoModal() {
    const modal = document.getElementById("storyPhotoModal");
    const preview = document.getElementById("storyPhotoPreview");
    const closeBtn = document.getElementById("storyPhotoClose");
    const photoButtons = document.querySelectorAll("[data-story-photo]");

    if (!modal || !preview) return;

    photoButtons.forEach(button => {
        button.addEventListener("click", function () {
            const imageUrl = this.dataset.storyPhoto;

            if (!imageUrl) return;

            preview.src = imageUrl;
            modal.classList.add("active");
            document.body.style.overflow = "hidden";
        });
    });

    function closeModal() {
        modal.classList.remove("active");
        document.body.style.overflow = "";
        preview.src = "";
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", closeModal);
    }

    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeModal();
        }
    });
}

function setupNewsletterFormById(options) {
    const form = document.getElementById(options.formId);
    const message = document.getElementById(options.messageId);

    if (!form) return;

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const submitButton = form.querySelector("button[type='submit']");
        const formData = new FormData(form);

        const firstName = (formData.get("first_name") || "").trim();
        const lastName = (formData.get("last_name") || "").trim();
        const email = (formData.get("email") || "").trim();
        const source = (formData.get("source") || options.defaultSource || "farm_subscribe").trim();

        const payload = {
            first_name: firstName,
            last_name: lastName,
            email: email,
            source: source
        };

        if (message) {
            message.textContent = "";
            message.classList.remove("error", "success");
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.dataset.originalText = submitButton.textContent;
            submitButton.textContent = "Subscribing...";
        }

        const subscribeUrl = window.FARM_SUBSCRIBE_URL || "/our-story/subscribe/";

        fetch(subscribeUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getStoryCSRFToken(form)
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json().then(data => ({
            ok: response.ok,
            data: data
        })))
        .then(result => {
            if (message) {
                message.textContent = result.data.message || "Thanks for subscribing.";
                message.classList.add(result.ok && result.data.success ? "success" : "error");
            }

            if (result.ok && result.data.success) {
                form.reset();
            }
        })
        .catch(error => {
            console.error("Subscribe error:", error);

            if (message) {
                message.textContent = "Something went wrong. Please try again.";
                message.classList.add("error");
            }
        })
        .finally(() => {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = submitButton.dataset.originalText || options.defaultButtonText || "Subscribe";
            }
        });
    });
}

function setupNewsletterForms() {
    setupNewsletterFormById({
        formId: "storySubscribeForm",
        messageId: "subscribeMessage",
        defaultSource: "our_story_page",
        defaultButtonText: "Subscribe"
    });

    setupNewsletterFormById({
        formId: "farmSubscribeForm",
        messageId: "farmSubscribeMessage",
        defaultSource: "farm_subscription_page",
        defaultButtonText: "Subscribe to Farm Updates"
    });
}

function setupHeroParallax() {
    const hero = document.querySelector(".story-hero");

    if (!hero) return;

    window.addEventListener("scroll", function () {
        const offset = window.scrollY * 0.18;
        hero.style.backgroundPosition = `center ${offset}px`;
    });
}

document.addEventListener("DOMContentLoaded", function () {
    setupStoryTimelineReveal();
    setupStoryPhotoModal();
    setupNewsletterForms();
    setupHeroParallax();
});