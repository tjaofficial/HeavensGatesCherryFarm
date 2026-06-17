import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from ..models import FarmNewsletterSubscriber


def our_story_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False

    return render(request, "our_story.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,

        "seo_title": "Our Story | Heaven's Gates Cherry Farm",
        "seo_description": "Learn the story of Heaven's Gates Cherry Farm in Hale, Michigan — from 50 baby cherry trees and a dream to strawberries, fruit trees, gardens, faith, hard work, and family.",
        "seo_keywords": "Heaven's Gates Cherry Farm story, Hale Michigan farm, Michigan cherry farm, family farm, strawberry farm Michigan, U-pick farm Hale Michigan, local produce farm",
        "seo_robots": "index, follow",
        "seo_canonical": request.build_absolute_uri(),

        "og_type": "website",
        "og_title": "Our Story | Heaven's Gates Cherry Farm",
        "og_description": "From 50 baby cherry trees and a dream to a growing Michigan farm filled with strawberries, fruit trees, gardens, faith, and family.",
        "og_url": request.build_absolute_uri(),
        "og_image": request.build_absolute_uri("/static/images/HGCF-logo.png"),
        "og_image_alt": "Heaven's Gates Cherry Farm in Hale, Michigan",

        "twitter_title": "Our Story | Heaven's Gates Cherry Farm",
        "twitter_description": "Read how Heaven's Gates Cherry Farm grew from 50 baby cherry trees and a dream into a family farm in Hale, Michigan.",
        "twitter_image": request.build_absolute_uri("/static/images/HGCF-logo.png"),
    })

@require_POST
def our_story_subscribe_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        }, status=400)

    email = (data.get("email") or "").strip().lower()

    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()

    # Backwards compatibility for old forms that only sent "name"
    old_name = (data.get("name") or "").strip()

    full_name = f"{first_name} {last_name}".strip()

    if not full_name and old_name:
        full_name = old_name

    source = (data.get("source") or "our_story_page").strip()

    if not email:
        return JsonResponse({
            "success": False,
            "message": "Please enter your email address."
        }, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({
            "success": False,
            "message": "Please enter a valid email address."
        }, status=400)

    subscriber, created = FarmNewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "name": full_name,
            "source": source,
            "is_active": True,
        }
    )

    if not created:
        subscriber.is_active = True

        update_fields = ["is_active"]

        if first_name:
            subscriber.first_name = first_name
            update_fields.append("first_name")

        if last_name:
            subscriber.last_name = last_name
            update_fields.append("last_name")

        if full_name:
            subscriber.name = full_name
            update_fields.append("name")

        if source:
            subscriber.source = source
            update_fields.append("source")

        subscriber.save(update_fields=update_fields)

        return JsonResponse({
            "success": True,
            "message": "You’re already on the list — we updated your subscription."
        })

    return JsonResponse({
        "success": True,
        "message": "You’re subscribed! We’ll keep you posted on harvests, U-Pick updates, and farm news."
    })

def farm_subscribe_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False

    return render(request, "farm_subscribe.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,

        "seo_title": "Farm Subscription Form | Heaven's Gates Cherry Farm",
        "seo_description": "Subscribe for harvest updates, U-Pick announcements, and farm news from Heaven's Gates Cherry Farm in Hale, Michigan.",
        "seo_keywords": "Heaven's Gates Cherry Farm subscribe, farm newsletter Michigan, U-pick updates, strawberry harvest updates, Hale Michigan farm news",
        "seo_robots": "index, follow",
        "seo_canonical": request.build_absolute_uri(),

        "og_type": "website",
        "og_title": "Subscribe to Heaven's Gates Cherry Farm Updates",
        "og_description": "Get harvest updates, U-Pick announcements, and farm news from Heaven's Gates Cherry Farm.",
        "og_url": request.build_absolute_uri(),
        "og_image": request.build_absolute_uri("/static/images/HGCF-logo.png"),
        "og_image_alt": "Heaven's Gates Cherry Farm",

        "twitter_title": "Subscribe to Heaven's Gates Cherry Farm Updates",
        "twitter_description": "Get harvest updates, U-Pick announcements, and farm news from Heaven's Gates Cherry Farm.",
        "twitter_image": request.build_absolute_uri("/static/images/HGCF-logo.png"),
    })



