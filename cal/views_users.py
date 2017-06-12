from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from cal.serializers import UserSerializer
from cal.serializers import GroupSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'GET':
        user = request.user
        if len(user.groups.filter(name="admin")) != 1:
            users = User.objects.filter(pk=user.id)
        else:
            users = User.objects.all()

        serializer = UserSerializer(users, many=True, context={"request":request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserViewSet(viewsets.ModelViewSet):
    pagination_class = None
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
