from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..utils import get_hale_farm_weather, get_cached_hale_forecast


lock = login_required(login_url='Login')

@lock
def weather_dashboard_view(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    weather = get_cached_hale_forecast()
    farm_weather = get_hale_farm_weather()

    return render(request, "environmental/weatherDashboard.html", {
        "smallHeader": smallHeader,
        "noFooter": noFooter,
        "sideBar": sideBar,
        "weather": weather,
        "farm_weather": farm_weather,
    })