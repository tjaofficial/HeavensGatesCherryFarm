from django.shortcuts import render, redirect
from ..utils import weatherDict
from django.contrib.auth.decorators import login_required

lock = login_required(login_url='Login')

@lock
def weather_dashboard_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True
    weather = weatherDict('hale')
    return render(request, "environmental/weatherDashboard.html", {
        'smallHeader': smallHeader,
        'noFooter': noFooter,
        'sideBar': sideBar,
        'weather': weather
    })