from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path

from rest_auth.views import ResetPasswordRedirectView, ConfirmEmailRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('account-email-verification-sent/', TemplateView.as_view(), name='account_email_verification_sent', ),
    re_path(r'^password-reset/confirm/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
            ResetPasswordRedirectView.as_view(), name='password_reset_confirm', ),
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailRedirectView.as_view(),
            name='account_confirm_email'),

    re_path(r'^api/v1/', include('rest_auth.urls')),
    re_path(r'^api/v1/', include('users.urls')),
    re_path(r'^api/v1/', include('countries.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
