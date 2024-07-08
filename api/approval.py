from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction, DatabaseError
from django.db.models import Q, OuterRef, Subquery, Max
from .models import ApvMaster, ApvComment, ApvSubItem, ApvApprover, ApvCC, ApvCategory, UserMaster, ApvAttachments, ApvReadStatus, NotiCenter
from django import forms
from lib import Pagenation
from datetime import datetime, date
from django.utils import timezone
import base64
import json
from django.core.files.base import ContentFile
from api.holiday.views import HolidayCheckView



class ApvListView(View):

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        # user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=request.user.id)
        _page = request.GET.get('page', '')
        _size = request.GET.get('page_size', '')
        date_sch_from = request.GET.get('date_sch_from', '')
        date_sch_to = request.GET.get('date_sch_to', '')

        # apv_status 삭제는 모두에게 보이지 않도록
        qs = ApvMaster.objects.filter().exclude(apv_status='삭제').order_by('-updated_at', '-doc_no')

        # 사용자의 권한에 따라 필터링
        if user.is_authenticated:
            if user.is_master:  # 마스터유저는 모든 게시물 조회 가능 (추후 필요시 is_superuser로 변경)
                pass

            else:
                # 임시 상태의 문서를 해당 사용자만 볼 수 있도록 필터링, 삭제 상태의 문서를 목록에서 제외
                qs = qs.filter(
                    Q(created_by=user) |
                    ~Q(apv_status='임시')
                ).exclude(apv_status='삭제')

                # 사용자가 생성한 게시물, cc_list에 포함된 게시물, 승인자로 포함된 게시물만 필터링
                qs = qs.filter(
                    Q(created_by=user) |
                    Q(apv_docs_cc__user=user) |
                    Q(apv_docs_approvers__approver1=user) |
                    Q(apv_docs_approvers__approver2=user) |
                    Q(apv_docs_approvers__approver3=user) |
                    Q(apv_docs_approvers__approver4=user) |
                    Q(apv_docs_approvers__approver5=user) |
                    Q(apv_docs_approvers__approver6=user)
                ).distinct()

        else:  # 인증되지 않은 사용자는 아무 게시물도 조회할 수 없음
            qs = qs.none()

        # 사용자가 읽은 게시물 ID 목록, 읽지않음과 결재대기 건수
        read_status = ApvReadStatus.objects.filter(user=user).values_list('document_id', flat=True)
        read_documents = set(read_status)
        unread_docs = qs.exclude(id__in=read_documents).count()
        waiting_docs = qs.filter(id__in=[apv.id for apv in qs if ApvDetail.get_next_approver(apv) == user]).count()

        # 기간 검색
        if date_sch_from:
            qs = qs.filter(updated_at__gte=date_sch_from)

        if date_sch_to:
            qs = qs.filter(updated_at__lte=date_sch_to)

        # 키워드 검색
        apv_all_sch = request.GET.get("apv_all_sch", '')
        if apv_all_sch:
            search_keywords = apv_all_sch.split(',')
            search_conditions = Q()
            for keyword in search_keywords:
                keyword = keyword.strip()
                if keyword:
                    search_condition = (
                        Q(doc_no__icontains=keyword) |
                        Q(doc_title__icontains=keyword) |
                        Q(created_by__username__icontains=keyword) |
                        Q(apv_category__name__icontains=keyword)
                    )
                    search_conditions |= search_condition
            qs = qs.filter(search_conditions)

        # 결재상태 검색
        apv_status_sch = request.GET.get('apv_status_sch', '')
        if apv_status_sch:
            if apv_status_sch == '참조':
                qs = qs.filter(apv_docs_cc__user=user)
            elif apv_status_sch == '내문서':
                qs = qs.filter(created_by_id=user)
            elif apv_status_sch == '결재대기':
                qs = qs.filter(id__in=[apv.id for apv in qs if ApvDetail.get_next_approver(apv) == user])
            elif apv_status_sch == '읽지않음':
                subquery = ApvReadStatus.objects.filter(document=OuterRef('pk'), user=user)
                qs = qs.filter(Q(apv_docs_check__is_read=False, apv_docs_check__user=user) | ~Q(id__in=subquery.values('document')))
            elif apv_status_sch in ['임시', '진행', '완료', '반려']:
                qs = qs.filter(apv_status=apv_status_sch).exclude(apv_docs_cc__user=user)

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

        results = []
        for row in qs_ps:
            cc_list = ApvCC.objects.filter(document=row)
            cc_data = [{
                'user_id': cc.user.id if cc.user else '',
                'username': cc.user.username if cc.user else '',
            } for cc in cc_list]

            comments = ApvComment.objects.filter(document=row)
            comment_data = comments.count()

            result = get_obj(row)
            result['apv_cc'] = cc_data
            result['comment_count'] = comment_data
            result['is_read'] = row.id in read_documents
            if row.apv_status == '진행':
                next_approver = ApvDetail.get_next_approver(row)
                result['next_approver'] = (
                            next_approver.username + ' ' + next_approver.job_position.name) if next_approver else ''
                result['next_approver_id'] = next_approver.id if next_approver else ''
            else:
                result['next_approver'] = ''
                result['next_approver_id'] = ''
            results.append(result)

        context = {
            'count': qs_ps.paginator.count,
            'previous': url_pre,
            'next': url_next,
            'results': results,
            'unread_docs': unread_docs,
            'waiting_docs': waiting_docs,
        }

        return JsonResponse(context, safe=False)



class ApvDetail(View):
    def get(self, request, *args, **kwargs):
        # user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=request.user.id)
        apv_id = request.GET.get('apv_id', '')

        if apv_id:
            apv_master = get_object_or_404(ApvMaster, id=apv_id)

            # 권한 검사: 슈퍼유저, 생성자, CC 리스트에 포함된 사용자, 승인자로 포함된 사용자
            if apv_master.apv_status == '임시':
                is_authorized = user.is_superuser or apv_master.created_by == user
            else:
                is_authorized = (
                        user.is_superuser or
                        apv_master.created_by == user or
                        apv_master.apv_docs_cc.filter(user=user).exists() or
                        apv_master.apv_docs_approvers.filter(
                            Q(approver1=user) |
                            Q(approver2=user) |
                            Q(approver3=user) |
                            Q(approver4=user) |
                            Q(approver5=user) |
                            Q(approver6=user)
                        ).exists()
                )

            if not is_authorized:
                return JsonResponse({'error': 'Forbidden'}, status=403)

            qs = [apv_master]

            # 세부항목 로딩
            sub_items = ApvSubItem.objects.filter(document=apv_master)
            sub_item_data = [{
                'item_no': item.item_no,
                'desc1': item.desc1,
                'desc2': item.desc2,
                'desc3': item.desc3,
                'price': item.price,
                'qty': item.qty,
                'amount': item.amount,
                'remarks': item.remarks,
            } for item in sub_items]

            # approver 로딩
            approvers = ApvApprover.objects.filter(document=apv_master).select_related(
                'approver1', 'approver2', 'approver3', 'approver4', 'approver5', 'approver6'
            )

            approver_data = []
            next_approver = None

            for approver in approvers:
                data = {}
                for i in range(1, 7):
                    approver_obj = getattr(approver, f'approver{i}', None)
                    status = getattr(approver, f'approver{i}_status', None)
                    if approver_obj is not None:
                        data.update({
                            f'approver{i}_id': approver_obj.id,
                            f'approver{i}_name': f"{approver_obj.username} {approver_obj.job_position.name}",
                            f'approver{i}_img': approver_obj.profile_image.url if approver_obj.profile_image else None,
                            f'approver{i}_team': approver_obj.department_position.name,
                            f'approver{i}_status': status,
                            f'approver{i}_date': getattr(approver, f'approver{i}_date', None)
                        })
                    else:
                        data.update({
                            f'approver{i}_id': None,
                            f'approver{i}_name': None,
                            f'approver{i}_img': None,
                            f'approver{i}_team': None,
                            f'approver{i}_status': None,
                            f'approver{i}_date': None
                        })

                    if status == '대기' and next_approver is None:
                        next_approver = approver_obj.id

                approver_data.append(data)

            # cc목록 로딩
            cc_list = ApvCC.objects.filter(document=apv_master)
            cc_data = [{
                'user_id': cc.user.id if cc.user else '',
                'username': cc.user.username + ' ' + cc.user.job_position.name if cc.user else '',
                'departmentName': cc.user.department_position.name if cc.user.department_position.name else '',
                'profile_image': cc.user.profile_image.url if cc.user.profile_image else '',
            } for cc in cc_list]

            # 첨부파일 로딩
            attachments = ApvAttachments.objects.filter(document=apv_master)
            attachment_data = [{
                'file': attachment.file.url,
                'created_at': attachment.created_at,
            } for attachment in attachments]

            # 댓글 로딩
            comments = ApvComment.objects.filter(document=apv_master)
            comment_data = [{
                'id': comment.id,
                'content': comment.content,
                'created_by': {
                    'id': comment.created_by.id,
                    'username': comment.created_by.username + ' ' + comment.created_by.job_position.name,
                    'profile_image': comment.created_by.profile_image.url if comment.created_by.profile_image else '',
                },
                'created_at': comment.created_at,
                'updated_at': comment.updated_at,
            } for comment in comments]

        # 읽음 상태 업데이트
        ApvReadStatus.objects.update_or_create(user=user, document=apv_master, defaults={'is_read': True})

        # 잔여연차 로딩
        holiday_instance = HolidayCheckView()
        holiday_instance.request = request  # request 객체 설정
        leave_balance_queryset = holiday_instance.get_user_holiday()
        leave_balance = list(leave_balance_queryset)  # QuerySet을 리스트로 변환

        results = [get_obj(row) for row in qs]
        for result in results:
            result['leave_balance'] = leave_balance
            result['sub_items'] = sub_item_data
            result['approvers'] = approver_data
            result['apv_cc'] = cc_data
            result['attachments'] = attachment_data
            result['comments'] = comment_data

        context = {
            'results': results,
            'current_user_id': user.id,
            'next_approver': next_approver,
        }

        return JsonResponse(context, safe=False)

    def post(self, request, *args, **kwargs):
        # user_id = request.COOKIES.get("user_id")
        user_id = request.user.id
        if not user_id:
            return JsonResponse({'error': 'User ID not found in cookies'}, status=400)

        user = get_object_or_404(UserMaster, id=user_id)
        apv_id = request.POST.get('apv_id', '')
        if not apv_id:
            return JsonResponse({'error': 'APV ID is required'}, status=400)

        apv_master = get_object_or_404(ApvMaster, id=apv_id)
        approver_action = request.POST.get('approver_action', '')

        # 기안취소
        if approver_action == 'return_temp':
            if apv_master.created_by != user:
                return JsonResponse({'error': '권한이 없습니다.'}, status=403)
            self.reset_approver_status(apv_master)
            apv_master.apv_status = '임시'
            apv_master.save()
            ApvReadStatus.objects.filter(document=apv_master).delete()
            return JsonResponse({'success': 'Status updated to 임시 and all approvals reset to 대기'}, status=200)

        # 승인 버튼을 누른 사용자가 다음 승인자인지 확인
        next_approver = self.get_next_approver(apv_master)
        if next_approver is None:
            return JsonResponse({'error': '잘못된 접근입니다.'}, status=400)

        # 현재 유저가 다음 승인자가 아닌 경우 에러 반환
        if next_approver.id != user.id:
            return JsonResponse({'error': '권한이 없습니다.'}, status=403)

        # 승인을 전달받을때
        if approver_action == 'approve':
            updated = self.update_approver_status(apv_master, user, '승인')
            if not updated:
                return JsonResponse({'error': 'Failed to update status'}, status=500)

            next_approver = self.get_next_approver(apv_master)
            if next_approver is None:
                apv_master.apv_status = '완료'
                apv_master.save(update_fields=['apv_status'])

            return JsonResponse({'success': 'Status updated'}, status=200)

        # 반려를 전달받을때
        elif approver_action == 'reject':
            updated = self.update_approver_status(apv_master, user, '반려')
            if updated:
                apv_master.apv_status = '반려'
                apv_master.save(update_fields=['apv_status'])

            if not updated:
                return JsonResponse({'error': 'Failed to update status'}, status=500)
            return JsonResponse({'success': 'Status updated to 반려'}, status=200)

        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    @staticmethod
    def get_next_approver(apv_master):
        approvers = ApvApprover.objects.filter(document=apv_master)
        for approver in approvers:
            for i in range(1, 7):
                status = getattr(approver, f'approver{i}_status', None)
                approver_obj = getattr(approver, f'approver{i}', None)
                if status == '대기':
                    return approver_obj
        return None

    def update_approver_status(self, apv_master, user, status):
        approvers = ApvApprover.objects.filter(document=apv_master)
        for approver in approvers:
            for i in range(1, 7):
                approver_obj = getattr(approver, f'approver{i}', None)
                if approver_obj == user:
                    setattr(approver, f'approver{i}_status', status)
                    setattr(approver, f'approver{i}_date', timezone.now().date())
                    approver.save()
                    return True
        return False


    def reset_approver_status(self, apv_master):
        approvers = ApvApprover.objects.filter(document=apv_master)
        for approver in approvers:
            for i in range(1, 7):
                setattr(approver, f'approver{i}_status', '대기')
                setattr(approver, f'approver{i}_date', None)
            approver.save()


class ApvCreate(View):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(UserMaster, id=request.user.id)

        # 잔여연차 로딩
        holiday_instance = HolidayCheckView()
        holiday_instance.request = request  # request 객체 설정
        leave_balance_queryset = holiday_instance.get_user_holiday()
        leave_balance = list(leave_balance_queryset)  # QuerySet을 리스트로 변환

        context = {
            'leave_balance': leave_balance,
        }

        return JsonResponse(context, safe=False)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=request.user.id)
        d_today = datetime.today().strftime('%Y-%m-%d')

        doc_no = generate_doc_no()
        apv_category_id = request.POST.get('apv_category_id', '')
        apv_status = request.POST.get('apv_status', '')
        doc_title = request.POST.get('doc_title', '')
        leave_reason = request.POST.get('leave_reason', '')
        period_from = self.get_date_from_string(request.POST.get('period_from', ''))
        period_from_half = request.POST.get('period_from_half', '')
        period_to = self.get_date_from_string(request.POST.get('period_to', ''))
        period_to_half = request.POST.get('period_to_half', '')
        period_count = self.get_float_from_string(request.POST.get('period_count', ''))
        special_comment = request.POST.get('special_comment', '')
        related_project = request.POST.get('related_project', '')
        related_info = request.POST.get('related_info', '')
        payment_method = request.POST.get('payment_method', '')

        approver_ids = [request.POST.get(f'approver{i}', None) for i in range(1, 7)]
        approvers = [get_object_or_404(UserMaster, pk=id) for id in approver_ids if id]

        apv_cc_ids = request.POST.getlist('apv_cc[]', [])
        apv_cc_users = UserMaster.objects.filter(pk__in=apv_cc_ids) if apv_cc_ids else []

        table_data = request.POST.get('table_data', '[]')
        table_data = json.loads(table_data)

        context = {}

        try:
            ApvMaster_obj = ApvMaster.objects.create(
                apv_category_id=apv_category_id,
                apv_status=apv_status,
                doc_no=doc_no,
                doc_title=doc_title,
                leave_reason=leave_reason,
                period_from=period_from,
                period_from_half=period_from_half,
                period_to=period_to,
                period_to_half=period_to_half,
                period_count=period_count,
                special_comment=special_comment,
                related_project=related_project,
                related_info=related_info,
                payment_method=payment_method,
                created_by=user,
                created_at=d_today,
                updated_at=d_today,
            )

            ApvApprover_obj = ApvApprover.objects.create(
                document=ApvMaster_obj,
                **{f'approver{i}': approver for i, approver in enumerate(approvers, start=1)},
                **{f'approver{i}_status': '대기' for i in range(1, len(approvers) + 1)}
            )

            for apv_cc_user in apv_cc_users:
                ApvCC.objects.create(document=ApvMaster_obj, user=apv_cc_user)

            for item in table_data:
                ApvSubItem.objects.create(
                    document=ApvMaster_obj,
                    item_no=item['item_no'],
                    desc1=item['desc1'],
                    desc2=item['desc2'],
                    desc3=item['desc3'],
                    price=item['price'],
                    remarks=item['remarks']
                )

            self.save_attachments(request, ApvMaster_obj)

            # 본인이 작성한 글은 항상 is_read가 True
            ApvReadStatus.objects.create(user=user, document=ApvMaster_obj, is_read=True)

            if ApvMaster_obj:
                context = get_res(context, ApvMaster_obj)
            else:
                msg = "등록 실패했습니다.\n"
                return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            print('Exception 오류 발생')
            print(e)
            msg = "입력한 데이터에 오류가 존재합니다.\n"
            for i in e.args:
                if i == 1062:
                    msg = '중복된 데이터가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)

    @staticmethod
    def get_date_from_string(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        except ValueError:
            return None

    @staticmethod
    def get_float_from_string(float_str):
        try:
            return float(float_str) if float_str else None
        except ValueError:
            return None

    @staticmethod
    def save_attachments(request, apv_master_obj):
        i = 0
        while f'attached_files[{i}][name]' in request.POST:
            file_name = request.POST[f'attached_files[{i}][name]']
            file_content_base64 = request.POST[f'attached_files[{i}][content]']
            file_content = base64.b64decode(file_content_base64)
            file = ContentFile(file_content, name=file_name)
            apv_attachment = ApvAttachments.objects.create(document=apv_master_obj)
            apv_attachment.file.save(file_name, file)
            i += 1


def get_res(context, obj):
    context['id'] = obj.id
    context['apv_category_id'] = obj.apv_category_id
    context['apv_status'] = obj.apv_status
    context['doc_no'] = obj.doc_no
    context['doc_title'] = obj.doc_title
    context['leave_reason'] = obj.leave_reason
    context['period_from'] = obj.period_from
    context['period_from_half'] = obj.period_from_half
    context['period_to'] = obj.period_to
    context['period_to_half'] = obj.period_to_half
    context['period_count'] = obj.period_count
    context['special_comment'] = obj.special_comment
    context['created_by'] = obj.created_by.id
    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at

    return context


def generate_doc_no():
    today = timezone.now().date()
    prefix = f'AP{today.strftime("%y%m%d")}-'

    # 해당 날짜의 가장 큰 번호 찾기
    max_doc_no = ApvMaster.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
        created_at__day=today.day,
        doc_no__startswith=prefix
    ).aggregate(Max('doc_no'))['doc_no__max']

    if max_doc_no:
        # 가장 큰 번호에서 숫자 부분만 추출
        last_count = int(max_doc_no.split('-')[-1])
        count_today = last_count + 1
    else:
        count_today = 1

    doc_no = f'{prefix}{count_today:03d}'
    return doc_no


class ApvUpdate(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        # user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=request.user.id)
        d_today = datetime.today().strftime('%Y-%m-%d')

        # doc_no = request.POST.get('doc_no', '')
        apv_category_id = request.POST.get('apv_category_id', '')
        apv_status = request.POST.get('apv_status', '')
        doc_title = request.POST.get('doc_title', '')
        leave_reason = request.POST.get('leave_reason', '')
        period_from = self.get_date_from_string(request.POST.get('period_from', ''))
        period_from_half = request.POST.get('period_from_half', '')
        period_to = self.get_date_from_string(request.POST.get('period_to', ''))
        period_to_half = request.POST.get('period_to_half', '')
        period_count = self.get_float_from_string(request.POST.get('period_count', ''))
        special_comment = request.POST.get('special_comment', '')
        related_project = request.POST.get('related_project', '')
        related_info = request.POST.get('related_info', '')
        payment_method = request.POST.get('payment_method', '')

        approver_ids = [request.POST.get(f'approver{i}', None) for i in range(1, 7)]
        approvers = [get_object_or_404(UserMaster, pk=id) for id in approver_ids if id]

        apv_cc_ids = request.POST.getlist('apv_cc[]', [])
        apv_cc_users = UserMaster.objects.filter(pk__in=apv_cc_ids) if apv_cc_ids else []

        table_data = request.POST.get('table_data', '[]')
        table_data = json.loads(table_data)

        context = {}

        try:
            obj = get_object_or_404(ApvMaster, pk=int(pk))
            obj.apv_category_id = apv_category_id
            obj.apv_status = apv_status
            # obj.doc_no = doc_no
            obj.doc_title = doc_title
            obj.leave_reason = leave_reason
            obj.period_from = period_from
            obj.period_from_half = period_from_half
            obj.period_to = period_to
            obj.period_to_half = period_to_half
            obj.period_count = period_count
            obj.special_comment = special_comment
            obj.related_project = related_project
            obj.related_info = related_info
            obj.payment_method = payment_method
            obj.created_by = user
            obj.created_at = d_today
            obj.updated_at = d_today

            obj.save()

            ApvApprover.objects.filter(document=obj).delete()
            ApvApprover_obj = ApvApprover.objects.create(document=obj,
                **{f'approver{i}': approver for i, approver in enumerate(approvers, start=1)},
                **{f'approver{i}_status': '대기' for i in range(1, len(approvers) + 1)}
            )
            approver_data = {'document': obj}

            ApvCC.objects.filter(document=obj).delete()
            for apv_cc_user in apv_cc_users:
                ApvCC.objects.update_or_create(
                    document=obj,
                    user=apv_cc_user
                )

            ApvSubItem.objects.filter(document=obj).delete()
            for item in table_data:
                ApvSubItem.objects.create(
                    document=obj,
                    item_no=item['item_no'],
                    desc1=item['desc1'],
                    desc2=item['desc2'],
                    desc3=item['desc3'],
                    price=item['price'],
                    remarks=item['remarks']
                )

            self.save_attachments(request, obj)

            context = get_res(context, obj)

        except Exception as e:
            print('Exception 오류 발생')
            print(e)
            msg = "입력한 데이터에 오류가 존재합니다.\n"
            for i in e.args:
                if i == 1062:
                    msg = '중복된 데이터가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)

    @staticmethod
    def get_date_from_string(date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        except ValueError:
            return None

    @staticmethod
    def get_float_from_string(float_str):
        try:
            return float(float_str) if float_str else None
        except ValueError:
            return None

    @staticmethod
    def save_attachments(request, apv_master_obj):
        i = 0
        while f'attached_files[{i}][name]' in request.POST:
            file_name = request.POST[f'attached_files[{i}][name]']
            file_content_base64 = request.POST[f'attached_files[{i}][content]']
            file_content = base64.b64decode(file_content_base64)
            file = ContentFile(file_content, name=file_name)
            apv_attachment = ApvAttachments.objects.create(document=apv_master_obj)
            apv_attachment.file.save(file_name, file)
            i += 1


class ApvDelete(View):
    @transaction.atomic
    def post(self, request):

        pk = request.POST.get('pk', '')

        if (pk == ''):
            msg = "삭제하시겠습니까?"
            return JsonResponse({'error': True, 'message': msg})

        try:
            obj = ApvMaster.objects.get(pk=int(pk))
            obj.delete()
        except Exception as e:
            print('삭제 실패')
            print(e)
            msg = ["사용중인 데이터 입니다. 관련 데이터 삭제 후 다시 시도해주세요."]
            return JsonResponse({'error': True, 'message': msg})

        context = {}
        context['id'] = pk
        return JsonResponse(context)



def get_obj(obj):
    return {
        'id': obj.id,
        'doc_no': obj.doc_no if obj.doc_no is not None else '',
        'doc_title': obj.doc_title if obj.doc_title is not None else '',
        'apv_category': {
            'id': obj.apv_category.id,
            'name': obj.apv_category.name
        } if obj.apv_category else '',
        'apv_status': obj.apv_status if obj.apv_status is not None else '',
        'created_by': {
            'id': obj.created_by.id,
            'username': obj.created_by.username,
            'department_position': obj.created_by.department_position.name,
            'profile_image': obj.created_by.profile_image.url,
            'job_position': obj.created_by.job_position.name,
        } if obj.created_by else '',
        'created_at': obj.created_at if obj.created_at is not None else '',
        'updated_at': obj.updated_at if obj.updated_at is not None else '',
        'comments_count': obj.comments_count if obj.comments_count else '',
        'views_count': obj.views_count if obj.views_count is not None else '',
        'special_comment': obj.special_comment if obj.special_comment is not None else '',

        'deadline': obj.deadline if obj.deadline is not None else '',
        'payment_method': obj.payment_method if obj.payment_method is not None else '',
        'related_team': obj.related_team if obj.related_team is not None else '',
        'related_project': obj.related_project if obj.related_project is not None else '',
        'related_info': obj.related_info if obj.related_info else '',
        'total_cost': obj.total_cost if obj.total_cost is not None else '',
        'period_from': obj.period_from if obj.period_from is not None else '',
        'period_from_half': obj.period_from_half if obj.period_from_half is not None else '',
        'period_to': obj.period_to if obj.period_to is not None else '',
        'period_to_half': obj.period_to_half if obj.period_to_half is not None else '',
        'period_count': obj.period_count if obj.period_count is not None else '',
        'leave_reason': obj.leave_reason if obj.leave_reason is not None else '',
    }


class ApvStatusUpdate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # user_id = request.COOKIES.get("user_id")
        user = get_object_or_404(UserMaster, id=request.user.id)
        if not user:
            return JsonResponse({'error': 'User not authenticated'}, status=403)

        apv_id = request.POST.get('apv_id')
        new_status = request.POST.get('apv_status')

        if not apv_id or not new_status:
            return JsonResponse({'error': 'Invalid request'}, status=400)

        apv_master = get_object_or_404(ApvMaster, id=apv_id)

        # 권한 검사: 슈퍼유저이거나 생성자이거나 다른 특정 권한이 있는 사용자만 상태 변경 가능
        if not (user.is_superuser or apv_master.created_by == user):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        apv_master.apv_status = new_status
        apv_master.save()

        return JsonResponse({'success': True, 'new_status': apv_master.apv_status})


class ApvCategoryList(View):
    def get(self, request, *args, **kwargs):
        qs = ApvCategory.objects.all().order_by('custom_order')
        categories = list(qs.values('id', 'name', 'desc'))
        return JsonResponse(categories, safe=False)



class ApvCommentCreate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=request.user.id)
        d_today = datetime.today().strftime('%Y-%m-%d')

        document_id = request.POST.get('document', '')
        content = request.POST.get('content', '')

        context = {}

        try:
            document = get_object_or_404(ApvMaster, id=document_id)

            ApvComment_obj = ApvComment.objects.create(
                document=document,
                content=content,
                created_by=user,
                created_at=d_today,
                updated_at=d_today,
            )

            if ApvComment_obj:
                context = get_res_comment(context, ApvComment_obj)
            else:
                msg = "등록 실패했습니다.\n"
                return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            print('Exception 오류 발생')
            print(e)
            msg = "입력한 데이터에 오류가 존재합니다.\n"
            for i in e.args:
                if i == 1062:
                    msg = '중복된 데이터가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


def get_res_comment(context, comment):
    context['id'] = comment.id
    context['document_id'] = comment.document.id
    context['content'] = comment.content
    context['created_by'] = {
        'id': comment.created_by.id,
        'username': comment.created_by.username,
        'profile_image': comment.created_by.profile_image.url if comment.created_by.profile_image else '',
    }
    context['created_at'] = comment.created_at
    context['updated_at'] = comment.updated_at

    return context


class ApvCommentUpdate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=request.user.id)
        d_today = datetime.today().strftime('%Y-%m-%d')

        comment_id = request.POST.get('comment_id', '')
        content = request.POST.get('content', '')

        if not comment_id:
            return JsonResponse({'error': True, 'message': '댓글 ID가 필요합니다.'})

        context = {}

        try:
            comment = get_object_or_404(ApvComment, id=comment_id)

            if comment.created_by != user:
                return JsonResponse({'error': True, 'message': '수정 권한이 없습니다.'})

            comment.content = content
            comment.updated_at = d_today
            comment.save()

            context = get_res_comment(context, comment)

        except Exception as e:
            print('Exception 오류 발생')
            print(e)
            msg = "입력한 데이터에 오류가 존재합니다.\n"
            for i in e.args:
                if i == 1062:
                    msg = '중복된 데이터가 존재합니다.'

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse(context)


class ApvCommentDelete(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=request.user.id)

        comment_id = request.POST.get('comment_id', '')

        if not comment_id:
            return JsonResponse({'error': True, 'message': '댓글 ID가 필요합니다.'})

        try:
            comment = get_object_or_404(ApvComment, id=comment_id)

            if comment.created_by != user:
                return JsonResponse({'error': True, 'message': '삭제 권한이 없습니다.'})

            comment.delete()

            return JsonResponse({'success': True, 'message': '댓글이 삭제되었습니다.'})

        except Exception as e:
            print('Exception 오류 발생')
            print(e)
            return JsonResponse({'error': True, 'message': '댓글 삭제 중 오류가 발생했습니다.'})
