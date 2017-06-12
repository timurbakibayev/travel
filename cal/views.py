from django.shortcuts import render
from django.db.models import Q
from rest_framework.decorators import api_view
from cal.serializers import MealSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from cal.models import Meal

def index(request):
    context = {"message": "Hello, world!"}
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
        # if request.GET.get("from"):
        #     date_from = request.GET.get("from").smeal()
        #     meals = meals.filter(end_date__gte=date_from)
        # if request.GET.get("till"):
        #     date_till = request.GET.get("till").smeal()
        #     meals = meals.filter(start_date__lte=date_till)
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
        serializer = MealSerializer(meal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        meal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
