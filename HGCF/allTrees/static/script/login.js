function setupPasswordToggle() {
    const passwordInput = document.getElementById("password");
    const toggleButton = document.getElementById("passwordToggle");

    if (!passwordInput || !toggleButton) return;

    toggleButton.addEventListener("click", function () {
        const isPassword = passwordInput.type === "password";

        passwordInput.type = isPassword ? "text" : "password";
        toggleButton.textContent = isPassword ? "Hide" : "Show";
        toggleButton.setAttribute("aria-label", isPassword ? "Hide password" : "Show password");
    });
}

function setupLoginLoadingState() {
    const form = document.getElementById("signup");
    const submitButton = document.getElementById("submit");

    if (!form || !submitButton) return;

    form.addEventListener("submit", function () {
        submitButton.disabled = true;
        submitButton.innerHTML = "<span>Entering TreeSpace...</span><strong>⏳</strong>";
    });
}

function setupLoginEntrance() {
    const shell = document.querySelector(".treespace-login-shell");

    if (!shell) return;

    shell.style.opacity = "0";
    shell.style.transform = "translateY(22px) scale(0.985)";

    requestAnimationFrame(() => {
        shell.style.transition = "opacity 0.65s ease, transform 0.65s ease";
        shell.style.opacity = "1";
        shell.style.transform = "translateY(0) scale(1)";
    });
}

document.addEventListener("DOMContentLoaded", function () {
    setupPasswordToggle();
    setupLoginLoadingState();
    setupLoginEntrance();
});