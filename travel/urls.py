from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from tp import views


# Serializers define the API representation.


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)


from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', obtain_jwt_token),
    url(r'^auth/verify/', verify_jwt_token),
    url(r'^auth/refresh/', refresh_jwt_token),
    url(r'^trips/$', views.trip_list),
    url(r'^comments/$', views.comment_list),
    url(r'^comments/(?P<pk>[0-9]+)/$', views.comment_detail),
    url(r'^trips/(?P<pk>[0-9]+)/$', views.trip_detail),
]
