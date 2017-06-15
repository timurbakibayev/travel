from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets
from cal.serializers import UserSerializer
from cal.serializers import GroupSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from cal.models import Profile


def request_post_errors(request):
    err={}
    if "password" in request.data:
        if not isinstance(request.data["password"],str) or len(request.data["password"])<8:
            err["password"] = ["Password should be a string with minimum length 8"]
    if "admin" in request.data and request.data["admin"] not in [0, 1]:
        err["admin"] = ["Should be 0 or 1"]
    if "manager" in request.data and request.data["manager"] not in [0, 1]:
        err["manager"] = ["Should be 0 or 1"]
    if "calories" in request.data:
        if isinstance(request.data["calories"], int):
            cals = request.data["calories"]
            if cals <= 0:
                err["calories"] = ["Number of calories should be greater than zero"]
        else:
            err["calories"] = ["Number of calories should be a positive integer"]
    return err


@api_view(['GET', 'POST'])
def user_list(request):
    try:
        manager = Group.objects.filter(name="manager")[0]
    except IndexError:
        g=Group()
        g.name = "manager"
        g.save()
        manager = g

    try:
        admin = Group.objects.filter(name="admin")[0]
    except IndexError:
        g=Group()
        g.name = "admin"
        g.save()
        admin = g

    if request.method == 'GET':
        user = request.user
        if len(user.groups.filter(name="admin")) != 1:
            users = User.objects.filter(pk=user.id)
        else:
            users = User.objects.all()

        serializer = UserSerializer(users, many=True, context={"request":request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            errors = request_post_errors(request)
            if len(errors) > 0:
                return Response(data=errors,
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            user = User.objects.filter(username=request.data["username"])[0]
            t, created = Profile.objects.get_or_create(pk=user.id, user_id=user.id)
            if "password" in request.data:
                user.set_password(request.data["password"])
                user.save()
            if "admin" in request.data:
                if len(user.groups.filter(name="admin")) == 1 and request.data["admin"] == 0:
                    user.groups.remove(admin)
                if len(user.groups.filter(name="admin")) == 0 and request.data["admin"] == 1:
                    user.groups.add(admin)
                user.save()
            if "manager" in request.data:
                if len(user.groups.filter(name="manager")) == 1 and request.data["manager"] == 0:
                    user.groups.remove(manager)
                if len(user.groups.filter(name="manager")) == 0 and request.data["manager"] == 1:
                    user.groups.add(manager)
                if request.data["manager"] not in [0,1]:
                    errors["manager"] = ["Should be 0 or 1"]
                user.save()
            if "calories" in request.data:
                t.calories = request.data["calories"]
            t.save()
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
        g=Group()
        g.name = "manager"
        g.save()
        manager = g

    try:
        admin = Group.objects.filter(name="admin")[0]
    except IndexError:
        g=Group()
        g.name = "admin"
        g.save()
        admin = g

    user1 = request.user
    if user1 is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if len(user1.groups.filter(name="admin")) != 1 and user != user1:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH' or request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            errors = request_post_errors(request)

            if len(errors) > 0:
                return Response(data=errors,
                                status=status.HTTP_400_BAD_REQUEST)
            print("saving...",errors)
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
                if len(user.groups.filter(name="manager")) == 1 and request.data["manager"] == 0:
                    user.groups.remove(manager)
                elif len(user.groups.filter(name="manager")) == 0 and request.data["manager"] == 1:
                    user.groups.add(manager)
                user.save()
            t,created = Profile.objects.get_or_create(pk=pk, user_id=user.id)
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

        if profile.verification_code == verification_code:
            profile.verified=True
            profile.save()
            context = {"message": "Your Email is successfully verified!",
                       "user": user,
                       "profile": profile}
            return render(request, "verify.html", context)
        context = {"message": "We are sorry, verification code is wrong!",
                   "user": user,
                   "profile": profile}
        return render(request, "verify.html", context)
    except:
        return Response(["Something went wrong!"], status=status.HTTP_400_BAD_REQUEST)