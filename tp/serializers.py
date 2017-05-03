from rest_framework import serializers
from tp.models import *
from django.contrib.auth.models import Group


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ('url', 'id', 'user', 'destination', 'entry_date', 'start_date', 'end_date', 'comment')
        read_only_fields = ('id', 'entry_date', 'user')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')