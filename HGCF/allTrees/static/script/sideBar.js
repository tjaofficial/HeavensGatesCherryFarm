document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("treeSpaceSidebar");
    const toggleButton = document.getElementById("sideBarToggle");
    const overlay = document.getElementById("sideBarOverlay");

    if (!sidebar || !toggleButton || !overlay) return;

    function openSidebar() {
        sidebar.classList.add("is-open");
        overlay.classList.add("is-open");
        document.body.classList.add("sidebar-open");
        toggleButton.setAttribute("aria-expanded", "true");
    }

    function closeSidebar() {
        sidebar.classList.remove("is-open");
        overlay.classList.remove("is-open");
        document.body.classList.remove("sidebar-open");
        toggleButton.setAttribute("aria-expanded", "false");
    }

    toggleButton.addEventListener("click", function () {
        if (sidebar.classList.contains("is-open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay.addEventListener("click", closeSidebar);

    sidebar.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", closeSidebar);
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 900) {
            closeSidebar();
        }
    });
});