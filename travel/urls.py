from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from tp import views
from django.conf.urls import url
from django.contrib import admin


# Serializers define the API representation.


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/$', obtain_jwt_token),
    url(r'^auth/verify/$', verify_jwt_token),
    url(r'^auth/refresh/$', refresh_jwt_token),
    url(r'^grant_manager/(?P<pk>[0-9]+)/$', views.grant_manager),
    url(r'^ungrant_manager/(?P<pk>[0-9]+)/$', views.ungrant_manager),
    url(r'^trips/$', views.trip_list),
    url(r'^trips/(?P<pk>[0-9]+)/$', views.trip_detail),
]
