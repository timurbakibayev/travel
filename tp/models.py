from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Trip(models.Model):
    user = models.ForeignKey(User, null=True)
    destination = models.CharField(max_length=1000, verbose_name="Destination")
    entry_date = models.DateField(auto_now=True)
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")

    def __str__(self):
        return self.destination

    class Meta:
        ordering = ["start_date"]


class Comment(models.Model):
    trip = models.ForeignKey(Trip)
    entry_date = models.DateField(auto_now=True)
    text = models.CharField(max_length=10000)

    def __str__(self):
        return self.text[:30]

    class Meta:
        ordering = ["entry_date"]
