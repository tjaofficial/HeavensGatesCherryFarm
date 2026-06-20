document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("sideBarToggle");
    const sidebar = document.getElementById("treeSpaceSidebar");
    const overlay = document.getElementById("sideBarOverlay");

    function openSidebar() {
        if (!sidebar || !overlay || !toggle) return;

        sidebar.classList.add("is-open");
        overlay.classList.add("is-open");
        document.body.classList.add("sidebar-open");
        toggle.setAttribute("aria-expanded", "true");
    }

    function closeSidebar() {
        if (!sidebar || !overlay || !toggle) return;

        sidebar.classList.remove("is-open");
        overlay.classList.remove("is-open");
        document.body.classList.remove("sidebar-open");
        toggle.setAttribute("aria-expanded", "false");
    }

    if (toggle) {
        toggle.addEventListener("click", function () {
            const isOpen = sidebar.classList.contains("is-open");

            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (overlay) {
        overlay.addEventListener("click", closeSidebar);
    }

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });

    if (window.lucide) {
        lucide.createIcons();
    }
});