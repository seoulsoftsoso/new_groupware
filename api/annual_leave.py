from threading import Event

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.db import transaction, DatabaseError
from django.db.models import Q, OuterRef, Subquery, Max
from .models import ApvMaster, ApvComment, ApvSubItem, ApvApprover, ApvCC, ApvCategory, UserMaster, ApvAttachments, \
    ApvReadStatus, NotiCenter, EventMaster, CodeMaster, BoardMaster
from lib import Pagenation
from datetime import datetime, date, time
from django.db.models import Sum, F
from django.db.models.functions import TruncYear, TruncMonth
from collections import defaultdict
from django.db.models.functions import ExtractYear, ExtractMonth
from decimal import Decimal


class LeaveManageList(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(UserMaster, id=request.user.id)
        _page = request.GET.get('page', '')
        _size = request.GET.get('page_size', '')
        date_sch_from = request.GET.get('date_sch_from', '')
        date_sch_to = request.GET.get('date_sch_to', '')

        # 연차기록에서 출장(business), 자리비움(personal) 제외
        qs = (
            EventMaster.objects.exclude(event_type__in=['Business', 'Personal'])
            .filter(start_date__gte=datetime(2025, 1, 1))
            .order_by('-start_date')
        )

        # 사용자의 권한에 따라 필터링
        if user.is_authenticated:
            if not user.is_superuser:
                qs = qs.filter(create_by=user)
        else:
            qs = qs.none()

        # 기간 검색
        if date_sch_from:
            qs = qs.filter(start_date__gte=date_sch_from)
        if date_sch_to:
            if isinstance(date_sch_to, str):
                date_sch_to = datetime.strptime(date_sch_to, '%Y-%m-%d').date()
            date_sch_to = datetime.combine(date_sch_to, time(23, 59, 59))
            qs = qs.filter(end_date__lte=date_sch_to)

        # 키워드 검색
        all_sch = request.GET.get("all_sch", '')
        if all_sch:
            search_keywords = all_sch.split(',')
            search_conditions = Q()
            for keyword in search_keywords:
                keyword = keyword.strip()
                if keyword:
                    search_condition = (
                            Q(title__icontains=keyword) |
                            Q(etc__icontains=keyword) |
                            Q(create_by__username__icontains=keyword) |
                            Q(create_by__department_position__name__icontains=keyword) |
                            Q(apv__leave_reason__icontains=keyword) |
                            Q(apv__apv_status__icontains=keyword)
                    )
                    search_conditions |= search_condition
            qs = qs.filter(search_conditions)

        if _page == '' or _size == '':
            results = [get_obj(row) for row in qs]
            context = {'results': results}
            return JsonResponse(context, safe=False)

        # Pagination
        qs_ps = Pagenation(qs, _size, _page)

        pre = int(_page) - 1
        url_pre = "/?page_size=" + _size + "&page=" + str(pre)
        if pre < 1:
            url_pre = None

        next = int(_page) + 1
        url_next = "/?page_size=" + _size + "&page=" + str(next)
        if next > qs_ps.paginator.num_pages:
            url_next = None

        results = [get_obj(row) for row in qs_ps]

        context = {
            'count': qs_ps.paginator.count,
            'previous': url_pre,
            'next': url_next,
            'results': results,
        }

        return JsonResponse(context, safe=False)


def get_obj(obj):
    leave_reason = {
        "연차 추가": "연차 추가",
        "연차 삭감": "연차 삭감"
    }.get(obj.title, obj.apv.leave_reason if obj.apv else '')

    return {
        'id': obj.id,
        'title': obj.title if obj.title is not None else '',
        'period_from': obj.start_date.date() if obj.start_date is not None else '',
        'period_from_datetime': obj.start_date if obj.start_date is not None else '',
        'period_to': obj.end_date.date() if obj.end_date is not None else '',
        'period_to_datetime': obj.end_date if obj.end_date is not None else '',
        'period_count': obj.period_count if obj.period_count is not None else '',
        'description': obj.description,
        'event_type': obj.event_type,
        'leave_reason': leave_reason,
        'apv_id': obj.apv.id if obj.apv is not None else '',
        'apv_status': obj.apv.apv_status if obj.apv is not None else '',
        'apv_category_id': obj.apv.apv_category_id if obj.apv and obj.apv.apv_category else None,
        'etc': obj.etc if obj.etc is not None else '',
        'create_by': {
            'id': obj.create_by.id,
            'username': obj.create_by.username,
            'department_position': obj.create_by.department_position.name,
            'profile_image': obj.create_by.profile_image.url if obj.create_by.profile_image else '',
            'job_position': obj.create_by.job_position.name,
            'signature_file_path': obj.create_by.signature_file_path.url if obj.create_by.signature_file_path else '',
        } if obj.create_by else '',
        'create_at': obj.create_at if obj.create_at is not None else '',
        'update_at': obj.update_at if obj.update_at is not None else '',
    }


class LeaveManageCreate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        event_type = request.POST.get('event_type', '')
        user_id = request.POST.get('user_id', '')
        start_date = request.POST.get('start_date', '')
        period_count = request.POST.get('period_count', '')
        etc = request.POST.get('etc', '')

        d_today = datetime.today().strftime('%Y-%m-%d')  # 오늘날짜

        try:
            with transaction.atomic():
                title = "연차 추가"
                if event_type == "minus":
                    title = "연차 삭감"
                target_user = UserMaster.objects.filter(id=user_id).first()

                create_event = EventMaster.objects.create(
                    url='',
                    title=title,
                    start_date=start_date,
                    end_date=start_date,
                    allDay=0,
                    event_type=event_type,
                    create_by=target_user,
                    updated_by=target_user,
                    delete_flag="Y",
                    period_count=period_count,
                    etc=etc,
                    create_at=d_today,
                    update_at=d_today,
                )

                context = {'result': 'ok'}
                return JsonResponse(context, safe=False)

        except Exception as e:
            transaction.set_rollback(True)
            msg = f"An unexpected error occurred: {str(e)}"
            return JsonResponse({'error': True, 'message': msg})


class LeaveManageUpdate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        obj_id = request.POST.get('pk', '')
        period_count = request.POST.get('period_count', '')
        etc = request.POST.get('etc', '')

        d_today = datetime.today().strftime('%Y-%m-%d')

        try:
            with transaction.atomic():
                obj = EventMaster.objects.get(id=int(obj_id))
                obj.period_count = period_count
                obj.etc = etc
                obj.updated_at = d_today
                obj.save()

                context = {'result': 'ok'}
                return JsonResponse(context, safe=False)

        except Exception as e:
            transaction.set_rollback(True)
            msg = f"An unexpected error occurred: {str(e)}"
            return JsonResponse({'error': True, 'message': msg})


class LeaveManageDelete(View):
    @transaction.atomic
    def post(self, request):
        obj_id = request.POST.get('pk', '')
        if (obj_id == ''):
            return JsonResponse({'error': True, 'message': "삭제할 항목이 선택되지 않았습니다."})

        try:
            with transaction.atomic():
                qs = EventMaster.objects.filter(pk=int(obj_id))
                if qs.exists():
                    obj = qs.first()
                    obj.delete()

                else:
                    return JsonResponse({'error': True, 'message': "삭제할 항목이 존재하지 않습니다."})

        except Exception as e:
            transaction.set_rollback(True)
            msg = f"An unexpected error occurred: {str(e)}"
            return JsonResponse({'error': True, 'message': msg})

        context = {'deleted_obj_id': obj_id}
        return JsonResponse(context)


# 연차통계 부분
class LeaveHistoryList(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        request_user = get_object_or_404(UserMaster, id=request.user.id)
        year_sch = request.GET.get('year_sch', '')
        try:
            year_sch = int(year_sch)
        except (ValueError, TypeError):
            return JsonResponse({'error': '기준연도에 오류가 있습니다.'}, status=400)

        start_date = date(1, 1, 1)  # 모든 데이터를 가져오기 위해 시작 날짜를 초기화
        end_date = date(year_sch + 1, 12, 31)  # 다음 년도까지 데이터 가져오기

        # 출장/자리비움 데이터 제외하기
        qs = (
            EventMaster.objects.exclude(event_type__in=['Business', 'Personal'])
            .filter(start_date__gte=start_date, end_date__lte=end_date)
        )

        # 모든 사용자 가져오기
        all_users = UserMaster.objects.filter(is_staff=True).exclude(etc="no_leave").values_list('username', 'employment_date', 'id').order_by('employment_date')

        # 키워드 검색
        all_sch = request.GET.get("all_sch", '')
        if all_sch:
            search_keywords = all_sch.split(',')
            search_conditions = Q()
            for keyword in search_keywords:
                keyword = keyword.strip()
                if keyword:
                    search_conditions |= Q(username__icontains=keyword)
            all_users = all_users.filter(search_conditions)

        # 사용자의 권한에 따라 필터링
        if request_user.is_authenticated:
            if not request_user.is_superuser:
                # all_users = all_users.filter(department_position_id=request_user.department_position.id)  #부서간에 볼수있도록
                all_users = all_users.filter(id=request_user.id)    #본인것만 볼수있도록
        else:
            qs = qs.none()

        # 사용자 정보와 이벤트 데이터 필터
        user_ids = [user[2] for user in all_users]
        qs = qs.filter(create_by__id__in=user_ids)

        # 모든 이전 데이터 leave_balance 계산
        previous_summary = (
            qs.filter(start_date__lt=date(year_sch, 1, 1))
            .values('create_by__username', 'event_type')
            .annotate(total_period_count=Sum('period_count'))
        )

        user_initial_balances = {user[0]: 0 for user in all_users}
        for row in previous_summary:
            create_by = row['create_by__username']
            if row['event_type'] == 'plus':
                user_initial_balances[create_by] += row['total_period_count'] or 0
            else:
                user_initial_balances[create_by] -= row['total_period_count'] or 0

        # leave_balance 계산 (현재 연도)
        summary = (
            qs.filter(start_date__year=year_sch)
            .annotate(
                year=ExtractYear('start_date'),
                month=ExtractMonth('start_date')
            )
            .values('year', 'month', 'create_by__username', 'event_type')
            .annotate(total_period_count=Sum('period_count'))
            .order_by('create_by__username', 'year', 'month')
        )

        results = {user[0]: {} for user in all_users}
        user_employment_dates = {user[0]: user[1] for user in all_users}

        for row in summary:
            create_by = row['create_by__username']
            year = row['year']
            month = row['month']
            total_period = row['total_period_count'] or 0

            if (year, month) not in results[create_by]:
                results[create_by][(year, month)] = 0
            if row['event_type'] == 'plus':
                results[create_by][(year, month)] += total_period
            else:
                results[create_by][(year, month)] -= total_period

        # 결과 데이터 포맷팅
        formatted_results = []
        next_year_initial_balances = {}

        for create_by, monthly_data in results.items():
            balance = Decimal(user_initial_balances.get(create_by, 0))
            initial_balance = balance  # 초기 값 저장
            details = []

            for month in range(1, 13):
                total_period = monthly_data.get((year_sch, month), 0)

                # 초기 잔여 휴가 포함하여 계산
                balance += Decimal(total_period)

                details.append({
                    'year': year_sch,
                    'month': month,
                    'total_period_count': (f"+{total_period:.1f}" if total_period > 0 else (
                        f"{total_period:.1f}" if total_period != 0 else '0.0')) if total_period != 0 or (
                    year_sch, month) in monthly_data else '',
                    'leave_balance': f"{balance:.1f}",
                    'no_data': total_period == 0 and (year_sch, month) not in monthly_data
                })

            # 현재 연도 잔여값을 내년 초기 값으로 저장
            next_year_initial_balances[create_by] = balance
            today = datetime.today().date()

            formatted_results.append({
                'create_by': create_by,
                'employment_date': user_employment_dates.get(create_by),
                'working_years': (today - user_employment_dates.get(create_by)).days // 365,
                'details': details,
                'leave_balance': f"{balance:.1f}",
                'initial_balance': f"{initial_balance:.1f}"
            })

        # 내년 데이터 처리 시 이월 값 초기화
        for create_by, balance in next_year_initial_balances.items():
            # 잔여값이 None인 경우 기본값 설정
            user_initial_balances = {
                user: next_year_initial_balances.get(user, Decimal(0))
                for user in user_initial_balances
            }

        context = {'summary': formatted_results}
        return JsonResponse(context, safe=False)