from django.shortcuts import render
from ..utils import build_seo

def homePage_view(request):
    return render(request, "homePage.html", {
        "seo_title": "Heaven's Gates Cherry Farm | Hale, Michigan Fruit Farm",
        "seo_description": "Heaven's Gates Cherry Farm is a family-owned cherry and strawberry farm in Hale, Michigan offering fresh fruit, seasonal produce, U-pick experiences, and local farm products.",
        "seo_keywords": "Heaven's Gates Cherry Farm, Hale Michigan farm, Michigan cherry farm, Michigan strawberry farm, fresh cherries, fresh strawberries, U-pick fruit, local produce, northern Michigan fruit farm",
        "seo_robots": "index, follow",
        "seo_canonical": request.build_absolute_uri(),

        "og_type": "website",
        "og_title": "Heaven's Gates Cherry Farm | Hale, Michigan Fruit Farm",
        "og_description": "Fresh cherries, strawberries, seasonal produce, U-pick experiences, and local farm goods from our family farm in Hale, Michigan.",
        "og_url": request.build_absolute_uri(),
        "og_image": request.build_absolute_uri("/static/images/hgcf-og-home.png"),
        "og_image_alt": "Heaven's Gates Cherry Farm logo",

        "twitter_title": "Heaven's Gates Cherry Farm | Hale, Michigan Fruit Farm",
        "twitter_description": "Fresh cherries, strawberries, seasonal produce, U-pick experiences, and local farm goods from our family farm in Hale, Michigan.",
        "twitter_image": request.build_absolute_uri("/static/images/hgcf-og-home.png"),
    })