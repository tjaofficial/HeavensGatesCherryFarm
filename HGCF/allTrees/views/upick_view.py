from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404 #type: ignore
from django.db import transaction
from django.db.models import Prefetch #type: ignore
from django.contrib import messages #type: ignore
from django.views.decorators.http import require_http_methods #type: ignore
from django.contrib.auth.decorators import login_required


from ..models import UPickEvent, UPickTimeSlot, UPickReservation
from ..forms import UPickReservationForm
from ..utils import send_upick_reservation_confirmation

DEFAULT_UPICK_RULES_TEXT = """Please check in when you arrive before entering the picking area.

Please arrive during your reserved time slot. If you are running late, your reservation may be released after the grace period so we can keep the day moving smoothly for other guests.

Children are welcome, but they must stay with an adult at all times.

Please stay in the marked picking areas and only pick from the rows or areas opened by farm staff.

Please do not climb on trees, fences, equipment, irrigation lines, or farm structures.

Closed-toe shoes are strongly recommended. The field may be muddy, uneven, wet, or slippery depending on weather and irrigation.

No pets are allowed in the picking fields. If you use a service animal, please contact us or check in with farm staff when you arrive so we can help guide safe access.

Please do not smoke, vape, drink alcohol, or litter anywhere in the picking areas.

Please be respectful of the plants. Do not pull, damage, or step on plants, rows, irrigation lines, or field markers.

Only pick ripe fruit from approved areas. If you are unsure what to pick, please ask farm staff.

Please do not eat fruit from the field unless farm staff says sampling is allowed that day.

Weather can affect U-Pick availability. Heavy rain, lightning, unsafe field conditions, or poor crop availability may cause delays, changes, or cancellations.

By visiting the farm, guests understand that this is an active farm with natural outdoor conditions, including uneven ground, insects, mud, weather changes, and farm equipment.

Thank you for helping us keep Heaven’s Gates Cherry Farm safe, clean, and enjoyable for everyone."""

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    return ip

def upick_landing_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False

    events = UPickEvent.objects.filter(
        is_active=True,
        is_public=True,
        date__gte=date.today()
    ).order_by("date")

    return render(request, "upick/upick_landing.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "events": events,
        "seo_title": "U-Pick Organic Strawberries & Fruit | Heaven's Gates Cherry Farm",
        "seo_description": "Plan your U-Pick visit to Heaven's Gates Cherry Farm in Hale, Michigan. Pick fresh organic seasonal strawberries and fruit, check availability, and enjoy a family-friendly farm experience.",
        "seo_keywords": "U-pick organic strawberries Michigan, U-pick organic fruit Hale Michigan, Heaven's Gates Cherry Farm U-pick organic, Michigan organic strawberry picking, Hale Michigan organic farm, family farm experience, fresh fruit picking, northern Michigan U-pick",
        "seo_robots": "index, follow",
        "seo_canonical": request.build_absolute_uri(),

        "og_type": "website",
        "og_title": "U-Pick at Heaven's Gates Cherry Farm",
        "og_description": "Visit Heaven's Gates Cherry Farm in Hale, Michigan for a seasonal U-Pick experience with fresh organic strawberries, fruit, and family-friendly farm fun.",
        "og_url": request.build_absolute_uri(),
        "og_image": request.build_absolute_uri("/static/images/strawberries.jpg"),
        "og_image_alt": "Fresh organic strawberries available for U-Pick at Heaven's Gates Cherry Farm",

        "twitter_title": "U-Pick at Heaven's Gates Cherry Farm",
        "twitter_description": "Plan your U-Pick visit to Heaven's Gates Cherry Farm in Hale, Michigan for fresh seasonal organic strawberries and fruit.",
        "twitter_image": request.build_absolute_uri("/static/images/strawberries.jpg"),
    })

def upick_day_view(request, event_id):
    noFooter = False
    smallHeader = False
    sideBar = False

    event = get_object_or_404(
        UPickEvent,
        id=event_id,
        is_active=True,
        is_public=True
    )

    time_slots = event.time_slots.filter(
        is_active=True
    ).order_by("start_time")

    return render(request, "upick/upick_day.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "event": event,
        "time_slots": time_slots,
    })

@require_http_methods(["GET", "POST"])
def upick_reserve_view(request, slot_id):
    noFooter = False
    smallHeader = False
    sideBar = False

    time_slot = get_object_or_404(
        UPickTimeSlot,
        id=slot_id,
        is_active=True,
        event__is_active=True,
        event__is_public=True,
    )

    if time_slot.is_full():
        messages.error(request, "That time slot is full. Please choose another one.")
        return redirect("upick_day", event_id=time_slot.event.id)

    if request.method == "POST":
        form = UPickReservationForm(request.POST)

        if form.is_valid():
            party_size = form.cleaned_data["party_size"]

            if party_size > time_slot.spots_remaining():
                form.add_error(
                    "party_size",
                    f"Only {time_slot.spots_remaining()} spots are left for this time slot."
                )
            else:
                email = form.cleaned_data["email"]
                phone = form.cleaned_data["phone"]

                existing_reservation = UPickReservation.objects.filter(
                    time_slot__event=time_slot.event,
                    status__in=["pending", "confirmed", "checked_in"],
                ).filter(
                    email=email
                ).exists()

                if existing_reservation:
                    form.add_error(
                        "email",
                        "You already have a reservation for this U-Pick day."
                    )
                else:
                    reservation = form.save(commit=False)
                    reservation.time_slot = time_slot
                    reservation.ip_address = get_client_ip(request)

                    if request.user.is_authenticated:
                        reservation.user = request.user

                    reservation.status = "confirmed"
                    reservation.save()

                    transaction.on_commit(
                        lambda: send_upick_reservation_confirmation(reservation)
                    )

                    return redirect("upick_success", reservation_id=reservation.id)
    else:
        initial = {}

        if request.user.is_authenticated:
            initial["email"] = request.user.email

            if request.user.first_name:
                initial["first_name"] = request.user.first_name

            if request.user.last_name:
                initial["last_name"] = request.user.last_name

        form = UPickReservationForm(initial=initial)

    return render(request, "upick/upick_reserve.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "time_slot": time_slot,
        "event": time_slot.event,
        "form": form,
    })

def upick_success_view(request, reservation_id):
    noFooter = False
    smallHeader = False
    sideBar = False

    reservation = get_object_or_404(
        UPickReservation,
        id=reservation_id
    )

    return render(request, "upick/upick_success.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "reservation": reservation,
    })

@login_required
def treespace_upick_setup_view(request):
    smallHeader = True
    noFooter = True
    sideBar = True

    events = (
        UPickEvent.objects
        .prefetch_related("time_slots")
        .all()
        .order_by("-date", "title")
    )

    if request.method == "POST":
        crop_name = request.POST.get("crop_name", "Strawberries").strip()
        title = request.POST.get("title", "U-Pick Strawberries").strip()
        description = request.POST.get("description", "").strip()
        date = request.POST.get("date")

        weather_note = request.POST.get("weather_note", "").strip()
        field_note = request.POST.get("field_note", "").strip()
        rules_text = request.POST.get("rules_text", "").strip()

        if not rules_text:
            rules_text = DEFAULT_UPICK_RULES_TEXT

        default_slot_capacity = int(request.POST.get("default_slot_capacity") or 10)
        default_slot_minutes = int(request.POST.get("default_slot_minutes") or 60)
        grace_period_minutes = int(request.POST.get("grace_period_minutes") or 15)

        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        is_public = request.POST.get("is_public") == "on"
        is_active = request.POST.get("is_active") == "on"

        if not date:
            messages.error(request, "Please choose a date for the U-Pick day.")
            return redirect("treespace_upick_setup")

        event = UPickEvent.objects.create(
            crop_name=crop_name,
            title=title,
            description=description,
            date=date,
            is_active=is_active,
            is_public=is_public,
            default_slot_capacity=default_slot_capacity,
            default_slot_minutes=default_slot_minutes,
            grace_period_minutes=grace_period_minutes,
            weather_note=weather_note,
            field_note=field_note,
            rules_text=rules_text,
        )

        if start_time and end_time:
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

            current = start_dt

            while current < end_dt:
                slot_end = current + timedelta(minutes=default_slot_minutes)

                if slot_end > end_dt:
                    break

                UPickTimeSlot.objects.create(
                    event=event,
                    start_time=current.time(),
                    end_time=slot_end.time(),
                    capacity=default_slot_capacity,
                    is_active=True,
                    is_walk_in_available=True,
                )

                current = slot_end

        messages.success(request, "U-Pick day created successfully.")
        return redirect("treespace_upick_setup")

    return render(request, "treeSpace/upick_setup.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "events": events,
        "default_rules_text": DEFAULT_UPICK_RULES_TEXT,
    })