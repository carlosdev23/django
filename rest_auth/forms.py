from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from allauth.account.utils import (
    filter_users_by_email,
    user_pk_to_url_str,
    user_username,
)
from rest_framework import serializers

from allauth.utils import build_absolute_uri
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account import app_settings
from dj_rest_auth.forms import AllAuthPasswordResetForm as _AllAuthPasswordResetForm


class AllAuthPasswordResetForm(_AllAuthPasswordResetForm):
    def save(self, request, **kwargs):
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)

        for user in self.users:
            temp_key = token_generator.make_token(user)
            # send the password reset email
            domain = settings.REACT_URL
            protocol = request.scheme
            client = user.client
            if client.id == 1:
                client = "app"

            # change to use frontend reset password url if needed
            url = f"{protocol}://{client}.{domain}/reset-password/?uid={user_pk_to_url_str(user)}&token={temp_key}"
            context = {
                "current_site": f"{request.scheme}://{get_current_site(request).domain}",
                "user": user,
                "password_reset_url": url,
                "request": request,
            }
            if (
                app_settings.AUTHENTICATION_METHOD
                != app_settings.AuthenticationMethod.EMAIL
            ):
                context["username"] = user_username(user)
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )

        return self.cleaned_data["email"]
