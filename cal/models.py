from django.db import models
from django.contrib.auth.models import User


class Meal(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    time = models.TimeField()
    text = models.TextField(max_length=1000)
    calories = models.IntegerField()

    def __str__(self):
        return self.text+": " + str(self.calories)

    class Meta:
        ordering = ["date"]
