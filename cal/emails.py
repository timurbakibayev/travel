from django.core.mail import send_mail
from calories import settings

def send_verification_email(profile):
    send_mail(
        'Please, verify your email',
        'Hi '+ profile.user.username +'!\n\nThanks for registering! \n' +
        "Please, verify your email by following this link:\n" +
        profile.verification_link()+"\n\nThank you for your cooperation!",
        settings.EMAIL_HOST_USER,
        [profile.user.email],
        fail_silently=False
    )


def send_invitation_email(invitation):
    send_mail(
        'You are invited to Calories!',
        'Hi! \n\nPlease, continue your registration by providing your username and password: \n' +
        invitation.invitation_link() + "\n\nThank you for your cooperation!",
        settings.EMAIL_HOST_USER,
        [invitation.email],
        fail_silently=False
    )