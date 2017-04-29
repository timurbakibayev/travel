from rest_framework import serializers
from tp.models import *


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ('id', 'destination', 'start_date', 'end_date')


class TripSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    destination =  serializers.CharField(max_length=1000)
    entry_date = serializers.DateField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def create(self, validated_data):
        return Trip.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.destination = validated_data.get('destination', instance.destination)
        instance.entry_date = validated_data.get('entry_date', instance.entry_date)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()
        return instance
