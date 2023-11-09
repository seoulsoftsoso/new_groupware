import datetime

from django.db import transaction
from django.db.models import Sum
from django_filters import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from api.pagination import PostPageNumberPagination5
from api.QRCode.QRCodeManager import QRCodeGen



from api.permission import MesPermission


