from django.urls import path, include
from dj_rest_auth.urls import urlpatterns as dj_rest_auth_urlpatterns

app_name = 'rest_auth'

urlpatterns = [
    path('', include([url for url in dj_rest_auth_urlpatterns if url.name != 'rest_user_details'])),
    path('registration/', include('dj_rest_auth.registration.urls'))
]
