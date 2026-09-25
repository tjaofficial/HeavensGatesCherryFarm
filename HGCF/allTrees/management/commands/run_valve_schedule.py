from django.core.management.base import BaseCommand  # type: ignore
from django.utils.timezone import localtime  # type: ignore

from ...models import valve_schedule
from ...utils import (
    publish_valve_command,
    get_irrigation_log_messages,
    add_log_to_area_trees,
)
from ...views.mqtt_pub import get_valve_statuses


MAX_ACTIVE_VALVES = 4


def status_is_on(status):
    return status is True or status == "on"


def schedule_is_active(schedule, current_time):
    """Return True when current_time is inside this schedule's run window.

    Also supports a schedule that crosses midnight, for example 23:00 -> 01:00.
    """
    start = schedule.start_time
    end = schedule.end_time

    if start <= end:
        return start <= current_time < end

    return current_time >= start or current_time < end


class Command(BaseCommand):
    help = "Checks irrigation schedules and activates/deactivates valves"

    def handle(self, *args, **kwargs):
        now = localtime()
        current_time = now.time().replace(second=0, microsecond=0)
        current_day = now.strftime("%a").lower()

        schedules = list(
            valve_schedule.objects
            .select_related("valve")
            .all()
        )

        # Use the actual Shelly output states as the source of truth.
        status_map = get_valve_statuses()
        active_device_ids = {
            device_id
            for device_id, status in status_map.items()
            if status_is_on(status)
        }

        self.stdout.write(
            f"[SCHEDULER] {current_day} {current_time.strftime('%H:%M')} | "
            f"active valves: {len(active_device_ids)}"
        )

        for schedule in schedules:
            valve = schedule.valve
            device_id = valve.valveIP
            scheduled_today = current_day in schedule.get_day_list()
            in_run_window = scheduled_today and schedule_is_active(schedule, current_time)
            is_running = device_id in active_device_ids

            # A manual action owns this valve for the remainder of the current
            # schedule window. Once outside the window, clear the override so the
            # next scheduled run can operate normally.
            if valve.manual_override:
                if not in_run_window:
                    valve.manual_override = False
                    valve.save(update_fields=["manual_override"])
                    self.stdout.write(
                        f"[OVERRIDE CLEARED] {valve.name}"
                    )
                else:
                    self.stdout.write(
                        f"[MANUAL] {valve.name} left unchanged"
                    )
                continue

            if in_run_window:
                if is_running:
                    continue

                if len(active_device_ids) >= MAX_ACTIVE_VALVES:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[LIMIT] {valve.name} not started; "
                            f"{MAX_ACTIVE_VALVES} valves are already ON."
                        )
                    )
                    continue

                publish_valve_command(device_id, True)
                active_device_ids.add(device_id)

                logMessage = get_irrigation_log_messages(
                    "schedule",
                    "start",
                    valve,
                    False,
                )
                add_log_to_area_trees(valve, logMessage, "Irrigation")

                self.stdout.write(
                    self.style.SUCCESS(
                        f"ON -> {valve.name} ({device_id})"
                    )
                )
                continue

            # Outside this schedule's active window, only shut the valve off if
            # it is actually on and is not manually overridden.
            if is_running:
                publish_valve_command(device_id, False)
                active_device_ids.discard(device_id)

                logMessage = get_irrigation_log_messages(
                    "schedule",
                    "stop",
                    valve,
                    False,
                )
                add_log_to_area_trees(valve, logMessage, "Irrigation")

                self.stdout.write(
                    self.style.SUCCESS(
                        f"OFF -> {valve.name} ({device_id})"
                    )
                )
