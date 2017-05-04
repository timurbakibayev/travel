from django.test import TestCase
from django.test import Client
import datetime
import json
from tp.serializers import *


class ApiTests(TestCase):
    def test_api_users(self):
        client = Client()

        admin_group = Group(name='admin')
        admin_group.save()
        manager_group = Group(name='manager')
        manager_group.save()

        admin = User.objects.create_user('test_admin', 'admin@test.com', 'pass')
        admin.is_staff = True
        admin.groups.add(admin_group)
        admin.save()

        # Getting token:
        tokens = {}
        response = client.post("/auth/",
                               data=json.dumps({'username': 'test_admin', 'password': 'pass'}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200, "We should get the token!")
        tokens["admin"] = json.loads(response.content.decode("UTF-8"), "UTF-8")["token"]

        regular_users = [("billgates", "bill"), ("stieve", "st1111"), ("samsung", "samsung12345678")]
        for user in regular_users:
            username, password = user
            self.user_1 = User.objects.create_user(username, username+'@gmail.com', password)
            self.user_1.is_staff = False
            self.user_1.save()
            response = client.post("/auth/",
                                   data=json.dumps({'username': username, 'password': password}),
                                   content_type="application/json")
            self.assertEqual(response.status_code, 200, "We should get the token!")
            tokens[username] = json.loads(response.content.decode("UTF-8"), "UTF-8")["token"]

        # Trying to manage users by admin:
        response = client.post("/users/",
                               data=json.dumps({"username": "test_api_1",
                                                "password": "any_password"}),
                               content_type="application/json")
        new_user = User.objects.filter(username="test_api_1")[0]
        self.assertEqual(response.status_code, 201, "Simple user creation")
        response = client.put("/users/"+str(new_user.id)+"/",
                              data=json.dumps({"username": "test_api_2"}),
                              HTTP_AUTHORIZATION="JWT " + tokens["admin"],
                              content_type="application/json")
        self.assertEqual(response.status_code, 200, "Simple user put")
        response = client.delete("/users/"+str(new_user.id)+"/",
                                 HTTP_AUTHORIZATION="JWT " + tokens["admin"],
                                 content_type="application/json")
        self.assertEqual(response.status_code, 204, "Simple user delete")
        response = client.get("/users/",
                              HTTP_AUTHORIZATION="JWT " + tokens["admin"],
                              content_type="application/json")
        user_list = json.loads(response.content.decode("UTF-8"), "UTF-8")["results"]
        self.assertEqual(len(user_list), 4, "There should be 4 users")

        # ordinary user should not see any users
        response = client.get("/users/",
                              HTTP_AUTHORIZATION="JWT " + tokens["billgates"],
                              content_type="application/json")
        user_list = json.loads(response.content.decode("UTF-8"), "UTF-8")["results"]
        self.assertEqual(len(user_list), 1, "Bill Gates user only")

        a_user = User.objects.filter(username="stieve")[0]
        response = client.put("/users/" + str(a_user.id) + "/",
                              data=json.dumps({"username": "test_api_4"}),
                              HTTP_AUTHORIZATION="JWT " + tokens["billgates"],
                              content_type="application/json")
        self.assertEqual(response.status_code, 404, "Not enough rights to put")

        response = client.get("/groups/",
                              HTTP_AUTHORIZATION="JWT " + tokens["billgates"],
                              content_type="application/json")
        user_list = json.loads(response.content.decode("UTF-8"), "UTF-8")["results"]
        self.assertEqual(len(user_list), 0, "Not enough rights to see group list")

        response = client.get("/groups/",
                              HTTP_AUTHORIZATION="JWT " + tokens["admin"],
                              content_type="application/json")
        user_list = json.loads(response.content.decode("UTF-8"), "UTF-8")["results"]
        self.assertEqual(len(user_list), 2, "But admin or manager may see everything")

        response = client.get("/grant_manager/" + str(a_user.id) + "/",
                              HTTP_AUTHORIZATION="JWT " + tokens["admin"],
                              content_type="application/json")

        response = client.get("/ungrant_manager/" + str(a_user.id) + "/",
                              HTTP_AUTHORIZATION="JWT " + tokens["billgates"],
                              content_type="application/json")
        print(response.status_code)
        print(response.content)





