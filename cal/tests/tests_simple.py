from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.utils.datetime_safe import datetime
from rest_framework_jwt.serializers import User

from cal.models import Meal
from cal.serializers import MealSerializer
from cal.serializers import UserSerializer


class MealTests(TransactionTestCase):
    def test_creating_meals(self):
        user = User()
        user.username = "test"
        user.email = "test@email.com"
        user.save()
        meal = Meal()
        meal.text = "Tomato"
        meal.date = "2017-06-11"
        meal.time = "20:30"
        with self.assertRaises(Exception):
            meal.save()
            #should fail, because no user or calories here
        meal.user = user
        meal.calories = 400
        meal.save()
        self.assertEqual(len(Meal.objects.all()), 1, "A meal should have been created here")

    def test_creating_meals_in_future(self):
        user = User()
        user.username = "test"
        user.email = "test@email.com"
        user.save()
        meal = Meal()
        meal.text = "Tomato"
        meal.date = str(datetime.today().date())
        meal.time = "20:30"
        meal.user = user
        meal.calories = 400
        with self.assertRaises(Exception):
            meal.save()
            #should fail, because no user or calories here
        self.assertEqual(len(Meal.objects.all()), 0, "There should be nothing")

    def test_meal_serializer(self):
        ms = MealSerializer(data={"text": "Bread",
                                  "date": "2017-01-10"})
        self.assertIs(ms.is_valid(), False)
        ms = MealSerializer(data={"text": "Bread",
                                  "date": "2017-01-10",
                                  "time": "02:00",
                                  "calories" : 300})
        self.assertIs(ms.is_valid(), True)

