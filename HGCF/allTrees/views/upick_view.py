from datetime import date
from django.shortcuts import render, redirect, get_object_or_404 #type: ignore
from django.db.models import Prefetch #type: ignore
from django.contrib import messages #type: ignore
from django.views.decorators.http import require_http_methods #type: ignore

from ..models import UPickEvent, UPickTimeSlot, UPickReservation
from ..forms import UPickReservationForm


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