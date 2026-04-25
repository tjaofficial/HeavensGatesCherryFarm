import json
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required # type: ignore
from django.http import JsonResponse # type: ignore
from django.shortcuts import render, get_object_or_404, redirect # type: ignore
from django.views.decorators.http import require_http_methods # type: ignore
from django.db.models import Sum # type: ignore
from ..models import UPickEvent, UPickTimeSlot, UPickReservation

@staff_member_required
def treespace_upick_dashboard_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    events = UPickEvent.objects.all().order_by("-date")

    selected_event = None
    selected_event_id = request.GET.get("event")

    if selected_event_id:
        selected_event = get_object_or_404(UPickEvent, id=selected_event_id)
    else:
        selected_event = UPickEvent.objects.filter(
            date__gte=date.today()
        ).order_by("date").first()

        if not selected_event:
            selected_event = UPickEvent.objects.order_by("-date").first()

    time_slots = []
    reservations = []

    total_capacity = 0
    total_reserved = 0
    total_checked_in = 0
    total_completed = 0
    total_no_show = 0
    total_cancelled = 0
    spots_remaining = 0

    if selected_event:
        time_slots = selected_event.time_slots.all().order_by("start_time")

        reservations = UPickReservation.objects.filter(
            time_slot__event=selected_event
        ).select_related(
            "time_slot",
            "user"
        ).order_by(
            "time_slot__start_time",
            "last_name",
            "first_name"
        )

        total_capacity = sum(slot.capacity for slot in time_slots)

        active_reservations = reservations.filter(
            status__in=["confirmed", "checked_in"]
        )

        total_reserved = sum(res.party_size for res in active_reservations)

        total_checked_in = sum(
            res.party_size for res in reservations.filter(status="checked_in")
        )

        total_completed = sum(
            res.party_size for res in reservations.filter(status="completed")
        )

        total_no_show = sum(
            res.party_size for res in reservations.filter(status="no_show")
        )

        total_cancelled = sum(
            res.party_size for res in reservations.filter(status="cancelled")
        )

        spots_remaining = max(total_capacity - total_reserved, 0)

    return render(request, "treespace/upick_dashboard.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,

        "events": events,
        "selected_event": selected_event,
        "time_slots": time_slots,
        "reservations": reservations,

        "total_capacity": total_capacity,
        "total_reserved": total_reserved,
        "total_checked_in": total_checked_in,
        "total_completed": total_completed,
        "total_no_show": total_no_show,
        "total_cancelled": total_cancelled,
        "spots_remaining": spots_remaining,
    })

@staff_member_required
@require_http_methods(["POST"])
def treespace_upick_update_reservation_status(request):
    try:
        json_data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid request data."
        }, status=400)

    reservation_id = json_data.get("reservation_id")
    action = json_data.get("action")

    if not reservation_id or not action:
        return JsonResponse({
            "success": False,
            "message": "Missing reservation or action."
        }, status=400)

    reservation = get_object_or_404(
        UPickReservation.objects.select_related("time_slot", "time_slot__event"),
        id=reservation_id
    )

    if action == "check_in":
        if reservation.status != "confirmed":
            return JsonResponse({
                "success": False,
                "message": "Only confirmed reservations can be checked in."
            }, status=400)

        reservation.check_in()
        message = f"{reservation.full_name()} checked in."

    elif action == "complete":
        if reservation.status != "checked_in":
            return JsonResponse({
                "success": False,
                "message": "Only checked-in reservations can be completed."
            }, status=400)

        reservation.mark_completed()
        message = f"{reservation.full_name()} marked completed."

    elif action == "no_show":
        reservation.mark_no_show()
        message = f"{reservation.full_name()} marked as no-show."

    elif action == "cancel":
        reservation.cancel()
        message = f"{reservation.full_name()} cancelled."

    elif action == "release":
        reservation.release_to_walkins()
        message = f"{reservation.full_name()} released to walk-ins."

    elif action == "confirm":
        reservation.status = "confirmed"
        reservation.save(update_fields=["status"])
        message = f"{reservation.full_name()} confirmed."

    else:
        return JsonResponse({
            "success": False,
            "message": "Invalid action."
        }, status=400)

    return JsonResponse({
        "success": True,
        "message": message,
        "reservationId": reservation.id,
        "newStatus": reservation.status,
        "newStatusDisplay": reservation.get_status_display(),
    })