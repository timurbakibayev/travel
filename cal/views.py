from django.shortcuts import render
from django.db.models import Q
from django.utils.datetime_safe import datetime
from rest_framework.decorators import api_view
from cal.serializers import MealSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from cal.models import Meal
from cal.models import Profile

def login(request):
    context = {"message": "Hello, world!"}
    return render(request, "login.html", context)

def index(request):
    context = {"today": datetime.now()}
    return render(request, "index.html", context)

@api_view(['GET', 'POST'])
def meal_list(request):
    if request.method == 'GET':
        user = request.user
        if len(user.groups.filter(name="admin")) != 1:
            meals = Meal.objects.filter(user=user)
        else:
            meals = Meal.objects.all()
        if request.GET.get("search"):
            txt = request.GET.get("search")
            for word in txt.lower().split():
                meals = meals.filter(Q(text__contains=word))
        if request.GET.get("date_from"):
            date_from = request.GET.get("date_from").strip()
            meals = meals.filter(date__gte=date_from)
        if request.GET.get("date_to"):
            date_to = request.GET.get("date_to").strip()
            meals = meals.filter(date__lte=date_to)
        if request.GET.get("time_from"):
            time_from = request.GET.get("time_from").strip()
            meals = meals.filter(time__gte=time_from)
        if request.GET.get("time_to"):
            time_to = request.GET.get("time_to").strip()
            meals = meals.filter(time__lte=time_to)
        serializer = MealSerializer(meals, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MealSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def meal_detail(request, pk):
    try:
        meal = Meal.objects.get(pk=pk)
    except Meal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if len(user.groups.filter(name="admin")) != 1 and meal.user != user:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = MealSerializer(meal)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MealSerializer(meal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        meal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
