from rest_framework import serializers
from cal.models import Meal
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
    gr = GroupSerializer(source='groups', many=True, required=False, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'gr')
