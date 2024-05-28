from django.db.models import F
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth import authenticate, login
from api.models import UserMaster, CodeMaster
from api.serializers import UserMasterSerializer
from rest_framework import status, viewsets
from django.shortcuts import render


# from api.user.authentication import get_expire_time


class CustomObtainAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Token.objects.filter(user=user, created__lt=get_expire_time()).delete()
        token, created = Token.objects.get_or_create(user=user)
        print(token)
        login(request, user)

        return Response({
            'user': UserMasterSerializer(user).data,
            'token': token.key,
            'is_superuser': user.is_superuser
        }, status=status.HTTP_200_OK)
