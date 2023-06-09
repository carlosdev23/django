from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers, exceptions
import rest_framework_simplejwt.serializers

from allauth.utils import email_address_exists
from allauth.account.utils import setup_user_email
from allauth.account.adapter import get_adapter
from allauth.account import app_settings as allauth_settings

from dj_rest_auth.serializers import PasswordResetSerializer as _PasswordResetSerializer
import dj_rest_auth.serializers
import dj_rest_auth.registration.serializers

from clients.utils import is_request_for_dronodat_client

from rest_auth.forms import AllAuthPasswordResetForm


class PasswordResetSerializer(_PasswordResetSerializer):
    password_reset_form_class = AllAuthPasswordResetForm


class LoginSerializer(dj_rest_auth.serializers.LoginSerializer):
    username = None

    def validate(self, attrs):
        attrs = super(LoginSerializer, self).validate(attrs)

        if attrs["user"].client_id != self.context["request"].tenant.id:
            msg = _("Unable to log in with provided credentials.")
            raise exceptions.ValidationError(msg)

        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = (
            "date_joined",
            "is_active",
            "user_permissions",
            "is_superuser",
            "last_login",
            "is_staff",
            "client",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": allauth_settings.EMAIL_REQUIRED},
            "groups": {"required": True},
        }

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."),
                )
        return email

    def save(self, request):
        validated_data = self.validated_data.copy()
        validated_data["is_staff"] = is_request_for_dronodat_client(request)
        validated_data["client"] = request.tenant
        groups = validated_data.pop("groups", [])
        user = get_user_model().objects.create_user(**validated_data)
        user.groups.set(groups)
        setup_user_email(request, user, [])
        return user


class JWTClaimsSerializer(
    rest_framework_simplejwt.serializers.TokenObtainPairSerializer
):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["groups"] = list(user.groups.values("id", "name"))
        return token
