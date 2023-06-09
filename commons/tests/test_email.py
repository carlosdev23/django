from django.test import TestCase
from commons.utils.email import send_email

class EmailTestCase(TestCase):
    def test_send_email(request):

        mail = send_email(
            "subject",
            "projects/email/email_notification_message.html",
            ["to@example.com"],
        )

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "subject"
        assert mail.outbox[0].to == ["to@example.com"]
