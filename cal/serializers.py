from rest_framework import serializers
from cal.models import Meal
from cal.models import Profile
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

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

    def validate(self, attrs):
        if attrs["calories"] <= 0:
            raise serializers.ValidationError("Number of calories should be positive")
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

    def i_admin(self,user):
        return len(user.groups.filter(name="admin"))

    def i_manager(self,user):
        return len(user.groups.filter(name="manager"))

    def i_verified(self,user):
        the_user = Profile.objects.get(pk=user.id)
        return the_user.verified

    def i_calories(self,user):
        try:
            the_user = Profile.objects.get(pk=user.id)
        except:
            t = Profile()
            t.user = user
            t.id = user.id
            t.save()
            the_user = t
        return the_user.calories


    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'admin', 'manager', 'calories', 'verified')
