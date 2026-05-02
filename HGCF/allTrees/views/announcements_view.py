from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.db.models.functions import ExtractYear
from ..models import FarmAnnouncement


def announcements_view(request):
    noFooter = False
    smallHeader = False
    sideBar = False

    search_query = request.GET.get("q", "").strip()
    selected_month = request.GET.get("month", "").strip()
    selected_year = request.GET.get("year", "").strip()
    selected_type = request.GET.get("type", "").strip()

    announcements = FarmAnnouncement.objects.filter(
        status="published",
        publish_date__lte=timezone.now()
    )

    if search_query:
        announcements = announcements.filter(
            Q(title__icontains=search_query) |
            Q(summary__icontains=search_query) |
            Q(body__icontains=search_query)
        )

    if selected_month:
        try:
            selected_month_int = int(selected_month)
            announcements = announcements.filter(publish_date__month=selected_month_int)
        except ValueError:
            selected_month = ""

    if selected_year:
        try:
            selected_year_int = int(selected_year)
            announcements = announcements.filter(publish_date__year=selected_year_int)
        except ValueError:
            selected_year = ""

    if selected_type:
        announcements = announcements.filter(announcement_type=selected_type)

    announcements = announcements.order_by("-is_pinned", "-publish_date")

    available_years = (
        FarmAnnouncement.objects.filter(
            status="published",
            publish_date__lte=timezone.now()
        )
        .annotate(year=ExtractYear("publish_date"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )

    months = [
        {"number": "1", "name": "January"},
        {"number": "2", "name": "February"},
        {"number": "3", "name": "March"},
        {"number": "4", "name": "April"},
        {"number": "5", "name": "May"},
        {"number": "6", "name": "June"},
        {"number": "7", "name": "July"},
        {"number": "8", "name": "August"},
        {"number": "9", "name": "September"},
        {"number": "10", "name": "October"},
        {"number": "11", "name": "November"},
        {"number": "12", "name": "December"},
    ]

    announcement_types = FarmAnnouncement.ANNOUNCEMENT_TYPE_CHOICES

    return render(request, "announcements/announcements.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,

        "announcements": announcements,
        "search_query": search_query,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "selected_type": selected_type,
        "available_years": available_years,
        "months": months,
        "announcement_types": announcement_types,

        "seo_title": "Farm Announcements | Heaven's Gates Cherry Farm",
        "seo_description": "Read the latest farm announcements, harvest updates, U-pick news, store updates, weather notices, and seasonal news from Heaven's Gates Cherry Farm in Hale, Michigan.",
        "seo_keywords": "Heaven's Gates Cherry Farm announcements, farm news Hale Michigan, Michigan farm updates, U-pick updates, strawberry harvest updates, cherry farm news",
        "seo_robots": "index, follow",
        "seo_canonical": request.build_absolute_uri(),

        "og_type": "website",
        "og_title": "Farm Announcements | Heaven's Gates Cherry Farm",
        "og_description": "Stay updated with harvest news, U-pick announcements, farm store updates, and seasonal notices from Heaven's Gates Cherry Farm.",
        "og_url": request.build_absolute_uri(),
        "og_image": request.build_absolute_uri("/static/images/HGCF-logo.png"),
        "og_image_alt": "Heaven's Gates Cherry Farm announcements",

        "twitter_title": "Farm Announcements | Heaven's Gates Cherry Farm",
        "twitter_description": "Stay updated with harvest news, U-pick announcements, farm store updates, and seasonal notices from Heaven's Gates Cherry Farm.",
        "twitter_image": request.build_absolute_uri("/static/images/HGCF-logo.png"),
    })

def announcement_detail_view(request, slug):
    noFooter = False
    smallHeader = False
    sideBar = False

    announcement = get_object_or_404(
        FarmAnnouncement,
        slug=slug,
        status="published",
        publish_date__lte=timezone.now()
    )

    recent_announcements = FarmAnnouncement.objects.filter(
        status="published",
        publish_date__lte=timezone.now()
    ).exclude(
        id=announcement.id
    ).order_by("-is_pinned", "-publish_date")[:3]

    if announcement.featured_image:
        og_image = request.build_absolute_uri(announcement.featured_image.url)
    else:
        og_image = request.build_absolute_uri("/static/images/HGCF-logo.png")

    return render(request, "announcements/announcement_detail.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,

        "announcement": announcement,
        "recent_announcements": recent_announcements,

        "seo_title": announcement.meta_title or f"{announcement.title} | Heaven's Gates Cherry Farm",
        "seo_description": announcement.meta_description or announcement.summary,
        "seo_keywords": "Heaven's Gates Cherry Farm, farm announcement, farm news, Hale Michigan farm, U-pick updates, harvest updates",
        "seo_robots": "index, follow",
        "seo_canonical": request.build_absolute_uri(),

        "og_type": "article",
        "og_title": announcement.title,
        "og_description": announcement.summary,
        "og_url": request.build_absolute_uri(),
        "og_image": og_image,
        "og_image_alt": announcement.image_alt_text or announcement.title,

        "twitter_title": announcement.title,
        "twitter_description": announcement.summary,
        "twitter_image": og_image,
    })