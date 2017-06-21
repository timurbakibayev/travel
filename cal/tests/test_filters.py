from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.test import TestCase, TransactionTestCase, Client
from django.db import transaction
from django.utils.datetime_safe import datetime
from rest_framework_jwt.serializers import User

from cal.models import Meal
from cal.serializers import MealSerializer
from cal.serializers import UserSerializer

import json
import datetime

class FiltersTests(TransactionTestCase):
    def test_filters(self):
        client = Client()

        admin_group = Group(name='admin')
        admin_group.save()
        manager_group = Group(name='manager')
        manager_group.save()

        admin = User.objects.create_user('test_admin', 'admin@test.com', 'pass')
        admin.is_staff = True
        admin.groups.add(admin_group)
        admin.groups.add(manager_group)
        admin.save()

        tokens = {}
        admin.profile.verified = True
        admin.profile.save()
        response = client.post("/auth-api/",
                               data=json.dumps({'username': 'test_admin', 'password': 'pass'}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200, "Now we should get the token!")
        tokens["admin"] = json.loads(response.content.decode("UTF-8"), "UTF-8")["token"]

        #add some meal:
        response = client.post("/meals/",
                   data=json.dumps({"text": "Apple",
                                    "date": "2017-04-02",
                                    "time": "15:30",
                                    "calories": 40}),
                   content_type="application/json",
                   HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(response.status_code, 201, "Should be no problem")
        response = client.post("/meals/",
                   data=json.dumps({"text": "Banana",
                                    "date": "2017-04-15",
                                    "time": "15:30",
                                    "calories": 40}),
                   content_type="application/json",
                   HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(response.status_code, 201, "Should be no problem")
        response = client.post("/meals/",
                   data=json.dumps({"text": "Apple",
                                    "date": "2017-04-20",
                                    "time": "16:05",
                                    "calories": 40}),
                   content_type="application/json",
                   HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(response.status_code, 201, "Should be no problem")
        response = client.post("/meals/",
                   data=json.dumps({"text": "Banana",
                                    "date": "2017-04-20",
                                    "time": "17:30",
                                    "calories": 40}),
                   content_type="application/json",
                   HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(response.status_code, 201, "Should be no problem")
        self.assertEqual(len(Meal.objects.all()), 4, "We have added 4 fruits")

        # First no filters:
        response = client.get("/meals/",
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 4, "Now api")

        # Search:
        response = client.get("/meals/?search=potato",
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 0,
                         "No potato here")

        response = client.get("/meals/?search=apple",
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 2,
                         "Two apples")

        response = client.get("/meals/?search=apple&time_from=16:00",
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 1,
                         "One apple after 16:00")


        response = client.get("/meals/?search=apple&date_from=2017-04-16",
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 1,
                         "One apple after 2017-04-16")

        response = client.get("/meals/?date_from=2017-04-16&date_to=2017-04-20",
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 2,
                         "Two fruits between these dates (no search)")


        response = client.get("/meals/?search=apple&time_to=16:00",
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 1,
                         "One apple before 16:00")

        # anyone else should see no fruits at all, let us create some user
        response = client.post("/users/",
                               data=json.dumps({"username": "test_api_1",
                                                "password": "passpass",
                                                "email": "fff@gmail.com"}),
                               content_type="application/json")
        # print(json.loads(response.content.decode("UTF-8"), "UTF-8"))
        self.assertEqual(response.status_code, 201, "user should be created")
        new_user = User.objects.filter(username="test_api_1")[0]
        response = client.get("/verify/" + str(new_user.id) + "/" + new_user.profile.verification_code,
                              content_type="application/json")
        response = client.post("/auth-api/",
                               data=json.dumps({'username': new_user.username, 'password': "passpass"}),
                               content_type="application/json")

        self.assertEqual(response.status_code, 200, "Now should be ok")
        tokens["test_api_1"] = json.loads(response.content.decode("UTF-8"), "UTF-8")["token"]

        response = client.get("/meals/",
                              content_type="application/json",
                              HTTP_AUTHORIZATION="JWT " + tokens["test_api_1"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 0,
                         "Should not see anything")

        # Now let's add a potato for test_api_1:
        response = client.post("/meals/",
                               data=json.dumps({"text": "Banana",
                                                "date": "2017-04-15",
                                                "time": "15:30",
                                                "calories": 40}),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["test_api_1"])
        self.assertEqual(response.status_code, 201, "Should be no problem")

        # and try again:
        response = client.get("/meals/",
                              content_type="application/json",
                              HTTP_AUTHORIZATION="JWT " + tokens["test_api_1"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 1,
                         "Only potato")

        # but admin now sees 5 meals:
        response = client.get("/meals/",
                              content_type="application/json",
                              HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        self.assertEqual(len(json.loads(response.content.decode("UTF-8"), "UTF-8")), 5, "Now api")
