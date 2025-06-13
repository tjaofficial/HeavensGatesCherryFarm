from django.shortcuts import render

def homePage_view(request):
    return render(request, "homePage.html", {
        
    })

def announcements_view(request):
    return render(request, "announcements.html", {
        
    })