from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


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


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calories = models.IntegerField(default=1000)
    verification_code = models.CharField(max_length=100, default="111")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return "profile for " + self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a matching profile whenever a user object is created."""
    if created:
        profile, new = Profile.objects.get_or_create(pk=instance.id, user=instance)
        print("Created a user:", profile)
