import random

from django.db import models
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.datetime_safe import date

from cal.emails import send_verification_email
from cal.emails import send_invitation_email
from calories import settings

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

    def save(self, *args, **kwargs):
        if str(self.date) > str(datetime.today().date()):
            raise Exception("The date should not be in the future!")
        if str(self.date) == str(datetime.today().date()) and str(self.time) > str(datetime.today().time()):
            raise Exception("The time should not be in the future!")


        super(Meal, self).save(*args, **kwargs)

class Invitation(models.Model):
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.email

    def invitation_link(self):
        print("Invitation link:", settings.GLOBAL_URL + "invite/"+str(self.id)+"/")
        return settings.GLOBAL_URL + "invite/"+str(self.id)+"/"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calories = models.IntegerField(default=1000)
    verification_code = models.CharField(max_length=100, default="111")
    verified = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    fails = models.IntegerField(default=0)
    invited = models.BooleanField(default=False)

    def __str__(self):
        return "profile for " + self.user.username

    def verification_link(self):
        print("Verification link:", settings.GLOBAL_URL + "verify/"+str(self.user.id)+"/"+self.verification_code)
        return settings.GLOBAL_URL + "verify/"+str(self.user.id)+"/"+self.verification_code

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created:
        profile, new = Profile.objects.get_or_create(user=instance)
        #print("Created a user:", profile)
        profile.verification_code = ''.join(random.choice('abc123') for _ in range(10))
        profile.invited = len(instance.email)==0
        profile.verified = profile.invited
        profile.save()
        if not profile.invited:
            try:
                send_verification_email(profile)
            except:
                pass


