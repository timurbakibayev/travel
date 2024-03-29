from django.utils.datetime_safe import datetime
from rest_framework import serializers
from cal.models import Meal
from cal.models import Invitation
from cal.models import Profile
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ('id', 'email')

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ('id',
                  'user',
                  'date',
                  'time',
                  'text',
                  'calories',
                  )
        read_only_fields = ('id', 'user')

    def validate_calories(self, value):
        if value <= 0:
            raise serializers.ValidationError("Number of calories should be positive")
        return value

    def validate_date(self, value):
        if value > datetime.today().date():
            raise serializers.ValidationError("Cannot be in future")
        return value

    def validate(self, attrs):
        if attrs["date"] == datetime.today().date():
            if attrs["time"] > datetime.today().time():
                raise serializers.ValidationError("Time cannot be in future")
        return attrs


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name',]


class UserSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField("i_admin")
    manager = serializers.SerializerMethodField("i_manager")
    calories = serializers.SerializerMethodField("i_calories")
    verified = serializers.SerializerMethodField("i_verified")
    blocked = serializers.SerializerMethodField("i_blocked")
    consumed = serializers.SerializerMethodField("i_consumed")
    invited = serializers.SerializerMethodField("i_invited")

    def i_admin(self,user):
        return len(user.groups.filter(name="admin")) > 0

    def i_manager(self,user):
        return len(user.groups.filter(name="manager")) > 0

    def i_verified(self,user):
        profile = Profile.objects.get(user=user)
        return profile.verified

    def i_invited(self,user):
        profile = Profile.objects.get(user=user)
        return profile.invited

    def i_blocked(self,user):
        profile = Profile.objects.get(user=user)
        return profile.blocked

    def i_calories(self,user):
        try:
            profile = Profile.objects.get(user=user)
        except:
            t = Profile()
            t.user = user
            t.id = user.id
            t.save()
            profile = t
        return profile.calories

    def i_consumed(self,user):
        c = 0
        for i in Meal.objects.filter(user=user, date=datetime.today()):
            c += i.calories
        return c

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'admin', 'manager',
                  'consumed', 'calories', 'verified', 'blocked', 'invited')
