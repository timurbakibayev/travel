from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from tp import views
from tp import user_views
from django.conf.urls import url
from django.contrib import admin


# Serializers define the API representation.


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', user_views.UserViewSet)
router.register(r'groups', user_views.GroupViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^register/$', user_views.register),
    url(r'^auth/$', obtain_jwt_token),
    url(r'^auth/verify/$', verify_jwt_token),
    url(r'^auth/refresh/$', refresh_jwt_token),
    url(r'^grant_manager/(?P<pk>[0-9]+)/$', user_views.grant_manager),
    url(r'^ungrant_manager/(?P<pk>[0-9]+)/$', user_views.ungrant_manager),
    url(r'^travel_plan/$', views.travel_plan),
    url(r'^trips/$', views.trip_list),
    url(r'^trips/(?P<pk>[0-9]+)/$', views.trip_detail),
]
