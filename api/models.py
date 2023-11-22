import datetime

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models
from django.db.models import Model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

"""
This models.py is initially written based on '데이터베이스설계서(유니로보틱스).hwp' of which version 1.0
For the explicit models, I did neither add class nor inherits any custom-made class and used naive models.Model.   
"""


class EnterpriseMaster(models.Model):
    class Meta:
        unique_together = ('code', 'name')

    code = models.CharField(max_length=4, unique=True, verbose_name='업체코드')
    name = models.CharField(max_length=20, unique=True, verbose_name='업체명')
    manage = models.CharField(max_length=20, null=True, verbose_name='관리명')

    # permissions = models.BigIntegerField(verbose_name='권한')
    permissions = models.CharField(max_length=100, verbose_name='권한')


class GroupCodeMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'code')

    # code = models.IntegerField(verbose_name='그룹코드')
    code = models.CharField(max_length=10, verbose_name='그룹코드')
    name = models.CharField(max_length=16, verbose_name='그룹코드 이름')
    enable = models.BooleanField(default=True, verbose_name='사용구분')

    created_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='group_code_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster',
                                   models.SET_NULL, null=True,
                                   related_name='group_code_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='group_code_master_enterprise',
                                   verbose_name='업체')


class CodeMaster(models.Model):
    class Meta:
        unique_together = ('enterprise', 'group', 'code')

    group = models.ForeignKey('GroupCodeMaster', models.PROTECT, related_name='codemaster_group',
                              verbose_name='그룹 코드')
    # code = models.IntegerField(verbose_name='상세 코드')  # 상세 코드
    code = models.CharField(max_length=10, verbose_name='상세 코드')  # 상세 코드
    name = models.CharField(max_length=16, verbose_name='상세 코드명')  # 상세 코드명
    ref_code = models.ForeignKey('CodeMaster',
                                 models.PROTECT,
                                 null=True,
                                 related_name='codemaster_ref_detail_code',
                                 verbose_name='참조 상세코드')
    explain = models.CharField(max_length=32, null=True, verbose_name='코드설명')  # 코드설명
    enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용 구분
    etc = models.CharField(max_length=64, null=True, verbose_name='기타')  # 기 타

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='code_master_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    updated_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='code_master_updated_by',
                                   verbose_name='최종작성자')  # 최종작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_at = models.DateField(auto_now=True, verbose_name='최종작성일')  # 최종작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, related_name='code_master_enterprise',
                                   verbose_name='업체')

    def __str__(self):
        return self.name


class UserMaster(AbstractBaseUser, PermissionsMixin):
    class UserMasterManager(BaseUserManager):

        def usermodel(self, user_id, password, username):
            # Do not add user using this usermodel()
            # This is for bootstrapping function

            user = self.model(user_id=user_id,
                              code="00000000",
                              username=username, )

            user.set_password(password)
            return user

        def create_user(self, user_id, password, username=""):
            user = self.usermodel(user_id, password, username)
            user.save(using=self._db)
            return user

        def create_superuser(self, user_id, password, username=""):
            user = self.usermodel(user_id, password, username)
            user.is_superuser = True
            user.save(using=self._db)

            return user

    class Meta:
        unique_together = ('enterprise', 'code')

    objects = UserMasterManager()
    USERNAME_FIELD = 'user_id'

    user_id = models.CharField(max_length=32, unique=True, verbose_name='유저 ID')
    code = models.CharField(max_length=8, null=True, verbose_name='사번')  # 사번
    username = models.CharField(max_length=26, null=True, verbose_name='유저 이름')
    factory_classification = models.ForeignKey('CodeMaster', models.PROTECT,
                                               null=True,
                                               related_name='factory_classification',
                                               verbose_name='공장구분')  # 공장구분,
    employment_division = models.ForeignKey('CodeMaster', models.PROTECT,
                                            null=True,
                                            related_name='employment_division',
                                            verbose_name='고용구분')  # 고용구분,
    employment_date = models.DateField(null=True, verbose_name='입사일자')  # 입사일자
    job_position = models.ForeignKey('CodeMaster', models.PROTECT,
                                     null=True,
                                     related_name='job_position',
                                     verbose_name='직위')
    department_position = models.ForeignKey('CodeMaster', models.PROTECT,
                                            null=True,
                                            related_name='department_position',
                                            verbose_name='부서구분')
    postal_code = models.CharField(max_length=12, null=True, verbose_name='우편번호')  # 우편번호
    address = models.CharField(max_length=64, null=True, verbose_name='주소')  # 주소
    # enable = models.BooleanField(default=True, verbose_name='사용구분')  # 사용구분
    etc = models.CharField(max_length=36, null=True, verbose_name='기타')  # 기타

    email = models.CharField(max_length=36, null=True, verbose_name='이메일')  #
    tel = models.CharField(max_length=36, null=True, verbose_name='전화번호')  #

    is_master = models.BooleanField(default=False, verbose_name='마스터 아이디')

    # permissions = models.BigIntegerField(default=0, verbose_name='권한')
    # permissions = models.CharField(default='0', max_length=100, verbose_name='권한')

    created_by = models.ForeignKey('UserMaster', models.SET_NULL, null=True, related_name='user_created_by',
                                   verbose_name='최초작성자')  # 최초작성자
    created_at = models.DateField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    enterprise = models.ForeignKey('EnterpriseMaster', models.PROTECT, default=1, related_name='user_master_enterprise',
                                   verbose_name='업체', null=False)

    is_active = models.BooleanField(default=1, verbose_name='활성여부')
    is_staff = models.BooleanField(default=0, verbose_name='사내직원여부')
    last_login = models.DateTimeField(default=timezone.now, verbose_name='마지막로그인')
    useremailreceive = models.BooleanField(default=False)
    userintro = models.TextField(blank=True, null=True)
    # snd_auth = models.CharField(default='00', max_length=128, verbose_name='2차인증')  # 스마트름뱅이 요청


class Question(models.Model):
    Question_type = models.CharField(max_length=1, null=False, verbose_name='문의종류')
    Question_path = models.CharField(max_length=1, null=False, verbose_name='검색경로')
    Question_name = models.CharField(max_length=128, null=False, verbose_name='이름')
    Question_company = models.CharField(max_length=128, null=False, verbose_name='기업(기관)명')
    Question_position = models.CharField(max_length=128, null=False, verbose_name='직책/직급')
    Question_department = models.CharField(max_length=128, null=False, verbose_name='부서명')
    Question_phone = models.CharField(max_length=16, null=False, verbose_name='연락처')
    Question_email = models.CharField(max_length=68, null=False, verbose_name='이메일')
    Question_content = models.TextField(null=False, verbose_name='문의내용')
    Question_date = models.DateTimeField(default=timezone.now, null=False, verbose_name='문의 작성시간')

    def __str__(self):
        return str(self.id)


class BoardMaster(models.Model):
    title = models.CharField(max_length=128, null=False, verbose_name='제목')
    content = models.TextField(null=False, verbose_name='내용')
    file_flag = models.BooleanField(default=False, null=True, verbose_name='파일첨부')  # true:첨부, False:없음
    fixed_flag = models.BooleanField(default=False, null=True, verbose_name='상단공지')  # true:상단공지, False:없음
    temp_flag = models.BooleanField(default=False, null=True, verbose_name='임시저장')  # true:임시저장
    click_cnt = models.IntegerField(default=0, null=False, verbose_name='조회수')
    delete_flag = models.CharField(max_length=1, default='N', null=False, verbose_name='삭제여부') # N: 삭제안함, Y: 삭제

    created_by = models.ForeignKey('UserMaster', models.CASCADE, null=True, related_name='board_user_by',
                                   verbose_name='최초작성자')  # 최초작성자
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_by = models.ForeignKey('UserMaster', models.CASCADE, null=True, related_name='board_up_user_by',
                                   verbose_name='수정자')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='수정일')
    boardcode = models.ForeignKey('CodeMaster', models.CASCADE, related_name='board_code', verbose_name='게시판구분')


class FileBoardMaster(models.Model):
    parent = models.ForeignKey('BoardMaster', models.CASCADE, related_name='board_file_master', verbose_name='파일첨부')
    file_path = models.CharField(max_length=128, null=False)
    created_by = models.ForeignKey('UserMaster', models.CASCADE, null=True, related_name='file_user_by',
                                   verbose_name='최초작성자')  # 최초작성자
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_by = models.ForeignKey('UserMaster', models.CASCADE, null=True, related_name='file_up_user_by',
                                   verbose_name='수정자')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='수정일')
    delete_flag = models.CharField(max_length=1, default='N', null=False, verbose_name='삭제여부')  # N: 삭제안함, Y: 삭제


class ReplyMaster(models.Model):
    parent = models.ForeignKey('BoardMaster', models.CASCADE, related_name='reply_board', verbose_name='상위게시판')
    reply = models.TextField(null=False, verbose_name='내용')
    created_by = models.ForeignKey('UserMaster', models.CASCADE, null=True, related_name='reply_user_by',
                                   verbose_name='최초작성자')  # 최초작성자
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='최초작성일')  # 최초작성일
    updated_by = models.ForeignKey('UserMaster', models.CASCADE, null=True, related_name='reply_up_user_by',
                                   verbose_name='수정자')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='수정일')
    delete_flag = models.CharField(max_length=1, default='N', null=False, verbose_name='삭제여부')  # N: 삭제안함, Y: 삭제
