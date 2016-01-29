from django.contrib.auth import login
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer
from .models import AppUser
from .permissions import IsAdminOrSameUser

# Create your views here.


class User(generics.GenericAPIView):

    """
        App User signup view.
        * Required fields: email, username, password.
        * Other fields: first_name, last_name, is_staff, is_active, is_subscribed.
          is_staff, is_active, is_subscribed fields have a default value as False.
        * Username and Email must be unique.
        * sample data:
            -{"first_name":"First name", "last_name": "Last Name","email":"email",
              "username": "username", "password": "password", "is_active": "True/False",
              "is_staff": "True/False", "is_subscribed": "True/False"}
        * is_active - True if user is active
        * is_staff - Admin user
        * is_subscribed - Subscribed users (Feature not used currently)
        * Headers:
            - Content-Type: Application/Json
    """

    serializer_class = UserSerializer
    queryset = AppUser.objects.all()

    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            user = user_serializer.data
            del user['password']
            return Response({"status": 1, "user": user})
        return Response({"status": -1, "errors": user_serializer.errors})


class UserLogin(APIView):

    """
        * User login and logout view which returns access token on success.
        * username and password are the required fields.
        * For logout token should be given as: Token <access_token>
        * Login:
            - Data: {"username": "username", "password": "password"}
            - Headers: Content-Type: Application/Json
            - METHOD: POST
        * Logout:
            - Headers:
                Content-Type: Application/Json
                Authorization: Token <token>
            - METHOD: DELETE
    """

    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            login(request, serializer.validated_data['user'])
            token, created = Token.objects.get_or_create(
                user=serializer.validated_data['user'])
            return Response({'status': 1,
                             'token': token.key,
                             'first_name': request.user.first_name,
                             'last_name': request.user.last_name,
                             'username': request.user.username})
        return Response({'status': -1, "error": serializer.errors})

    def delete(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token:
            try:
                # Token should be in form Token <access_token>
                token = token.split()[1]
            except:
                return Response({'status': -1, 'errors': 'Please provide valid token'})    
            try:
                token_obj = get_object_or_404(Token, key=token)
                user = token_obj.user
                user.save()
                token_obj.delete()
            except Http404:
                pass
            return Response({'status': 1, 'token': None})
        else:
            return Response({'status': -1, 'errors': 'Please provide token'})


class UpdateUser(generics.GenericAPIView):

    """
        API to update user
        * User should be logged in to update the user
        * User himself or admin can only update user
        * username, password, email fields are mandatory even if not changed
        * sample data:
            -{"first_name":"First name", "last_name": "Last Name","email":"email",
              "username": "username", "password": "password", "is_active": "True/False",
              "is_staff": "True/False", "is_subscribed": "True/False"}
        * URL: /user/<id>/
        * Method: PUT
        * Delete user:
            - Method: DELETE
    """

    serializer_class = UserSerializer
    queryset = AppUser.objects.all()
    permission_classes = (permissions.IsAuthenticated,
                          IsAdminOrSameUser)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user_instance = self.get_object()
        user_serializer = self.get_serializer(user_instance,
                                              data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            user = user_serializer.data
            del user['password']
            return Response({"status": 1, "user": user})
        return Response({"status": -1, "errors": user_serializer.errors})

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"status": 1})
