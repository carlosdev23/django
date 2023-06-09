import os
from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags

my_dict = {
    'site': 'bobbyhadz.com',
    'topic': 'Python'
}
def send_email(
    subject: str,
    template: str,
    recipients: list[str],
    data: dict[str, Any] = {},
):
    """
    This function sends an email using a selected template.
    Arguments:
        subject: the subject of the email
        template: the template to be used for the email
        recipient: a list of recipients the email will be sent to
        data: a dictionary to be added as context variables in the email
    """
    context = data
    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)
    
    mail.send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
        html_message=html_content,
    )

    return mail

