from msilib.schema import Error
from time import time
from django.core.management import BaseCommand, CommandError
from django_tenants.utils import tenant_context
from django.utils import timezone

from datetime import date, timedelta

from clients.models import Client
from projects.models import Mission


class Command(BaseCommand):
    help = "Send notification or updates to asset owners about the incoming mission"

    def handle(self, *args, **options):
        try:
            clients = Client.objects.all().exclude(name='public')

            for client in clients:
                with tenant_context(client):
                    missions = Mission.objects.filter(date.today() >= mission.start_date.date() - timedelta(days=14))
                    for mission in missions:
                        mission.send_mission_email_notification()
                        self.stdout.write(f'{timezone.now()} Sent email notification for {mission.name}:'f' {mission.owners}')
        except Exception as e:
            pass