from rest_framework import serializers
from tp.models import *


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = ('id', 'user', 'destination', 'entry_date', 'start_date', 'end_date', 'comment')
        read_only_fields = ('id', 'entry_date', 'user')

