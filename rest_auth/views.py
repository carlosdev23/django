from django.views.generic.base import RedirectView


class ConfirmEmailRedirectView(RedirectView):
    query_string = False

    @property
    def url(self):
        key = self.kwargs.get('key')
        return f'https://{self.request.tenant.primary_domain}.dronodat.com/verify-account?key={key}'


class ResetPasswordRedirectView(RedirectView):
    query_string = False

    @property
    def url(self):
        uid = self.kwargs.get('uid')
        token = self.kwargs.get('token')
        return f'https://{self.request.tenant.primary_domain}.dronodat.com/reset-password?uid={uid}&token={token}'
