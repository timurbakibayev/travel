from django.db import models

# Create your models here.
class Trip(models.Model):
    destination =  models.CharField(max_length=1000, verbose_name="Destination")
    entry_date = models.DateField(auto_now=True)
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")

    class Meta:
        ordering = ["start_date"]


class Comment(models.Model):
    trip = models.ForeignKey(Trip)
    entry_date = models.DateField(auto_now=True)
    text = models.CharField(max_length=10000)

    class Meta:
        ordering = ["entry_date"]
