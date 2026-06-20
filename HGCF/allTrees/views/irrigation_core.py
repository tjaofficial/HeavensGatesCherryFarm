import requests # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore
from ..models import valve_registration, valve_schedule
from ..forms import valve_schedule_form, ValveRegistrationForm
from django.utils.timezone import now # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
import json
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.views.decorators.http import require_POST
from ..utils import publish_valve_command, get_irrigation_log_messages, add_log_to_area_trees
from .mqtt_pub import get_valve_statuses
from django.urls import reverse
import time

lock = login_required(login_url='login')

@lock
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

@lock
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

@lock
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
        'form': form,
        'is_edit': False,
        'page_title': 'Set Irrigation Schedule',
        'page_subtitle': 'Create an automated valve run by time and day.',
        'submit_label': 'Save Schedule',
    })

@lock
def irrigation_dashboard(request):
    noFooter = True
    smallHeader = True
    sideBar = True

    return render(request, "irrigation/irrigation_dashboard.html", {
        'noFooter': noFooter, 
        'smallHeader': smallHeader,
        'sideBar': sideBar,
    })

@lock
@require_POST
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

@lock
@require_POST
def toggle_valve(request):
    try:
        data = json.loads(request.body)
        device_id = data.get("device_id")
        turn_on = data.get("turn_on") is True

        valveSelect = valve_registration.objects.get(valveIP=device_id)

        print(device_id, turn_on)

        try:
            if turn_on:
                allValves = valve_registration.objects.all()

                for valve in allValves:
                    valve_device_id = valve.valveIP

                    if valve_device_id == device_id:
                        publish_valve_command(device_id, True)

                        logMessage = get_irrigation_log_messages(
                            'manual',
                            'start',
                            valveSelect,
                            request.user
                        )

                        add_log_to_area_trees(valveSelect, logMessage, 'Irrigation')

                    else:
                        publish_valve_command(valve_device_id, False)

                        logMessage = get_irrigation_log_messages(
                            'manual',
                            'stop',
                            valve,
                            request.user
                        )

                        add_log_to_area_trees(valve, logMessage, 'Irrigation')

                verified, samples = verify_valve_reached_status(
                    device_id,
                    expected_on=True,
                    attempts=4,
                    delay_seconds=5
                )

                if verified:
                    valveSelect.manual_override = True
                    valveSelect.save(update_fields=['manual_override'])

                    return JsonResponse({
                        "status": "success",
                        "message": f"{valveSelect.name} confirmed ON.",
                        "verification_samples": samples
                    })

                warning_message = (
                    f"Warning: {valveSelect.name} was told to turn ON, "
                    f"but it never confirmed ON after multiple checks. "
                    f"This may be a relay, power, wiring, or connection issue."
                )

                print("⚠️", warning_message)
                print("Verification samples:", samples)

                add_log_to_area_trees(
                    valveSelect,
                    warning_message,
                    'Irrigation'
                )

                return JsonResponse({
                    "status": "warning",
                    "message": warning_message,
                    "verification_samples": samples
                })

            else:
                publish_valve_command(device_id, False)

                logMessage = get_irrigation_log_messages(
                    'manual',
                    'stop',
                    valveSelect,
                    request.user
                )

                add_log_to_area_trees(valveSelect, logMessage, 'Irrigation')

                valveSelect.manual_override = True
                valveSelect.save(update_fields=['manual_override'])

                return JsonResponse({
                    "status": "success",
                    "message": f"{valveSelect.name} turned OFF."
                })

        except Exception as e:
            return JsonResponse({
                "status": "error1",
                "message": str(e)
            }, status=500)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

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

@lock
def get_schedule_overview(request):
    today = now().strftime('%a').lower()
    schedules = valve_schedule.objects.filter(days__icontains=today).select_related('valve')

    output = []

    for s in schedules:
        output.append({
            "id": s.id,
            "valve": s.valve.name,
            "start": s.start_time.strftime('%H:%M'),
            "end": s.end_time.strftime('%H:%M'),
            "days": s.days,
            "edit_url": reverse('irrigation_schedule_edit', args=[s.id]),
            "delete_url": reverse('irrigation_schedule_delete', args=[s.id]),
        })

    return JsonResponse({"schedules": output})

@lock
def irrigation_schedule_edit(request, schedule_id):
    noFooter = True
    smallHeader = True
    sideBar = True

    schedule = get_object_or_404(
        valve_schedule.objects.select_related('valve'),
        id=schedule_id
    )

    initial_days = []

    if schedule.days:
        initial_days = schedule.days.split(',')

    if request.method == 'POST':
        form = valve_schedule_form(request.POST, instance=schedule)

        if form.is_valid():
            edited_schedule = form.save(commit=False)
            edited_schedule.days = ','.join(form.cleaned_data['days'])
            edited_schedule.save()

            return redirect('irrigation_dashboard')
    else:
        form = valve_schedule_form(
            instance=schedule,
            initial={
                'days': initial_days
            }
        )

    return render(request, "irrigation/irrigation_timer.html", {
        'noFooter': noFooter,
        'smallHeader': smallHeader,
        'sideBar': sideBar,
        'form': form,
        'schedule': schedule,
        'is_edit': True,
        'page_title': 'Edit Irrigation Schedule',
        'page_subtitle': 'Update the valve, run time, and active days.',
        'submit_label': 'Save Changes',
    })

@lock
@require_POST
def irrigation_schedule_delete(request, schedule_id):
    schedule = get_object_or_404(valve_schedule, id=schedule_id)

    schedule.delete()

    return JsonResponse({
        "status": "success",
        "message": "Schedule deleted."
    })

def verify_valve_reached_status(device_id, expected_on=True, attempts=4, delay_seconds=5):
    """
    Checks the valve status multiple times before deciding it failed.

    This prevents false alerts from one bad/flaky status read.

    Success rule:
        If the valve reports the expected status even once, it passes.

    Failure rule:
        If every check misses or reports the wrong status, it fails.
    """

    samples = []

    for attempt in range(attempts):
        time.sleep(delay_seconds)

        try:
            status_map = get_valve_statuses()
            current_status = status_map.get(device_id)

            samples.append(current_status)

            is_on = current_status is True or current_status == "on"

            if expected_on and is_on:
                return True, samples

            if not expected_on and not is_on and current_status is not None:
                return True, samples

        except Exception as e:
            samples.append(f"error: {str(e)}")

    return False, samples
