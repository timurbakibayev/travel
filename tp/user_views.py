from rest_framework.decorators import api_view
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework import viewsets
from tp.serializers import *
from django.db.models import Q


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        user = self.request.user
        if len(user.groups.filter(name="admin")) > 0 or \
                len(user.groups.filter(name="manager")) > 0 or \
                user.is_superuser:
            queryset_list = User.objects.all().order_by('-date_joined')
        else:
            queryset_list = User.objects.filter(username=user.username).order_by('-date_joined')
        return queryset_list

    def perform_update(self, serializer):
        user = self.request.user
        if len(user.groups.filter(name="admin")) > 0 or \
           len(user.groups.filter(name="manager")) > 0 or \
           user.is_superuser:
            instance = serializer.save()
            return instance


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer

    def get_queryset(self):
        user = self.request.user
        if len(user.groups.filter(name="admin")) > 0 or \
                len(user.groups.filter(name="manager")) > 0 or \
                user.is_superuser:
            queryset_list = Group.objects.all().order_by('name')
        else:
            queryset_list = []
        return queryset_list

    def perform_update(self, serializer):
        user = self.request.user
        if len(user.groups.filter(name="admin")) > 0 or \
           len(user.groups.filter(name="manager")) > 0 or \
           user.is_superuser:
            instance = serializer.save()
            return instance


@api_view(['GET'])
def grant_manager(request, pk):
    try:
        user = User.objects.get(pk=pk)
        manager = Group.objects.filter(name="manager")[0]
    except User.DoesNotExist:
        return Response(status=status.HTTP_204_NO_CONTENT)
    if len(request.user.groups.filter(name="admin")) > 0:
        user.groups.add(manager)
        user.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def ungrant_manager(request, pk):
    try:
        user = User.objects.get(pk=pk)
        manager = Group.objects.filter(name="manager")[0]
    except User.DoesNotExist:
        return Response(status=status.HTTP_204_NO_CONTENT)
    if len(request.user.groups.filter(name="admin")) > 0:
        user.groups.remove(manager)
        user.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
