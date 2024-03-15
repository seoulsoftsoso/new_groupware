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
from api.project_mgmt.common import *

from api.user.views import CustomObtainAuthToken
from api.views import *
from api.notice.views import *
from api.board.views import *
from api.reply.views import *
from api.attendance.views import *
from api.corporate_vehicle.views import *
from api.excel.views import *
from api.business.views import *
from api.holiday.views import *
from api.administrator.approval_views import *
from api.administrator.pqy_question_views import *
from api.administrator.user_setting_views import *

from web.views import *

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

TITLE = "서울소프트 그룹웨어 프로젝트"
VERSION = "v0.1"
DESCRIPTION = """


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

                  re_path(r'^data/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),


                  #관리자페이지(그룹웨어)
                  path('admins/index/', admin_index_page, name="adminIndex"),
    
                  #근태관련
                  path('admins/work_schedule/', admin_work_schedule_page.as_view(), name="adminWorkSchedule"),
                  path('admins/workhistory_search', work_history_search.as_view(), name="workHistorySearch"),
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
                  re_path(r'^data/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),

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
                  path('admins/node_info/', GetNodeInfo.as_view(), name="nodeInfo"),


                  #법인차량
                  path('admins/vehicle/', CorporateMgmtListView.as_view(), name="vehicleMain"),
                  path('check-vehicle-availability/', check_vehicle_availability, name="vehicle_availability"), # 법인차량 예약가능 여부체크
                  path('admins/vehicle/edit_data', corporate_edit_data, name="corporateEditFormData"), # Edit Modal 데이터 랜더링
                  path('admins/vehicle/useCheck_add', CorporateMgmtCreateView.as_view(), name="CorporateMgmtCreateView"),


                  #출장관리
                  path('admins/business', business_main_page.as_view(), name="BusinessMain"),
                  path('admins/business/edit_getdata', BusinessEditModal.as_view(), name="businessEditModalData"),

                  #조직도
                  path('admins/organization', organization_page, name='Organization'),

                  # 프로젝트관리
                  path('admins/project_main', project_main_page, name="ProjectMain"),
                  path('admins/project_mgmt', project_mgmt_page, name="ProjectMgmt"),
                  path('admins/task_mgmt/', task_mgmt_page, name="TaskMgmt"),

                  path('project/projectmgmt/', projectmgmtadd.as_view(), name='ProjectAdd'),
                  path('project/projectmgmtedit/', projectmgmtedit.as_view(), name='ProjectEdit'),
                  path('project/protask_edit',ProTaskEdit.as_view(), name="ProTaskEdit"),
                  path('project/taskadd/', taskmgmt.as_view(), name='TaskAdd'),
                  path('porject/taskedit', GetSubDataEdit.as_view(), name='GetSubDataEdit'),
                  #path('project/tasksubadd/', taskmgmt.as_view(), name='TaskSubAdd'),
                  path('project/getsub/', getSubData.as_view(), name='getSubData'),
                  path('project/member_list_get', ProMemberListGet.as_view(), name="ProMemberListGet"),


                  # 주간업무보고
                  path('admins/weekly_report_main', weekly_report_main_page, name="weeklyReportMain"),
                  path('admins/weekly_report_mgmt', weekly_report_mgmt_page, name="weeklyReportMgmt"),


                  # 휴가관리
                  path('admins/holiday_info', holiday_info_page, name="holidayInfo"),
                  path('admins/holiday_check', HolidayCheckView.as_view(), name="HolidayCheckView"),
                  path('admins/holiday_adjustment', HolidayAdjustmentView.as_view(), name="HolidayAdjustmentView"),
                  path('admins/get_adjust_holiday', get_adjust_holiday, name="getAdjustHoliday"),
                  path('admins/create_adjust_holiday', create_adjust_holiday, name="createAdjustHoliday"),
                  path('admins/update_adjust_holiday', update_adjust_holiday, name="updateAdjustHoliday"),
                  path('admins/delete_adjust_holiday', delete_adjust_holiday, name="deleteAdjustHoliday"),


                  # ADMINS
                  # 가입승인/탈퇴
                  path('admins/approval_delete_page', ApprovalDeletePageView.as_view(), name="approvalDeletePage"),
                  path('admins/user_approval', user_approval, name="userApproval"),
                  path('admins/user_resignation', user_resignation, name="userResignation"),
                  path('admins/user_authority_page', user_authority_page, name="userAuthorityPage"),
                  # 견적문의
                  path('admins/pay_question_page', PayQuestionPage.as_view(), name="payQuestionPage"),
                  path('admins/pay_question/detail/<int:question_id>/', PayQuestionDetail.as_view(), name="PayQuestionDetail"),
                  # 내정보 관리
                  path('admins/user_settings_page', UserSettingsPage.as_view(), name="userSettingsPage"),
                  path('admins/change_password', change_password, name="changePassword"),
                  path('admins/signature_img_upload', signature_img_upload, name="signatureImgUpload"),
                  path('admins/testform', test_form, name="testForm"),



                  #메인페이지
                  path('menu/<str:menu_num>/', SubView, name='sub'),
                  path('submit_question/', submit_question, name='submit_question'),

                  path('event/get_event_all/', get_eventDataAll.as_view(), name='get_eventDataAll')

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        # drf yasg
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
