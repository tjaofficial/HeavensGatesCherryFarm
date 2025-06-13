from django.core.management.base import BaseCommand # type: ignore
from django.utils.timezone import now # type: ignore
from ...models import valve_schedule  # adjust path to your app
import requests # type: ignore
import datetime

class Command(BaseCommand):
    help = 'Checks schedule and activates valves'

    def handle(self, *args, **kwargs):
        current_time = now().time()
        current_day = now().strftime('%a').lower()  # 'mon', 'tue', etc.

        schedules = valve_schedule.objects.all()

        for schedule in schedules:
            if current_day not in schedule.get_day_list():
                continue  # skip if not today's day

            # compare times
            if schedule.start_time <= current_time <= schedule.end_time:
                self.activate_valve(schedule.valveIP, True)
            else:
                self.activate_valve(schedule.valveIP, False)

    def activate_valve(self, ip, turn_on):
        try:
            url = f"http://{ip}/rpc/Switch.Set?id=0&on={'true' if turn_on else 'false'}"
            requests.get(url, timeout=3)
            self.stdout.write(self.style.SUCCESS(f"{'ON' if turn_on else 'OFF'} → {ip}"))
        except Exception as e:
            self.stderr.write(f"Error for {ip}: {e}")
