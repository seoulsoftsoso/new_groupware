"""seoulsoft_mes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url

from api import views
from api.Item.cost_calculate_views import ItemCostCalculateViewSet
from api.Item.mobile_views import ItemInMobileViewSet
from api.Item.n_item_in_views import Material_input_read
from api.Item.out_order_views import ItemOutOrderViewSet
from api.Item.rein_views import ItemReinViewSet
from api.QRCode.QRCodeManager import QRCodeTestURL
from api.QRCode.RQCodeReceiver import *
from api.auto_complete import Code_108_ac, Customer_name_ac, Code_104_ac, Code_113_ac, Code_112_ac, Code_114_ac, \
    Code_109_ac, Code_110_ac, Code_111_ac, Code_105_ac, Code_106_ac, Code_115_ac, Code_116_ac, Code_118_ac, Code_119_ac, \
    Code_127_ac, Code_128_ac, Oc_name_ac, Gc_name_ac, Customer_code_ac, Item_code_ac, Item_name_ac, Company_division_ac, \
    Item_code_name_ac, Item_nice_number_ac, Item_fee_rate, enterprise_name_ac, client_name_ac, menulist_name_ac, \
    Code_107_ac
from api.base.codemaster_views import CodeMasterViewSet, CodeMasterSelectView
from api.base.codemaster_views_n import CodeMaster_in, CodeMaster_create, CodeMaster_read, CodeMaster_update, \
    CodeMaster_delete
from api.base.customer_excel_views import CustomerExcelView
from api.base.customer_views import CustomerMasterViewSet, CustomerMasterSelectView, CustomerMasterPartView
from api.base.enterprise_views import EnterpriseMasterViewSet
from api.base.enterprise_views_n import EnterpriseMaster_in, EnterpriseMaster_create, EnterpriseMaster_read, \
    EnterpriseMaster_update, EnterpriseMaster_delete
from api.base.facilities_files_views import FacilitiesFilesViewSet
from api.base.facilities_views import FacilitiesMasterViewSet
from api.base.facilities_views_n import FacilitiesMaster_in, FacilitiesMaster_create, FacilitiesMaster_read, \
    FacilitiesMaster_update, FacilitiesMaster_delete
from api.base.groupcodemaster_views import GroupCodeMasterViewSet, GenerateCodeMaster
from api.base.groupcodemaster_views_n import GroupCode_in, GroupCode_create, GroupCode_read, GroupCode_update
from api.base.item_excel_views import ItemExcelView, YuseongItemExcelView
from api.base.item_views_n import ItemMaster_in, ItemMaster_create, ItemMaster_read, ItemMaster_update, \
    ItemMaster_delete, ItemMaster_qr_update
from api.base.menu_view import Menuauth, getSubMenuList, getLmenuList, columnViewSet
from api.base.myinfo_views import MyInfoViewSet
from api.base.customer_views_n import CustomerMaster_in, CustomerMaster_create, CustomerMaster_delete, \
    CustomerMaster_update, CustomerMaster_read, CustomerMaster_excel
from api.base.myinfo_views_n import MyInfoMaster_in, MyInfoMaster_create, MyInfoMaster_read, MyInfoMaster_update, \
    MyInfoMaster_delete
from api.base.order_company import OrderCompanyViewSet
from api.base.order_company_n import OrderCompany_in, OrderCompany_create, OrderCompany_read, OrderCompany_update, \
    OrderCompany_delete
from api.base.unitprice_views import customer_unitprice, UnitPriceSubViewSet, customer_unitprice_update, \
    customer_unitprice_delete
from api.base.user_views import UserMasterViewSet, UserMasterSelectViewSet
from api.base.item_views import ItemMasterViewSet, ItemMasterSelectViewSet, ItemMasterPartViewSet, ItemMasterViewSet5, \
    ItemMasterLedViewSet
from api.base.user_views_n import UserMaster_in, UserMaster_create, UserMaster_read, UserMaster_update, \
    UserMaster_delete
from api.bom.excel_views import BomExcelView
from api.bom.item_views import BomItemViewSet
from api.bom.master_views import BomMasterViewSet, BomMasterSelectViewSet, BomMasterViewSet10
from api.bom.bom_views import BomViewSet, BomSelectViewSet
from api.bom.log_views import BomLogViewSet
from api.Item.calculate_views import ItemCalculateViewSet, ItemCalculateAlertViewSet, ItemCalculateZeroViewSet
from api.Item.in_views import ItemInViewSet
from api.Item.out_views import ItemOutViewSet
from api.Item.adjust_views import ItemAdjustViewSet, ItemMasterAdjustViewSet
from api.cost.CostProduct_views import CostProductViewSet
from api.estimate.estimate_items_views_n import EstimateItems_read, EstimateItems_create, EstimateItems_update
from api.estimate.estimate_views_n import Estimate_read, Estimate_create, Estimate_update, Estimate_in, \
    sendmail_to_company_pdf

from api.log_views import write_log
from api.order.in_views import OrderInViewSet
from api.order.orders_view import OrdersViewSet, OrdersItemsViewSet, OrdersInItemsViewSet
from api.order.views import OrderViewSet
from api.ordering.ordering_items_view_n import OrderingItems_read, OrderingItems_create
from api.ordering.ordering_view_n import Ordering_read, Ordering_create, OrderingAPI
from api.orderpurchase.order_purchase_pay_views import Order_purchase_pay_read, Order_purchase_pay_create, \
    Order_purchase_pay_update, Order_purchase_pay_delete
from api.orderpurchase.order_purchase_views import Order_purchase_read
from api.orderpurchase.order_sales_pay_views import Order_sales_pay_create, Order_sales_pay_read, \
    Order_sales_pay_update, Order_sales_pay_delete
from api.orderpurchase.order_sales_views import Order_sales_read
from api.outsourcing.outsourcing_views import OutsourcingItemViewSet, OutsourcingInItemsViewSet
from api.ordering.ordering_view import OrderingViewSet, OrderingItemsViewSet, OrderingExItemsViewSet, \
    OrderingPartViewSet, OrderingItemsPartViewSet
from api.estimate.estimate_views import EstimateViewSet, EstimateItemsViewSet
from api.process.subprocesstemplet_views import SubprocessTempletViewSet
from api.quality.Rotator_view import RotatorViewSet
from api.quality.Stator_view import StatorViewSet
from api.quality.unbalance_view import UnbalanceViewSet, UnbalanceDetailViewSet
from api.request.request_items_views_n import RequestItems_read, RequestItems_create
from api.request.request_views import RequestViewSet, RequestItemsViewSet
from api.process.management_views import ProcessManagementViewSet, ProcessHasFaultReasonViewSet, ProcessHasFaultReasonSelectViewSet
from api.process.progress_views import SubprocessProgressManagementViewSet
from api.process.sataus_views import ProcessStatusViewSet
from api.process.subprocess_views import SubprocessManagementViewSet, SubprocessManagementAlertViewSet, SubprocessManagementLookupViewSet
from api.process.fault_manage_views import SubprocessFaultManagementViewSet
from api.rental.master_views import RentalMasterViewSet
from api.rental.views import RentalViewSet
from api.request.request_views_n import Request_read, Request_create
from api.sensor.value_views import SensorValueViewSet
from api.sensor.value_views_H2 import SensorH2ValueViewSet
from api.sensor.views import SensorViewSet
from api.sensor.views_H2 import SensorH2ViewSet
from api.production.production import DeviceViewSet
from api.temp_volt_monitoring.value_views import SensorPCValueViewSet, SensorPCValueBPViewSet
from api.temp_volt_monitoring.views import SensorPCViewSet
from api.user.views import CustomObtainAuthToken, MenuHandler
from api.views import *
from api.warehouse.adjust_views import ItemWarehouseAdjustViewSet, ItemMasterWarehouseAdjustViewSet
from api.warehouse.calculate_views import ItemWarehouseCalculateViewSet
from api.warehouse.in_views import ItemWarehouseInViewSet
from api.warehouse.item_views import ItemMasterWarehouseViewSet
from api.warehouse.log_views import ItemWarehouseLogViewSet
from api.warehouse.out_views import ItemWarehouseOutViewSet
from api.warehouse.rein_views import ItemWarehouseReinViewSet


from api.location.location import LocationItemCalculateView

from web.views import *

from django.conf import settings
from django.conf.urls.static import static

TITLE = "서울소프트 MES 프로젝트 API"
VERSION = "v0.1"
DESCRIPTION = """
본 문서는 서울소프트 MES프로젝트에서 사용되는 서버 API 및 이에 대한 model/serializer들을 기술하는 문서입니다.
아래 "Preliminaries" 항목에는 전체적인 API 문서 보는 법을 설명하니 반드시 숙지해주시길 바랍니다.

## Notification
- 현재 기준정보 -> BOM -> 자재 -> 공정 -> 대여 -> ... 순으로 documentation을 진행할 예정입니다. 
- Request 시에 foreign key 형태로 전송할 경우 (e.g. codemaster code) 해당 코드로 전송합니다.
- Response 시에 해당 모델이 foreign key 연결되어있는 경우, nested form으로 연결된 model의 결과물을 함께 출력합니다. 
  - 몇몇 모델에만 적용되어 있으며, 필요한 경우 저에게 연락주시면 바로 수정해드립니다.
  - **꼭, foreign key 연결된 model의 데이터를 다른 endpoint를 호출하여 가져오지 마시고 수정 요청해주시길 바랍니다.**
- 각 모델의 `created_at`, `created_by`, `updated_at`, `updated_by` field는 자동생성되니 함께 request해주지 않아도 됩니다.
- 대부분의 `GET` 함수들은 list (i.e. url이 `resource/` 형식이면서 `GET` method) 형식이고, `GET`과 관련된 중요한 내용들은 여기에\
  기술합니다. retrieve 함수들 (i.e. url이 `resource/{id}` 형식이면서 `GET` method)의 경우 단일 id 항목에 대한 단순히\
  하나의 결과값만 출력합니다.

## Preliminaries

- 본 API 문서의 구성
  - 좌측은 각각의 resource들에 대한 큰 메뉴입니다. 여기에는 customer (고객사), code (코드마스터) \
    등 각각의 큰 리소스들 기반으로 분류되어 있습니다(group_codes 제외). 죄측의 메뉴를 선택하면 아래쪽의 각각의 endpoint들의 설명으로 이동됩니다.
  - 하단의 남색 글씨 (좌측 메뉴를 선택하면 이동되는)는 각각의 resource큰 항목들을 의미합니다. 여기 아래에는 각 resource에 대한 개괄적인 설명이 \
    존재합니다.
  - 각 resource(남색 글씨) 아래에는 각각의 endpoint (bold 체의 조금 작은 검은 글씨)들이 존재하고, 그 밑에는 각각의 대한 설명이 존재합니다.
    - `AUTHORIZATIONS`: 어떤 인증 방식을 사용했는지 설명됩니다. 본 프로젝트에서는 최종적으로 TOKEN방식이 될 예정입니다.
    - `QUERY PARAMETERS`: 각 endpoint에 포함할 질의 변수들입니다. GET method에서 filter 조건을 걸 때 대부분 사용될 것입니다.\
    이는 반드실 URL에 포함되어야 합니다 (즉, 제공해드린 javascript의 .ajax url field).
    - `REQUEST BODY SCHEMA`: POST, DELETE, UPDATE 명령 시에 HTTP BODY에 어떤 값을 포함하여 전송해야하는지를 기술합니다. \
    ajax를 사용하기 때문에 `application/json`과 같은 Content-Type은 신경쓰지 않으셔도 됩니다. 이 항목의 아래쪽에 존재하는 각각의 좌측\
    field와 우측에 value를 넣을지가 중요합니다. 
      - 우측 value의 placeholder는 각각의 field가 어떤 type을 받느냐를 나타내고, 그 바로 뒤 괄호 안에는 간략한 설명이 포함되어 있습니다.
      - 그 뒤의 `[ 1 .. N ]`는 max length가 어느정도인지를 기술합니다.
      - 그 뒤에 Nullable이 붙은 경우에는 null이 가능하므로 같이 전송을 안하면 알아서 null로 들어간다는 의미입니다. 
      - 좌측의 field 아래에 'required'라고 되어있는 부분은 필수로 포함되어야 하는 field들 입니다.
  - 그 아래쪽에는 Response가 존재합니다. 여러분이 request를 날렸을 때 답변으로 받은 response의 형태입니다. `RESPONSE SCHEMA`는 어떤 형태로\
    받을 것인지에 대한 설명이고, syntax는 바로 위 `REQUEST BODY SCHEMA`와 유사합니다. 참고하여야 할 점은 각 SCHEMA 위에 201, 200, 과 같은\
    숫자들이 있습니다. 각 숫자의 의미는 HTTP RESPONSE STAUS 입니다. 러프하게 설명하자면 200류는 성공, 400류는 client 잘못, 500류는 서버 잘못\
    혹은 서버 에러입니다. 500류가 날 경우에는 즉시 저에게 연락주시면 고치도록 하겠습니다.    
- **API endpoint**: 각각의 큰 항목 내의 작은 항목들은 각각의 API endpoint들을 의미합니다. 
  - 즉, 이 각각의 URL이 하나의 API call에 매핑된다고 생각하시면 됩니다.
  - 각각의 resource에 대한 HTTP methods (GET, POST, PATCH, DELETE)로 이루어져 있거나, 관련되어 있는 resource들이 함께 들어가 있습니다.
    - redoc의 한계로 인해 안타깝께도 큰 항목 내의 계층적인 항복을 나눌수가 없습니다. 이부분은 개선이 가능하면 개선후 추가 설명드리겠습니다. 

"""

# drf yasg
schema_view = get_schema_view(
   openapi.Info(
      title=TITLE,
      default_version=VERSION,
      description=DESCRIPTION,
      # terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="grammaright@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   )

#########################
# define router
#########################
router = DefaultRouter()
# BOM
router.register(r'bom/log', BomLogViewSet)
router.register(r'bom/master', BomMasterViewSet)
router.register(r'bom/master10', BomMasterViewSet10)
router.register(r'bom/master_select', BomMasterSelectViewSet)
router.register(r'bom/select', BomSelectViewSet)
router.register(r'bom', BomViewSet)

# materials
router.register(r'items/in', ItemInViewSet)
router.register(r'items/out', ItemOutViewSet)
router.register(r'items/outorder', ItemOutOrderViewSet)
router.register(r'items/rein', ItemReinViewSet)
router.register(r'items/adjust/status', ItemMasterAdjustViewSet)
router.register(r'items/adjust', ItemAdjustViewSet)
router.register(r'items/calculate', ItemCalculateViewSet)
router.register(r'items/calculatezero', ItemCalculateZeroViewSet)
router.register(r'items/calculate_alert', ItemCalculateAlertViewSet)
router.register(r'items/cost/calculate', ItemCostCalculateViewSet)  # 원자재 원가조회
router.register(r'items/mobile', ItemInMobileViewSet)  # 모바일 QR 조회

router.register(r'cost/product/search', CostProductViewSet)

# warehouse(창고관리)
router.register(r'wh/items', ItemMasterWarehouseViewSet)
router.register(r'wh/in', ItemWarehouseInViewSet)
router.register(r'wh/out', ItemWarehouseOutViewSet)
router.register(r'wh/rein', ItemWarehouseReinViewSet)
router.register(r'wh/adjust/status', ItemMasterWarehouseAdjustViewSet)
router.register(r'wh/adjust', ItemWarehouseAdjustViewSet)
router.register(r'wh/calculate', ItemWarehouseCalculateViewSet)
router.register(r'wh/log', ItemWarehouseLogViewSet)
# process
router.register(r'process/sub/progress', SubprocessProgressManagementViewSet)
router.register(r'process/sub', SubprocessManagementViewSet)
router.register(r'process/sub_alert', SubprocessManagementAlertViewSet)
router.register(r'process/sub_lookup', SubprocessManagementLookupViewSet)
router.register(r'process/subtemplet', SubprocessTempletViewSet)
router.register(r'process/status', ProcessStatusViewSet)
router.register(r'process/sub_fault', SubprocessFaultManagementViewSet)
router.register(r'process/has_fault', ProcessHasFaultReasonViewSet)
router.register(r'process/has_fault_select', ProcessHasFaultReasonSelectViewSet)
router.register(r'process', ProcessManagementViewSet)
# rental
router.register(r'rental/master', RentalMasterViewSet)
router.register(r'rental', RentalViewSet)
# sensor
router.register(r'sensors/values', SensorValueViewSet)
router.register(r'sensors', SensorViewSet)
# 온습도 H2_PS T2_EX
router.register(r'sensors_h2/values', SensorH2ValueViewSet)
router.register(r'sensors_h2', SensorH2ViewSet)
router.register(r'production/device', DeviceViewSet)
# sensor pc
router.register(r'sensor_pc/values/add', SensorPCValueBPViewSet)
router.register(r'sensor_pc/values', SensorPCValueViewSet)
router.register(r'sensor_pc', SensorPCViewSet)
# order
router.register(r'orders/in', OrderInViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order_s', OrdersViewSet)  # 발주관리 리뉴얼
router.register(r'order_s_items', OrdersItemsViewSet)  # 발주상세 항목
router.register(r'order_s_in_items', OrdersInItemsViewSet)  # 발주입고 항목
# 외주관리
router.register(r'outsourcings/in', OutsourcingInItemsViewSet)
router.register(r'outsourcings', OutsourcingItemViewSet)
# 기준정보
router.register(r'enterprises', EnterpriseMasterViewSet)
router.register(r'group_codes', GroupCodeMasterViewSet)
router.register(r'generate_codes', GenerateCodeMaster)
router.register(r'codes', CodeMasterViewSet)
router.register(r'codes_select', CodeMasterSelectView)
router.register(r'customers', CustomerMasterViewSet)
router.register(r'customers_select', CustomerMasterSelectView)
router.register(r'customers_part', CustomerMasterPartView)

router.register(r'users', UserMasterViewSet)
router.register(r'users_select', UserMasterSelectViewSet)
router.register(r'items', ItemMasterViewSet)
router.register(r'items5', ItemMasterViewSet5)
router.register(r'items_select', ItemMasterSelectViewSet)
router.register(r'items_part', ItemMasterPartViewSet)
router.register(r'items_led', ItemMasterLedViewSet)

router.register(r'facilities/files', FacilitiesFilesViewSet)       # TODO: 'facilities/<int>/files/' 형태
router.register(r'facilities', FacilitiesMasterViewSet)
router.register(r'order/company', OrderCompanyViewSet)
router.register(r'myinfo', MyInfoViewSet)

router.register(r'unitprice/sub', UnitPriceSubViewSet) #거래처별 단가관리 업체조회, 등록
router.register(r'getMenulist', MenuHandler)  #업체,사용자별 메뉴 조회
router.register(r'basic_information/columnview', columnViewSet)

# 주문관리
router.register(r'ordering_input', OrderingViewSet)
router.register(r'ordering_input_part', OrderingPartViewSet)
router.register(r'ordering_items_input', OrderingItemsViewSet)
router.register(r'ordering_items_input_part', OrderingItemsPartViewSet)
router.register(r'ordering_ex_items_input', OrderingExItemsViewSet)
router.register(r'estimate_input', EstimateViewSet)
router.register(r'estimate_items_input', EstimateItemsViewSet)
router.register(r'request_input', RequestViewSet)
router.register(r'request_items_input', RequestItemsViewSet)

# 품질측정관리
router.register(r'Unbalance', UnbalanceViewSet)
router.register(r'UnbalanceDetail', UnbalanceDetailViewSet)
router.register(r'Rotator', RotatorViewSet)
router.register(r'Stator', StatorViewSet)

custom_obtain_auth_token = CustomObtainAuthToken.as_view()


urlpatterns = [
    path('', index),
    path('users/login/', custom_obtain_auth_token),

    path('menu/<str:menu_num>/', SubView, name='sub'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
    # drf yasg
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

