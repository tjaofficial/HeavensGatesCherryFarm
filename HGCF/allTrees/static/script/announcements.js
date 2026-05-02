function showAnnouncementToast(message, isError = false) {
    const toast = document.getElementById("announcementToast");

    if (!toast) {
        alert(message);
        return;
    }

    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("show");

    clearTimeout(window.announcementToastTimer);

    window.announcementToastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2600);
}

function setupAnnouncementReveal() {
    const cards = document.querySelectorAll("[data-announcement-card], .announcement-cta, .announcement-body-card, .recent-announcements-panel");

    if (!("IntersectionObserver" in window)) {
        cards.forEach(card => card.classList.add("visible"));
        return;
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    }, {
        threshold: 0.12
    });

    cards.forEach(card => observer.observe(card));
}

function setupAutoSubmitFilters() {
    const form = document.querySelector(".announcement-filter-form");

    if (!form) return;

    const selects = form.querySelectorAll("select");

    selects.forEach(select => {
        select.addEventListener("change", function () {
            form.submit();
        });
    });
}

function setupShareButtons() {
    const buttons = document.querySelectorAll(".share-button");

    buttons.forEach(button => {
        button.addEventListener("click", async function () {
            const title = this.dataset.shareTitle || document.title;
            const url = this.dataset.shareUrl || window.location.href;

            if (navigator.share) {
                try {
                    await navigator.share({
                        title: title,
                        url: url
                    });
                    return;
                } catch (error) {
                    console.log("Share cancelled or failed:", error);
                }
            }

            try {
                await navigator.clipboard.writeText(url);
                showAnnouncementToast("Link copied to clipboard.");
            } catch (error) {
                console.error("Clipboard error:", error);
                showAnnouncementToast("Could not copy link.", true);
            }
        });
    });
}

function setupSearchShortcut() {
    const searchInput = document.getElementById("announcementSearch");

    if (!searchInput) return;

    document.addEventListener("keydown", function (event) {
        const isSlash = event.key === "/";
        const isTyping = ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName);

        if (isSlash && !isTyping) {
            event.preventDefault();
            searchInput.focus();
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    setupAnnouncementReveal();
    setupAutoSubmitFilters();
    setupShareButtons();
    setupSearchShortcut();
});