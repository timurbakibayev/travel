from rest_framework import serializers
from tp.models import *


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = ('id', 'user', 'destination', 'entry_date', 'start_date', 'end_date')
        read_only_fields = ('id', 'entry_date', 'user')


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'entry_date', 'text', 'trip')
        read_only_fields = ('id', 'entry_date')

