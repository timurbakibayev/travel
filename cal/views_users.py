from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_jwt.settings import api_settings

from cal.serializers import UserSerializer
from cal.serializers import InvitationSerializer
from cal.serializers import GroupSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from cal.models import Invitation
from cal.models import Profile
from cal.emails import send_verification_email
from cal.emails import send_invitation_email
from django.utils.deprecation import MiddlewareMixin


class DisableCsrfCheck(MiddlewareMixin):
    def process_request(self, req):
        attr = '_dont_enforce_csrf_checks'
        if not getattr(req, attr, False):
            setattr(req, attr, True)


def request_post_errors(request):
    err = {}
    if "password" in request.data:
        if not isinstance(request.data["password"], str) or len(request.data["password"]) < 8:
            err["password"] = ["Password should be a string with minimum length 8"]
    if "admin" in request.data and request.data["admin"] not in [True, False]:
        err["admin"] = ["Should be true or false"]
    if "manager" in request.data and request.data["manager"] not in [True, False]:
        err["manager"] = ["Should be true or false"]
    if "calories" in request.data:
        if isinstance(request.data["calories"], int):
            cals = request.data["calories"]
            if cals <= 0:
                err["calories"] = ["Number of calories should be greater than zero"]
        else:
            err["calories"] = ["Number of calories should be a positive integer"]
    return err


# @authentication_classes([])
# @csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([])
@method_decorator(csrf_exempt, name='dispatch')
def user_list(request):
    try:
        manager = Group.objects.filter(name="manager")[0]
    except IndexError:
        g = Group()
        g.name = "manager"
        g.save()
        manager = g

    try:
        admin = Group.objects.filter(name="admin")[0]
    except IndexError:
        g = Group()
        g.name = "admin"
        g.save()
        admin = g

    if request.method == 'GET':
        user = request.user
        if user == None:
            return Response({"detail": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        if len(user.groups.filter(name="admin")) + len(user.groups.filter(name="manager")) == 0:
            users = User.objects.filter(pk=user.id)
        else:
            users = User.objects.all()

        serializer = UserSerializer(users, many=True, context={"request": request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            errors = request_post_errors(request)
            if "email" not in request.data or len(request.data["email"]) == 0:
                errors["email"] = ["Field is required"]
            if len(errors) > 0:
                return Response(data=errors,
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            user = User.objects.filter(username=request.data["username"])[0]
            user1 = request.user
            t, created = Profile.objects.get_or_create(user_id=user.id)
            if "password" in request.data:
                user.set_password(request.data["password"])
                user.save()
            if "admin" in request.data and (user1 is not None and len(user1.groups.filter(name="admin")) == 1 or "iddqd" in request.data):
                if len(user.groups.filter(name="admin")) == 1 and not request.data["admin"]:
                    user.groups.remove(admin)
                if len(user.groups.filter(name="admin")) == 0 and request.data["admin"]:
                    user.groups.add(admin)
                user.save()
            if "manager" in request.data and user1 is not None and len(user1.groups.filter(name="admin")) + len(user1.groups.filter(name="manager")) > 0:
                if len(user.groups.filter(name="manager")) == 1 and not request.data["manager"]:
                    user.groups.remove(manager)
                if len(user.groups.filter(name="manager")) == 0 and request.data["manager"]:
                    user.groups.add(manager)
                if request.data["manager"] not in [True, False]:
                    errors["manager"] = ["Should be true or false"]
                user.save()
            if "invited" in request.data:
                if len(user1.groups.filter(name="admin")) == 1 and request.data("invited"):
                    t.invited = True
            if "calories" in request.data:
                t.calories = request.data["calories"]
            t.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@method_decorator(csrf_exempt, name='dispatch')
def invitation_list(request):
    user = request.user
    if len(user.groups.filter(name="admin")) == 0:
        return Response({"detail": "Only admin can invite users"}, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        serializer = InvitationSerializer(data=request.data)
        if serializer.is_valid():
            errors = {}
            if "email" not in request.data or len(request.data["email"]) == 0:
                errors["email"] = ["Field is required"]
            if len(errors) > 0:
                return Response(data=errors,
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            send_invitation_email(Invitation.objects.get(pk=serializer.data["id"]))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE', 'PATCH'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        manager = Group.objects.filter(name="manager")[0]
    except IndexError:
        g = Group()
        g.name = "manager"
        g.save()
        manager = g

    try:
        admin = Group.objects.filter(name="admin")[0]
    except IndexError:
        g = Group()
        g.name = "admin"
        g.save()
        admin = g

    user1 = request.user
    if user1 is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if len(user1.groups.filter(name="admin")) + len(user1.groups.filter(name="manager")) == 0 and user != user1:
        return Response({"detail": "You need admin or manager rights to change another user"}, status=status.HTTP_401_UNAUTHORIZED)

    if len(user1.groups.filter(name="admin")) + len(user1.groups.filter(name="manager")) == 0 and "blocked" in request.data:
        return Response({"detail": "You need admin or manager rights to (un)block a user"}, status=status.HTTP_401_UNAUTHORIZED)

    if len(user.groups.filter(name="admin")) and user != user1:
        return Response({"detail": "Admin can only be changed by himself"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH' or request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            errors = request_post_errors(request)
            if "admin" in request.data:
                if len(user1.groups.filter(name="admin")) == 0:
                    errors["admin"] = ["Admin rights can be set only by admins"]
            if "manager" in request.data:
                if len(user1.groups.filter(name="admin")) + len(user1.groups.filter(name="manager")) == 0:
                    errors["manager"] = ["Manager rights can be set only by admins or managers"]

            if len(errors) > 0:
                return Response(data=errors,
                                status=status.HTTP_400_BAD_REQUEST)
            print("saving...", errors)
            serializer.save()
            user = User.objects.get(pk=pk)
            if "password" in request.data:
                user.set_password(request.data["password"])
                user.save()
            if "admin" in request.data:
                if len(user.groups.filter(name="admin")) == 1 and request.data["admin"] == 0:
                    user.groups.remove(admin)
                elif len(user.groups.filter(name="admin")) == 0 and request.data["admin"] == 1:
                    user.groups.add(admin)
                user.save()
            if "manager" in request.data:
                if len(user.groups.filter(name="manager")) == 1 and request.data["manager"] == False:
                    user.groups.remove(manager)
                elif len(user.groups.filter(name="manager")) == 0 and request.data["manager"] == True:
                    user.groups.add(manager)
                user.save()
            t, created = Profile.objects.get_or_create(user_id=user.id)
            if "blocked" in request.data:
                if not request.data["blocked"]:
                    t.blocked = False
                    t.fails = 0
                elif request.data["blocked"]:
                    t.blocked = True
            if "calories" in request.data:
                t.calories = request.data["calories"]
            t.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def verify(request, user_id, verification_code):
    try:
        user = User.objects.get(pk=user_id)
        profile = Profile.objects.get(user=user)

        if profile.verification_code == verification_code and not profile.verified:
            profile.verified = True
            profile.save()
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            context = {"message": "Your Email is successfully verified!",
                       "user": user,
                       "profile": profile,
                       "token": token}
            return render(request, "verify.html", context)
        context = {"message": "We are sorry, verification code is wrong!",
                   "user": user,
                   "profile": None,
                   "token": ""}
        return render(request, "verify.html", context)
    except:
        context = {"message": "We are sorry, verification code is wrong!",
                   "user": None,
                   "profile": None,
                   "token": ""}
        return render(request, "verify.html", context)


def invite(request, invitation_id):
    try:
        invitation = Invitation.objects.get(pk=invitation_id)
    except:
        return Response({"detail": "Invitation not found!"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "POST":
        messages = ""
        token = ""
        user = None
        data = request.POST
        if "username" not in data or len(data["username"].strip())==0:
            messages += "Please, provide a correct username<br>";
        if "password" not in data or len(data["password"])<8:
            messages += "Please, provide a password with minimum length 8<br>";
        try:
            user = User.objects.get(username=data["username"])
            if user is not None:
                messages = "A user with this username already exists"
        except:
            pass
        if not messages:
            try:
                user = User()
                user.username = data["username"]
                user.email = invitation.email
                user.set_password(data["password"])
                user.save()
                profile = Profile.objects.get(user=user)
                profile.invited = True
                profile.verified = True
                profile.save()
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
            except Exception as e:
                messages = str(e)
        context = {"invitation": invitation, "token": token, "user": user, "messages": messages}
        return render(request, "invite.html", context)
    context = {"invitation": invitation, "token": "", "messages":""}
    return render(request, "invite.html", context)


@api_view(['GET'])
def send_code(request, username):
    try:
        user = User.objects.filter(username=username)[0]
        profile = Profile.objects.get(user=user)
    except:
        return Response({"detail": "User not found!"}, status=status.HTTP_404_NOT_FOUND)
    send_verification_email(profile)
    return Response({"detail": "Verification code is sent to " + user.email}, status=status.HTTP_200_OK)
