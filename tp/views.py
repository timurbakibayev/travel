from rest_framework.decorators import api_view
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework import viewsets
from tp.serializers import *
from django.db.models import Q


@api_view(['GET', 'POST'])
def trip_list(request):
    if request.method == 'GET':
        user = request.user
        if len(user.groups.filter(name="admin")) != 1:
            trips = Trip.objects.filter(user=user)
        else:
            trips = Trip.objects.all()
        if request.GET.get("search"):
            txt = request.GET.get("search")
            for word in txt.lower().split():
                trips = trips.filter(Q(comment__contains=word) | Q(destination__contains=word))
        if request.GET.get("from"):
            date_from = request.GET.get("from").strip()
            trips = trips.filter(end_date__gte=date_from)
        if request.GET.get("till"):
            date_till = request.GET.get("till").strip()
            trips = trips.filter(start_date__lte=date_till)
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TripSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def trip_detail(request, pk):
    try:
        trip = Trip.objects.get(pk=pk)
    except Trip.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if len(user.groups.filter(name="admin")) != 1 and trip.user != user:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = TripSerializer(trip)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TripSerializer(trip, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        trip.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def travel_plan(request):
    if request.method == 'GET':
        user = request.user
        if user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        trips = Trip.objects.filter(user=user)
        today = date.today()
        next_year = today.year
        next_month = today.month + 1
        if next_month > 12:
            next_month = 1
            next_year += 1
        trips = trips.filter(start_date__gte=date(next_year, next_month, 1))
        next_month = next_month + 1
        if next_month > 12:
            next_month = 1
            next_year += 1
        trips = trips.filter(start_date__lt=date(next_year, next_month, 1))
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)
