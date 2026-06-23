import json
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required # type: ignore
from django.http import JsonResponse # type: ignore
from django.shortcuts import render, get_object_or_404, redirect # type: ignore
from django.views.decorators.http import require_http_methods # type: ignore
from django.db.models import Sum # type: ignore
from ..models import UPickEvent, UPickTimeSlot, UPickReservation, UPickWaitlistEntry, FarmNewsletterSubscriber
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.urls import reverse
from ..utils import send_upick_reservation_confirmation
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings



@login_required
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

    return render(request, "treeSpace/upick_dashboard.html", {
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

@login_required
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

@login_required
@require_http_methods(["POST"])
def treespace_upick_remove_waitlist_entry(request, entry_id):
    waitlist_entry = get_object_or_404(
        UPickWaitlistEntry,
        id=entry_id,
        status=UPickWaitlistEntry.STATUS_WAITING
    )

    removed_reason = request.POST.get("removed_reason", "").strip()

    waitlist_entry.status = UPickWaitlistEntry.STATUS_REMOVED
    waitlist_entry.removed_reason = removed_reason
    waitlist_entry.removed_at = timezone.now()
    waitlist_entry.save(update_fields=[
        "status",
        "removed_reason",
        "removed_at",
    ])

    messages.success(
        request,
        f"{waitlist_entry.full_name()} was removed from the waiting list."
    )

    return redirect(f"{reverse('treespace_upick_dashboard')}?event={waitlist_entry.event.id}")

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def treespace_upick_convert_waitlist_entry(request, entry_id):
    waitlist_entry = get_object_or_404(
        UPickWaitlistEntry,
        id=entry_id,
        status=UPickWaitlistEntry.STATUS_WAITING
    )

    time_slot_id = request.POST.get("time_slot_id")

    if not time_slot_id:
        messages.error(
            request,
            "Please select an available time slot before creating the reservation."
        )
        return redirect("treespace_upick_waitlist")

    time_slot = (
        UPickTimeSlot.objects
        .select_related("event")
        .filter(
            id=time_slot_id,
            is_active=True,
            event__is_active=True,
        )
        .first()
    )

    if not time_slot:
        messages.error(
            request,
            "That time slot could not be found or is no longer active."
        )
        return redirect("treespace_upick_waitlist")

    # Specific-day waitlist entries can only go into that same event.
    # General waitlist entries have event=None and can go into any selected slot.
    if waitlist_entry.event and time_slot.event_id != waitlist_entry.event_id:
        messages.error(
            request,
            "That time slot does not match this waitlist entry's U-Pick day."
        )
        return redirect("treespace_upick_waitlist")

    remaining_spots = time_slot.spots_remaining()
    will_overbook = waitlist_entry.people_count > remaining_spots

    overbook_note = ""
    if will_overbook:
        overbook_note = (
            f" OVERBOOKED: Slot had {remaining_spots} spot(s) remaining, "
            f"but waitlist guest was added with {waitlist_entry.people_count} people."
        )

    reservation = UPickReservation.objects.create(
        time_slot=time_slot,
        first_name=waitlist_entry.first_name,
        last_name=waitlist_entry.last_name,
        email=waitlist_entry.email,
        phone=waitlist_entry.phone,
        party_size=waitlist_entry.people_count,
        estimated_quarts=waitlist_entry.estimated_quarts,
        status="confirmed",
        agreed_to_rules=True,
        customer_note=waitlist_entry.notes,
        internal_note=(
            f"Created from waitlist entry #{waitlist_entry.id}. "
            f"Estimated quarts: {waitlist_entry.estimated_quarts or 'N/A'}."
            f"{overbook_note}"
        ),
    )

    waitlist_entry.status = UPickWaitlistEntry.STATUS_CONVERTED
    waitlist_entry.converted_reservation = reservation
    waitlist_entry.converted_at = timezone.now()
    waitlist_entry.save(update_fields=[
        "status",
        "converted_reservation",
        "converted_at",
    ])

    transaction.on_commit(
        lambda: send_upick_reservation_confirmation(reservation)
    )

    if will_overbook:
        messages.warning(
            request,
            f"{waitlist_entry.full_name()} was added as a reservation, but this slot is now overbooked."
        )
    else:
        messages.success(
            request,
            f"{waitlist_entry.full_name()} was added as a reservation and sent a confirmation email."
        )

    return redirect(f"{reverse('treespace_upick_dashboard')}?event={time_slot.event.id}")

def chunk_list(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def normalize_email(email):
    if not email:
        return ""

    return email.strip().lower()


def get_email_update_recipients(
    include_subscribers=False,
    include_reservations=False,
    include_waitlist=False
):
    recipients = set()

    # Farm newsletter subscribers
    if include_subscribers:
        subscriber_emails = FarmNewsletterSubscriber.objects.filter(
            is_active=True
        ).exclude(
            email__isnull=True
        ).exclude(
            email__exact=""
        ).values_list("email", flat=True)

        for email in subscriber_emails:
            clean_email = normalize_email(email)

            if clean_email:
                recipients.add(clean_email)

    # U-Pick reservation emails
    if include_reservations:
        reservation_emails = UPickReservation.objects.exclude(
            email__isnull=True
        ).exclude(
            email__exact=""
        ).values_list("email", flat=True)

        for email in reservation_emails:
            clean_email = normalize_email(email)

            if clean_email:
                recipients.add(clean_email)

    # U-Pick waitlist emails
    if include_waitlist:
        waitlist_emails = UPickWaitlistEntry.objects.exclude(
            email__isnull=True
        ).exclude(
            email__exact=""
        ).values_list("email", flat=True)

        for email in waitlist_emails:
            clean_email = normalize_email(email)

            if clean_email:
                recipients.add(clean_email)

    return sorted(recipients)


@login_required
@require_http_methods(["GET", "POST"])
def treespace_email_update_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    preview_count = None

    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        include_subscribers = request.POST.get("include_subscribers") == "on"
        include_reservations = request.POST.get("include_reservations") == "on"
        include_waitlist = request.POST.get("include_waitlist") == "on"

        action = request.POST.get("action")

        recipients = get_email_update_recipients(
            include_subscribers=include_subscribers,
            include_reservations=include_reservations,
            include_waitlist=include_waitlist,
        )

        preview_count = len(recipients)

        if action == "preview":
            messages.info(
                request,
                f"This email would send to {preview_count} unique recipient(s)."
            )

            return render(request, "treeSpace/email_update.html", {
                "smallHeader": smallHeader,
                "noFooter": noFooter,
                "sideBar": sideBar,
                "preview_count": preview_count,
                "subject": subject,
                "message": message,
                "include_subscribers": include_subscribers,
                "include_reservations": include_reservations,
                "include_waitlist": include_waitlist,
            })

        if not subject:
            messages.error(request, "Please enter an email subject.")
            return redirect("treespace_email_update")

        if not message:
            messages.error(request, "Please enter an email message.")
            return redirect("treespace_email_update")

        if not recipients:
            messages.error(request, "No recipients were found for the selected audience.")
            return redirect("treespace_email_update")

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

        if not from_email:
            messages.error(request, "DEFAULT_FROM_EMAIL is not configured in settings.py.")
            return redirect("treespace_email_update")

        sent_count = 0
        failed_count = 0

        plain_text_message = message

        html_message = message.replace("\n", "<br>")

        # Send in batches using BCC so recipients do not see each other's emails.
        for recipient_batch in chunk_list(recipients, 50):
            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_text_message,
                    from_email=from_email,
                    to=[from_email],
                    bcc=recipient_batch,
                )

                email.attach_alternative(html_message, "text/html")
                email.send(fail_silently=False)

                sent_count += len(recipient_batch)

            except Exception as e:
                failed_count += len(recipient_batch)
                print("Email update send failed:", e)

        if failed_count:
            messages.warning(
                request,
                f"Email attempted. Sent to {sent_count} recipient(s), but {failed_count} failed."
            )
        else:
            messages.success(
                request,
                f"Email sent to {sent_count} recipient(s)."
            )

        return redirect("treespace_email_update")

    return render(request, "treeSpace/email_update.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "preview_count": preview_count,
    })





