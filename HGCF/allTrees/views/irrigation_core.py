import requests # type: ignore
from django.shortcuts import render, redirect # type: ignore
from django.http import JsonResponse # type: ignore
from ..models import valve_registration, valve_schedule
from ..forms import valve_schedule_form
from django.utils.timezone import now # type: ignore
import json
from django.views.decorators.csrf import csrf_exempt # type: ignore
from ..utils import publish_valve_command
from .mqtt_pub import get_valve_statuses

#SHELLY_IP = "192.168.2.84"  # Replace with static IP of your Shelly

# def toggle_valve(request):
#     ip = request.GET.get("ip")
#     action = request.GET.get("action")  # 'on' or 'off'
#     if not ip or action not in ["on", "off"]:
#         return JsonResponse({"error": "Invalid input"}, status=400)

#     try:
#         res = requests.get(f"http://{ip}/rpc/Switch.Set?id=0&on={'true' if action == 'on' else 'false'}", timeout=3)
#         return JsonResponse({"status": "success"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)

def get_all_valve_statuses(request):
    try:
        status_map = get_valve_statuses()
        valves = {}
        registered_valves = list(valve_registration.objects.all())

        for i, valve in enumerate(registered_valves):
            device_id = valve.valveIP
            status = status_map.get(device_id)

            valves[device_id] = {
                "name": valve.name or f"Valve {chr(65 + i)}",
                "status": status,
                "ip": device_id  # Required by frontend
            }

        return JsonResponse({"status": "success", "valves": valves})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def get_schedule_overview(request):
    today = now().strftime('%a').lower()  # e.g., 'mon'
    schedules = valve_schedule.objects.filter(days__icontains=today)

    output = []
    for s in schedules:
        output.append({
            "valve": s.valve.name,
            "start": s.start_time.strftime('%H:%M'),
            "end": s.end_time.strftime('%H:%M'),
            "days": s.days
        })

    return JsonResponse({"schedules": output})

def irrigation_timer(request):
    noFooter = True
    smallHeader = True
    sideBar = True
    if request.method == 'POST':
        form = valve_schedule_form(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.days = ','.join(form.cleaned_data['days'])
            schedule.save()
            return redirect('dashboard')
    else:
        form = valve_schedule_form()

    return render(request, "irrigation/irrigation_timer.html", {
        'noFooter': noFooter, 
        'smallHeader': smallHeader,
        'sideBar': sideBar,
        'form': form
    })

def irrigation_dashboard(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    return render(request, "irrigation/irrigation_dashboard.html", {
        'noFooter': noFooter, 
        'smallHeader': smallHeader,
        'sideBar': sideBar,
    })

def emergency_shutoff(request):
    for valve in valve_registration.objects.all():
        try:
            requests.get(f"http://{valve.valveIP}/rpc/Switch.Set?id=0&on=false", timeout=2)
        except:
            continue
    return JsonResponse({"status": "all_off"})


@csrf_exempt
def toggle_valve(request):
    if request.method == "POST":
        data = json.loads(request.body)
        device_id = data.get("device_id")
        turn_on = data.get("turn") == "on"

        print(device_id, turn_on)
        try:
            publish_valve_command(device_id, turn_on)
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})


