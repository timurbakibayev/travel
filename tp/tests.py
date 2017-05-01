from django.test import TestCase
from django.test import Client
import datetime
import json
from .models import *
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
        response = client.get("/")
        self.admin = User.objects.create_user('test_admin', 'admin@test.com', 'pass')
        self.admin.save()
        self.admin.is_staff = True
        self.admin.save()

        # Getting token:
        response = client.post("/auth/",
                               data=json.dumps({'username': 'test_admin', 'password': 'pass'}),
                               content_type="application/json")
        self.assertEqual(response.status_code, 200, "We should get the token!")
        token = json.loads(response.content.decode("UTF-8"), "UTF-8")["token"]
        # Trying to create a new Trip:
        response = client.post("/trips/",
                               data=json.dumps({"destination": "Amsterdam",
                                                "start_date": "2017-04-20",
                                                "end_date": "2017-05-01",
                                                "comment": "too many bicycles"}),
                               content_type="application/json"
                               )
        # this should fail (401) because "Authentication credentials were not provided"
        self.assertEqual(response.status_code, 401, "Authentication credentials were not provided")
        response = client.post("/trips/",
                               data=json.dumps({"destination": "Amsterdam",
                                                "start_date": "2017-04-02",
                                                "end_date": "2017-05-01",
                                                "comment": "too many bicycles"}),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + token)
        self.assertEqual(response.status_code, 201, "The trip should be successfully created")

        for trip in Trip.objects.all():
            some_trip = trip
            self.assertEqual(trip.destination, "Amsterdam")
            self.assertEqual(trip.start_date, datetime.date(2017, 4, 2))
            self.assertEqual(trip.end_date, datetime.date(2017, 5, 1))
            self.assertEqual(trip.comment, "too many bicycles")

        self.assertGreater(len(Trip.objects.all()), 0, "There should be at least one object")

        # Now try API PUT

        response = client.put("/trips/"+str(some_trip.id)+"/",
                               data=json.dumps({"destination": "Paris",
                                                "start_date": "2017-04-02",
                                                "end_date": "2017-05-01",
                                                "comment": "too many tourists"}),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + token)
        self.assertEqual(response.status_code, 200, "The trip should be successfully changed")
        trip = Trip.objects.get(pk=some_trip.id)
        self.assertEqual(trip.destination, "Paris")
        self.assertEqual(trip.start_date, datetime.date(2017, 4, 2))
        self.assertEqual(trip.end_date, datetime.date(2017, 5, 1))
        self.assertEqual(trip.comment, "too many tourists")

