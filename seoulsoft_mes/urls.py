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

from api.auto_complete import Code_108_ac, Code_104_ac, Code_113_ac, Code_112_ac, Code_114_ac, \
    Code_109_ac, Code_110_ac, Code_111_ac, Code_105_ac, Code_106_ac, Code_115_ac, Code_116_ac, Code_118_ac, Code_119_ac, \
    Code_127_ac, Code_128_ac, Gc_name_ac, enterprise_name_ac, client_name_ac, \
    Code_107_ac
from api.base.codemaster_views import CodeMasterViewSet, CodeMasterSelectView
from api.base.codemaster_views_n import CodeMaster_in, CodeMaster_create, CodeMaster_read, CodeMaster_update, \
    CodeMaster_delete

from api.base.enterprise_views import EnterpriseMasterViewSet
from api.base.enterprise_views_n import EnterpriseMaster_in, EnterpriseMaster_create, EnterpriseMaster_read, \
    EnterpriseMaster_update, EnterpriseMaster_delete

from api.base.groupcodemaster_views import GroupCodeMasterViewSet, GenerateCodeMaster

from api.base.user_views import UserMasterViewSet, UserMasterSelectViewSet
from api.calendar.common import get_eventDataAll

from api.user.views import CustomObtainAuthToken
from api.views import *
from api.notice.views import *
from api.board.views import *
from api.reply.views import *
from api.attendance.views import *
from api.corporate_vehicle.views import *
from api.excel.views import *
from web.views import *

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

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

# 기준정보
router.register(r'enterprises', EnterpriseMasterViewSet)
router.register(r'group_codes', GroupCodeMasterViewSet)
router.register(r'generate_codes', GenerateCodeMaster)
router.register(r'codes', CodeMasterViewSet)
router.register(r'codes_select', CodeMasterSelectView)

router.register(r'users', UserMasterViewSet)
router.register(r'users_select', UserMasterSelectViewSet)

custom_obtain_auth_token = CustomObtainAuthToken.as_view()

urlpatterns = [
                  path('', index, name='index'),
                  path('login/', login_page, name="loginPage"),
                  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
                  path('users/login/', custom_obtain_auth_token, name="auth_login"),
                  path('signup/', signup_page, name='signup'),
                  path('check-duplicate/', check_duplicate, name='check_duplicate'),
                  path('users/signup/', UserCreate, name='UserCreate'),


                  #관리자페이지(그룹웨어)
                  path('admins/index/', admin_index_page, name="adminIndex"),
    
                  #근태관련
                  path('admins/work_schedule/', admin_work_schedule_page.as_view(), name="adminWorkSchedule"),
                  path('admins/month_work_schedule/', MonthAttendanceListView.as_view(), name="monthWorkSchedule"),
                  path('check-in/', check_in, name='check_in'),
                  path('check-out/', check_out, name='check_out'),
                  path('last_attendance/', last_attendance, name='last_attendance'),

                  #공지사항
                  path('admins/notice', admin_notice_page, name="adminNotice"),
                  path('admins/notice/write_form', amdin_noticewrite_page, name="noticeWritePage"),
                  path('admins/notice/detail/<int:notice_id>/edit/', admin_noticeEdit_page, name="noticeEdit"),
                  path('admins/notice/detail/<int:notice_id>/', amdin_noticedetail_page, name="noticeDetail"),
                  path('admins/notice/write', admin_noticewrite_add, name="noticeWriteAdd"),
                  path('admins/notice/edit/<int:notice_id>/', admin_noticewrite_edit, name="noticeWriteEdit"),
                  path('admins/notice/delete', admin_notice_delete, name="noticeDelete"),

                  #댓글
                  path('admins/reply_add/', reply_add, name="replyAdd"),

                  #파일첨부
                  path('download/<int:file_id>/', download_File, name='download_file'),
                  path('delete_file/', delete_file, name="delete_file"),
                  path('work_xlsx_download/', excel_download, name="xlsxDownload"),

                  #게시판
                  path('admins/board', amdin_board_page, name="adminBoard"),
                  path('admins/board/write_form', admin_boardwrite_page, name="boardWritePage"),
                  path('admins/board/detail/<int:board_id>/edit/', admin_boardEdit_page, name="boardEdit"),
                  path('admins/board/detail/<int:board_id>/', amdin_boardDetail_page, name="boardDetail"),
                  path('admins/board/<int:id>/', admin_boardList_page, name="boardList"),
                  path('admins/board/write', admin_boardwrite_add, name="boardWriteAdd"),
                  path('admins/board/delete', admin_board_delete, name="boardDelete"),
                  path('admins/board/edit/<int:board_id>/', admin_boardwrite_edit, name="boardWriteEdit"),
                  path('admins/board/group_add', admin_boardGroup_add, name="boardGroupAdd"),
                  path('admins/board/group_edit', admin_boardGroup_edit, name="boardGroupEdit"),
                  path('admins/board/group_delete', admin_boardGroup_delete, name="boardGroupDelete"),
                  path('admins/member_info/', GetMemberInfo.as_view(), name="memberInfo"),


                  #법인차량
                  path('admins/vehicle/', vehicle_main_page, name="vehicleMain"),



                  #메인페이지
                  path('menu/<str:menu_num>/', SubView, name='sub'),
                  path('submit_question/', submit_question, name='submit_question'),

                  path('event/get_event_all/', get_eventDataAll.as_view(), name='get_eventDataAll'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        # drf yasg
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
