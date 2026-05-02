function getStoryCSRFToken() {
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

function setupNewsletterForm() {
    const form = document.getElementById("storySubscribeForm");
    const message = document.getElementById("subscribeMessage");

    if (!form) return;

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const submitButton = form.querySelector("button[type='submit']");
        const formData = new FormData(form);

        const payload = {
            name: formData.get("name"),
            email: formData.get("email")
        };

        if (message) {
            message.textContent = "";
            message.classList.remove("error", "success");
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Subscribing...";
        }

        fetch("/our-story/subscribe/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getStoryCSRFToken()
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
                submitButton.textContent = "Subscribe";
            }
        });
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
    setupNewsletterForm();
    setupHeroParallax();
});