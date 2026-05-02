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
    name = (data.get("name") or "").strip()

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
            "name": name,
            "source": "our_story_page",
            "is_active": True,
        }
    )

    if not created:
        subscriber.is_active = True

        if name and not subscriber.name:
            subscriber.name = name

        subscriber.save(update_fields=["is_active", "name"])

        return JsonResponse({
            "success": True,
            "message": "You’re already on the list — we reactivated your subscription."
        })

    return JsonResponse({
        "success": True,
        "message": "You’re subscribed! We’ll keep you posted on harvests, U-pick updates, and farm news."
    })