from django.core.management.base import BaseCommand # type: ignore
from django.utils.timezone import localtime # type: ignore
from ...models import valve_schedule, valve_registration  # adjust path to your app
from ...utils import publish_valve_command, get_irrigation_log_messages, add_log_to_area_trees

class Command(BaseCommand):
    help = 'Checks schedule and activates valves'

    def handle(self, *args, **kwargs):
        current_time = localtime().time()
        current_day = localtime().strftime('%a').lower()  # 'mon', 'tue', etc.
        print("WHat the hell is hoing on")
        schedules = valve_schedule.objects.all()
        allValves = valve_registration.objects.all()

        for schedule in schedules:
            self.stdout.write(f"[DEBUG] Schedule for valve {schedule.valve}: days={schedule.get_day_list()}, start={schedule.start_time}, end={schedule.end_time}")
            self.stdout.write(f"[DEBUG] Now: {current_day}, {current_time}")

            if current_day not in schedule.get_day_list():
                continue  # skip if not today's day

            # compare times
            self.stdout.write(f"[DEBUG] Comparing: {schedule.start_time} <= {current_time} <= {schedule.end_time}")

            valve = schedule.valve

            if valve.manual_override:
                if current_time == schedule.end_time:
                    for val in allValves:
                        val.manual_override = False
                        val.save()
                print(f"[SKIP] Manual override is active for valve {valve}")
                continue
            if schedule.start_time <= current_time <= schedule.end_time:
                for val in allValves:
                    if valve.valveIP == val.valveIP:
                        publish_valve_command(valve.valveIP, True)
                        logMessage = get_irrigation_log_messages('schedule', 'start', valve, False)
                        add_log_to_area_trees(valve, logMessage, 'Irrigation')
                        self.stdout.write(self.style.SUCCESS(f"ON → {valve.valveIP}"))
                    else:
                        publish_valve_command(valve.valveIP, False)
                        logMessage = get_irrigation_log_messages('schedule', 'stop', valve, False)
                        add_log_to_area_trees(valve, logMessage, 'Irrigation')
                        self.stdout.write(self.style.SUCCESS(f"OFF → {valve.valveIP}"))
                        val.manual_override = False
                        val.save()
            else:
                publish_valve_command(valve.valveIP, False)
                logMessage = get_irrigation_log_messages('schedule', 'stop', valve, False)
                add_log_to_area_trees(valve, logMessage, 'Irrigation')
                self.stdout.write(self.style.SUCCESS(f"OFF → {valve.valveIP}"))
            
