from django.conf.urls import url, include
from django.contrib import admin
from cal import views
from cal import views_users
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/$', obtain_jwt_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^meals/$', views.meal_list),
    url(r'^meals/(?P<pk>[0-9]+)/$', views.meal_detail),
    url(r'^users/$', views_users.user_list),
    url(r'^users/(?P<pk>[0-9]+)/$', views_users.user_detail),
    url(r'^verify/(?P<user_id>[0-9]+)/(?P<verification_code>[0-9a-zA-Z]+)', views_users.verify),
]
