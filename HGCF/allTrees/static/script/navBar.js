document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.getElementById("menu");
    const mainNav = document.getElementById("mainNav");

    if (!menuButton || !mainNav) return;

    menuButton.addEventListener("click", function () {
        const isOpen = mainNav.classList.toggle("is-open");

        menuButton.classList.toggle("is-open", isOpen);
        menuButton.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    const navLinks = mainNav.querySelectorAll("a");

    navLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            mainNav.classList.remove("is-open");
            menuButton.classList.remove("is-open");
            menuButton.setAttribute("aria-expanded", "false");
        });
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 1037) {
            mainNav.classList.remove("is-open");
            menuButton.classList.remove("is-open");
            menuButton.setAttribute("aria-expanded", "false");
        }
    });
});