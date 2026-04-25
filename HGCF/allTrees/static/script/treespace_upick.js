function getCSRFToken() {
    const csrfInput = document.querySelector("input[name='csrfmiddlewaretoken']");

    if (csrfInput) {
        return csrfInput.value;
    }

    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));

    return cookieValue ? cookieValue.split("=")[1] : "";
}

async function updateReservationStatus(reservationId, action) {
    const actionLabels = {
        check_in: "check in this guest",
        complete: "mark this reservation completed",
        no_show: "mark this guest as no-show",
        cancel: "cancel this reservation",
        release: "release this reservation to walk-ins",
        confirm: "reconfirm this reservation",
    };

    const label = actionLabels[action] || "update this reservation";

    const confirmed = confirm(`Are you sure you want to ${label}?`);

    if (!confirmed) return;

    try {
        const response = await fetch("/treespace/upick/reservation/status/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({
                reservation_id: reservationId,
                action: action
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            showAdminToast(data.message || "Could not update reservation.", true);
            return;
        }

        updateReservationRow(data.reservationId, data.newStatus, data.newStatusDisplay);
        showAdminToast(data.message || "Reservation updated.");

        setTimeout(() => {
            window.location.reload();
        }, 650);

    } catch (error) {
        console.error("Reservation update error:", error);
        showAdminToast("Something went wrong updating the reservation.", true);
    }
}

function updateReservationRow(reservationId, newStatus, newStatusDisplay) {
    const row = document.getElementById(`reservation-row-${reservationId}`);
    const pill = document.getElementById(`status-pill-${reservationId}`);

    if (row) {
        row.dataset.status = newStatus;
    }

    if (pill) {
        pill.textContent = newStatusDisplay;
        pill.className = `status-pill status-${newStatus}`;
    }
}

function showAdminToast(message, isError = false) {
    const toast = document.getElementById("adminToast");

    if (!toast) {
        alert(message);
        return;
    }

    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.classList.add("show");

    clearTimeout(window.adminToastTimer);

    window.adminToastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2600);
}

function setupReservationFilters() {
    const searchInput = document.getElementById("reservationSearch");
    const statusFilter = document.getElementById("statusFilter");
    const rows = Array.from(document.querySelectorAll(".reservation-table tbody tr"));

    if (!searchInput || !statusFilter || !rows.length) return;

    function applyFilters() {
        const searchValue = searchInput.value.trim().toLowerCase();
        const statusValue = statusFilter.value;

        rows.forEach(row => {
            const rowSearch = row.dataset.search || "";
            const rowStatus = row.dataset.status || "";

            const matchesSearch = !searchValue || rowSearch.includes(searchValue);
            const matchesStatus = !statusValue || rowStatus === statusValue;

            row.style.display = matchesSearch && matchesStatus ? "" : "none";
        });
    }

    searchInput.addEventListener("input", applyFilters);
    statusFilter.addEventListener("change", applyFilters);
}

document.addEventListener("DOMContentLoaded", function () {
    setupReservationFilters();
});