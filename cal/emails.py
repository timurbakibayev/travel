from django.core.mail import send_mail
from calories import settings


def send_verification_email(profile):
    send_mail(
        'Please, verify your email',
        'Hi '+ profile.user.username +'!\n\nThanks for registering! \n' +
        "Please, verify your email by following this link:\n" +
        profile.verification_link()+"\n\nThank you for cooperation!",
        settings.EMAIL_HOST_USER,
        [profile.user.email],
        fail_silently=False
    )