from django.core import mail
from django_tenants.test.cases import TenantTestCase
from freezegun import freeze_time

from projects.models import Mission, Project
from projects.tests.factories import MissionFactory

@freeze_time("2022-8-10")
class MissionTestCase(TenantTestCase):
    def setUp(self):
        super().setUp()
        self.mission = MissionFactory()

    def test_send_mission_email_notification_14_days(self):
        self.mission.send_mission_email_notification()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Notification: Mission test mission')
        self.assertTrue(self.mission.is_notification_sent)

    @freeze_time("2022-8-24")
    def test_send_mission_email_notification_1_day(self):
        self.mission.send_mission_email_notification()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Reminder: Mission test mission')
        self.assertTrue(self.mission.is_reminder_sent)

    def test_send_mission_email_notification_update(self):
        self.mission.is_notification_sent = True
        self.mission.save()
        self.mission.send_mission_email_notification('update')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Updated: Mission test mission')

    def test_send_mission_email_notification_cancelled(self):
        self.mission.is_notification_sent = True
        self.mission.save()
        self.mission.send_mission_email_notification('delete')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Cancelled: Mission test mission')