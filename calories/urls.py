from django.conf.urls import url, include
from django.contrib import admin
from cal import views
from cal import views_users
from cal import views_jwt
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^index$', views.index, name="index"),
    url(r'^login', views.login, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^auth-web/$', views_jwt.auth_web),
    url(r'^auth-api/$', views_jwt.auth_api),
    url(r'^auth-api-default/$', obtain_jwt_token),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^meals/$', views.meal_list),
    url(r'^meals/(?P<pk>[0-9]+)/$', views.meal_detail),
    url(r'^users/$', views_users.user_list),
    url(r'^invitations/$', views_users.invitation_list),
    url(r'^users/(?P<pk>[0-9]+)/$', views_users.user_detail),
    url(r'^users/(?P<username>.+)/send_verification_code/$', views_users.send_code),
    url(r'^verify/(?P<user_id>[0-9]+)/(?P<verification_code>[0-9a-zA-Z]+)$', views_users.verify),
    url(r'^invite/(?P<invitation_id>[0-9]+)/$', views_users.invite),
]
