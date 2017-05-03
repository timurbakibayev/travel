from django.test import TestCase
from .serializers import *


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
