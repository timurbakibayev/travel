from rest_framework import serializers
from tp.models import *


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = ('id', 'user', 'destination', 'entry_date', 'start_date', 'end_date')
        # extra_kwargs = {'id': {'required': False}}


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'entry_date', 'text', 'trip')

