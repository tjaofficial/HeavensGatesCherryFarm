import requests # type: ignore
from django.shortcuts import render, redirect # type: ignore
from django.http import JsonResponse # type: ignore
from ..models import valve_registration, valve_schedule
from ..forms import valve_schedule_form, ValveRegistrationForm
from django.utils.timezone import now # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
import json
from django.views.decorators.csrf import csrf_exempt # type: ignore
from ..utils import publish_valve_command, get_irrigation_log_messages, add_log_to_area_trees
from .mqtt_pub import get_valve_statuses

lock = login_required(login_url='login')

def get_all_valve_statuses(request):
    status_map = get_valve_statuses()
    try:
        #print("Valve Status Map:", status_map)  # Add this
        valves = {}
        registered_valves = list(valve_registration.objects.all())

        for i, valve in enumerate(registered_valves):
            device_id = valve.valveIP
            status = status_map.get(device_id)

            valves[device_id] = {
                "name": valve.name or f"Valve {chr(65 + i)}",
                "status": status,
                "ip": device_id,  # Required by frontend
                "area_name": valve.areaID.name
            }

        #print(valves)

        return JsonResponse({"status": "success", "valves": valves})
    except Exception as e:
        return JsonResponse({"status": "error2", "message": str(e)}, status=500)

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
            return redirect('irrigation_dashboard')
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
    try:
        for valve in valve_registration.objects.all():
            deviveID = valve.valveIP
            try:
                publish_valve_command(deviveID, False)
                logMessage = get_irrigation_log_messages('emergency', 'stop_all', valve, request.user)
                add_log_to_area_trees(valve, logMessage, 'Irrigation')
            except:
                continue
        return JsonResponse({"status": "all_off"})
    except Exception as e:
            return JsonResponse({"status": "error-e-stop", "message": str(e)})

@csrf_exempt
def toggle_valve(request):
    if request.method == "POST":
        data = json.loads(request.body)
        device_id = data.get("device_id")
        turn_on = data.get("turn_on") == True

        print(device_id, turn_on)
        valveSelect = valve_registration.objects.get(valveIP=device_id)
        logMessage = get_irrigation_log_messages('manual', 'start', valveSelect, request.user)
        print(logMessage)
        try:
            if turn_on:
                allValves = valve_registration.objects.all()
                for valve in allValves:
                    deviveID = valve.valveIP
                    if deviveID == device_id:
                        publish_valve_command(device_id, True)
                        logMessage = get_irrigation_log_messages('manual', 'start', valveSelect, request.user)
                        add_log_to_area_trees(valveSelect, logMessage, 'Irrigation')
                        valveSelect.manual_override = True
                        valveSelect.save()
                    else:
                        publish_valve_command(deviveID, False)
                        logMessage = get_irrigation_log_messages('manual', 'stop', valve, request.user)
                        add_log_to_area_trees(valve, logMessage, 'Irrigation')
                        valveSelect.manual_override = True
                        valveSelect.save()
            else:
                publish_valve_command(device_id, False)
                logMessage = get_irrigation_log_messages('manual', 'stop', valveSelect, request.user)
                add_log_to_area_trees(valveSelect, logMessage, 'Irrigation')
                valveSelect.manual_override = True
                valveSelect.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error1", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})

@lock
def add_valve(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    if request.method == 'POST':
        form = ValveRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('irrigation_dashboard')
    else:
        form = ValveRegistrationForm()
    return render(request, 'irrigation/add_valve.html', {
        'noFooter': noFooter, 
        'smallHeader': smallHeader,
        'sideBar': sideBar,
        'form': form
    })



