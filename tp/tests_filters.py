from django.contrib.auth.models import Group
from django.test import TestCase
from django.test import Client
import datetime
import json
from .serializers import *
# Create your tests here.


class FilterTests(TestCase):
    def test_filters(self):
        client = Client()

        # Getting token:
        tokens = {}
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

        client.post("/trips/",
                               data=json.dumps({"destination": "Amsterdam",
                                                "start_date": "2017-04-02",
                                                "end_date": "2017-05-01",
                                                "comment": "too many bicycles"}),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["billgates"])

        client.post("/trips/",
                               data=json.dumps({"destination": "New York",
                                                "start_date": "2017-07-02",
                                                "end_date": "2017-08-01",
                                                "comment": "planning in July"}),
                               content_type="application/json",
                               HTTP_AUTHORIZATION="JWT " + tokens["billgates"])

        some_trip = Trip.objects.filter(destination="Amsterdam")[0]
        # Now try API PUT
        client.put("/trips/"+str(some_trip.id)+"/",
                              data=json.dumps({"destination": "Paris",
                                               "start_date": "2017-04-02",
                                               "end_date": "2017-05-01",
                                               "comment": "too many tourists"}),
                              content_type="application/json",
                              HTTP_AUTHORIZATION="JWT " + tokens["billgates"])

        response = client.get("/trips/?search=paris", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 1, "one trip with Paris")

        response = client.get("/trips/?search=paris tourists", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 1, "one trip with Paris and tourists")

        response = client.get("/trips/?search=paris bicycles", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 0, "one trip with Paris and bicycles")

        response = client.get("/trips/?from=2017-02-25", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 2, "both trips are after Feb, 25")

        response = client.get("/trips/?from=2017-05-15", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 1, "only one trip is after May, 15")

        response = client.get("/trips/?from=2017-09-15", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 0, "no trips after September, 15")

        response = client.get("/trips/?till=2017-02-25", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 0, "no trips before Feb, 25")

        response = client.get("/trips/?till=2017-04-15", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 1, "only one trip is before April, 15")

        response = client.get("/trips/?till=2017-09-15", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 2, "both trips are before September, 15")

        response = client.get("/trips/?from=2017-05-15&till=2017-09-15", HTTP_AUTHORIZATION="JWT " + tokens["billgates"])
        result = json.loads(response.content.decode("UTF-8"), "UTF-8")
        self.assertEqual(len(result), 1, "one trip in that interval")

