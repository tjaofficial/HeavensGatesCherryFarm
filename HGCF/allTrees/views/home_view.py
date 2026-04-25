from django.shortcuts import render
from ..utils import build_seo

def homePage_view(request):
    return render(request, "homePage.html", {
        
    })

def announcements_view(request):
    context={}
    context.update(build_seo(
        request,
        title="About Our Farm | Heaven's Gates Cherry Farm",
        description="Learn about Heaven's Gates Cherry Farm, our family roots, and our mission to grow quality fruit in Hale, Michigan.",
        keywords="about Michigan farm, family cherry farm, Hale Michigan agriculture"
    ))
    return render(request, "announcements.html", context)