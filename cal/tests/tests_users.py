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

class UsersTests(TransactionTestCase):
    def test_users(self):
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
        response = client.post("/auth-api/",
                               data=json.dumps({'username': 'test_admin', 'password': 'pass'}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 400, "Email is not verified!")
        admin.profile.verified = True
        admin.profile.save()
        response = client.post("/auth-api/",
                               data=json.dumps({'username': 'test_admin', 'password': 'pass'}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200, "Now we should get the token!")
        tokens["admin"] = json.loads(response.content.decode("UTF-8"), "UTF-8")["token"]

        regular_users = [("user1", "user1"), ("user2", "user2"), ("user3", "user3")]
        for user in regular_users:
            username, password = user
            user_1 = User.objects.create_user(username, username + '@gmail.com', password)
            user_1.is_staff = False
            user_1.save()
            user_1.profile.verified = True
            user_1.profile.save()

            #get the tokens
            response = client.post("/auth-api/",
                                   data=json.dumps({'username': username, 'password': password}),
                                   content_type="application/json")
            self.assertEqual(response.status_code, 200, "We should get the token!")
            tokens[username] = json.loads(response.content.decode("UTF-8"), "UTF-8")["token"]

        # create a user with api
        response = client.post("/users/",
                               data=json.dumps({"username": "test_api_1",
                                                "password": "any_password"}),
                               content_type="application/json")
        #print(json.loads(response.content.decode("UTF-8"), "UTF-8"))
        self.assertEqual(response.status_code, 400, "should reply with 'Email field is required'")
        with self.assertRaises(Exception):
            new_user = User.objects.filter(username="test_api_1")[0]

        response = client.post("/users/",
                               data=json.dumps({"username": "test_api_1",
                                                "password": "pass4",
                                                "email" : "fff@gmail.com"}),
                               content_type="application/json")
        #print(json.loads(response.content.decode("UTF-8"), "UTF-8"))
        self.assertEqual(response.status_code, 400, "should reply with 'Password too short'")
        with self.assertRaises(Exception):
            new_user = User.objects.filter(username="test_api_1")[0]

        response = client.post("/users/",
                               data=json.dumps({"username": "test_api_1",
                                                "password": "passpass",
                                                "email" : "fff@gmail.com"}),
                               content_type="application/json")
        #print(json.loads(response.content.decode("UTF-8"), "UTF-8"))
        self.assertEqual(response.status_code, 201, "user should be created")
        new_user = User.objects.filter(username="test_api_1")[0]

        response = client.post("/auth-api/",
                               data=json.dumps({'username': new_user.username, 'password': "passpass"}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 400, "We should get the error (Email is not verified)!")

        # let's verify it:
        response = client.get("/verify/"+str(new_user.id) + "/" + new_user.profile.verification_code,
                              content_type="application/json")

        # and try again:
        response = client.post("/auth-api/",
                               data=json.dumps({'username': new_user.username, 'password': "passpass"}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200, "Now should be ok")

        # regular user should see only himself
        response = client.get("/users/",
                              HTTP_AUTHORIZATION="JWT " + tokens["user1"],
                              content_type="application/json")
        user_list = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(user_list), 1, "User1 only")

        # now let's make him a manager:
        response = client.put("/users/"+str(User.objects.get(username="user1").id)+"/",
                               HTTP_AUTHORIZATION="JWT " + tokens["user1"],
                               data=json.dumps({"manager":True}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 400, "He should not be able to make himself a manager")

        response = client.put("/users/"+str(User.objects.get(username="user1").id)+"/",
                               HTTP_AUTHORIZATION="JWT " + tokens["admin"],
                               data=json.dumps({"manager":True}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200, "Admin has enough rights for it")

        # and try again:
        response = client.get("/users/",
                              HTTP_AUTHORIZATION="JWT " + tokens["user1"],
                              content_type="application/json")
        user_list = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(user_list), 5, "All five users ")
