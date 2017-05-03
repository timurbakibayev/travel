from datetime import date
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Trip(models.Model):
    user = models.ForeignKey(User, default=1, verbose_name="User")
    destination = models.CharField(max_length=1000, verbose_name="Destination")
    entry_date = models.DateField(auto_now=True, verbose_name="Entry Date")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    comment = models.CharField(max_length=10000, null=True, blank=True, verbose_name="Comment")

    def days_left(self):
        today = date.today()
        if today >= self.start_date:
            return 0
        else:
            return (self.start_date - today).days

    def save(self, *args, **kwargs):
        if self.start_date > self.end_date:
            pass
        else:
            super(Trip, self).save(*args, **kwargs)

    def __str__(self):
        return self.destination

    class Meta:
        ordering = ["start_date"]


# TODO: Make user a required field (remove null=True)
