from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from KPI.kpi_views import kpi_log
from api.base.base_form import customer_fm
from api.models import CustomerMaster, ItemMaster, UnitPrice
from api.permission import MesPermission
from api.serializers import CustomerMasterSerializer, CustomerMasterSelectSerializer, CustomerMasterPartSerializer, \
    UnitPriceSerializer
from rest_framework.pagination import PageNumberPagination


def customer_unitprice(request):
    try:
        results = ItemMaster.objects.all().filter(enterprise__id=request.COOKIES.get('enterprise_id')).order_by('-id')
        CU = customer_fm(request.GET, request.COOKIES['enterprise_name'])
        context = {}
        context['cu'] = customer_fm(request.GET, request.COOKIES['enterprise_name'])
        context['data'] = results
        data = {
            'data': [{
                'id': re.id,
                'code': re.code,
                'name': re.name,
                'detail': re.detail,
                'model': re.model
            } for re in results]
        }

    except Exception as ex:

        print(ex)

    return render(request, 'basic_information/customer_unitprice.html', context)


class UnitPriceSubViewSet(viewsets.ModelViewSet):
    queryset = UnitPrice.objects.all()
    serializer_class = UnitPriceSerializer
    permission_classes = [IsAuthenticated, MesPermission]
    http_method_names = ['get', 'post', 'patch', 'delete']  # to remove 'put'
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "get_queryset", False)
        return UnitPrice.objects.filter(enterprise_id=self.request.user.enterprise_id, item_id=self.request.query_params.get('item_id')).order_by('-id')

    def list(self, request, *args, **kwargs):
        return super().list(request, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "create", False)
        return super().create(request, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "partial_update", False)
        return super().partial_update(request, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        kpi_log(self.request.user.enterprise, self.request.user.user_id, "UnitPriceSubViewSet", "destroy", False)
        return super().destroy(request, request, *args, **kwargs)
