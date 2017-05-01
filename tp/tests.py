from django.contrib.auth.models import Group
from django.test import TestCase
from django.test import Client
import datetime
import json
from .serializers import *
# Create your tests here.


class TripTests(TestCase):
    def test_creating_trip(self):
        t = Trip()
        t.destination = "Heidelberg"
        t.start_date = "2017-01-01"
        t.end_date = "2017-04-01"
        t.save()
        self.assertIsNot(t.entry_date, None)

    def test_start_date_later_than_end_date(self):
        t = Trip()
        t.destination = "New York"
        t.start_date = "2017-01-01"
        t.end_date = "2016-12-30"
        t.save()
        self.assertIs(t.id, None)

    def test_serializers(self):
        ts = TripSerializer(data={"destination": "London",
                                  "start_date": "2017-01-10",
                                  "end_date": "2017-01-30"})
        self.assertIs(ts.is_valid(), True)


class ApiTests(TestCase):
    def test_api_auth_and_trip_post(self):
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

        # Trying to create a new Trip:
        response = client.post("/trips/",
                               data=json.dumps({"destination": "Amsterdam",
                                                "start_date": "2017-04-20",
                                                "end_date": "2017-05-01",
                                                "comment": "too many bicycles"}),
                               content_type="application/json"
                               )
        self.assertEqual(response.status_code, 401, "Authentication credentials were not provided")

        response = client.post("/trips/",
                               data=json.dumps({"destination": "Amsterdam",
                                                "start_date": "2017-04-02",
                                                "end_date": "2017-05-01",
                                                "comment": "too many bicycles"}),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        self.assertEqual(response.status_code, 201, "The trip should be successfully created")

        response = client.post("/trips/",
                               data=json.dumps({"destination": "New York",
                                                "start_date": "2017-07-02",
                                                "end_date": "2017-08-01",
                                                "comment": "planning in July"}),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        self.assertEqual(response.status_code, 201, "The trip should be successfully created")

        some_trip = Trip.objects.filter(destination="Amsterdam")[0]
        self.assertEqual(some_trip.destination, "Amsterdam")
        self.assertEqual(some_trip.start_date, datetime.date(2017, 4, 2))
        self.assertEqual(some_trip.end_date, datetime.date(2017, 5, 1))
        self.assertEqual(some_trip.comment, "too many bicycles")

        self.assertGreater(len(Trip.objects.all()), 0, "There should be at least one object")

        # Now try API PUT
        response = client.put("/trips/"+str(some_trip.id)+"/",
                              data=json.dumps({"destination": "Paris",
                                               "start_date": "2017-04-02",
                                               "end_date": "2017-05-01",
                                               "comment": "too many tourists"}),
                              content_type="application/json",
                              HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        self.assertEqual(response.status_code, 200, "The trip should be successfully changed")
        trip = Trip.objects.get(pk=some_trip.id)
        self.assertEqual(trip.destination, "Paris")
        self.assertEqual(trip.start_date, datetime.date(2017, 4, 2))
        self.assertEqual(trip.end_date, datetime.date(2017, 5, 1))
        self.assertEqual(trip.comment, "too many tourists")

        # Now that we have something in our DB, try get some data with GET
        response = client.get("/trips/", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 2, "this user has one record")

        response = client.get("/trips/", HTTP_AUTHORIZATION="JWT " + tokens["stieve"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 0, "this user has no records!")

        response = client.get("/trips/", HTTP_AUTHORIZATION="JWT " + tokens["admin"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), Trip.objects.count(), "admin should see all records!")

        response = client.get("/trips/?search=paris", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 1, "one trip with Paris")

