from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction, DatabaseError
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import ApvMaster, ApvComment, ApvSubItem, ApvApprover, ApvCC, ApvCategory, UserMaster, ApvAttachments
from django import forms
from lib import Pagenation
from datetime import datetime, date
import base64
from django.core.files.base import ContentFile



class ApvListView(View):

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '')
        _size = request.GET.get('page_size', '')
        date_sch_from = request.GET.get('date_sch_from', '')
        date_sch_to = request.GET.get('date_sch_to', '')

        qs = ApvMaster.objects.filter().order_by('-updated_at')

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
        if apv_status_sch and apv_status_sch != '전체':
            qs = qs.filter(apv_status=apv_status_sch)

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
            'results': results
        }

        return JsonResponse(context, safe=False)



class ApvDetail(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        apv_id = request.GET.get('apv_id', '')
        if apv_id:
            apv_master = ApvMaster.objects.get(id=apv_id)
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
            approvers = ApvApprover.objects.filter(document=apv_master)
            approver_data = []
            for approver in approvers:
                approver_data.append({
                    'approver1_id': approver.approver1.id if approver.approver1 is not None else None,
                    'approver1_name': approver.approver1.username if approver.approver1 is not None else None,
                    'approver1_team': approver.approver1.department_position.name if approver.approver1 is not None else None,
                    'approver1_status': approver.approver1_status,
                    'approver1_date': approver.approver1_date,
                    'approver2_id': approver.approver2.id if approver.approver2 is not None else None,
                    'approver2_name': approver.approver2.username if approver.approver2 is not None else None,
                    'approver2_team': approver.approver1.department_position.name if approver.approver2 is not None else None,
                    'approver2_status': approver.approver2_status,
                    'approver2_date': approver.approver2_date,
                    'approver3_id': approver.approver3.id if approver.approver3 is not None else None,
                    'approver3_name': approver.approver3.username if approver.approver3 is not None else None,
                    'approver3_team': approver.approver1.department_position.name if approver.approver3 is not None else None,
                    'approver3_status': approver.approver3_status,
                    'approver3_date': approver.approver3_date,
                    'approver4_id': approver.approver4.id if approver.approver4 is not None else None,
                    'approver4_name': approver.approver4.username if approver.approver4 is not None else None,
                    'approver4_team': approver.approver1.department_position.name if approver.approver4 is not None else None,
                    'approver4_status': approver.approver4_status,
                    'approver4_date': approver.approver4_date,
                    'approver5_id': approver.approver5.id if approver.approver5 is not None else None,
                    'approver5_name': approver.approver5.username if approver.approver5 is not None else None,
                    'approver5_team': approver.approver1.department_position.name if approver.approver5 is not None else None,
                    'approver5_status': approver.approver5_status,
                    'approver5_date': approver.approver5_date,
                    'approver6_id': approver.approver6.id if approver.approver6 is not None else None,
                    'approver6_name': approver.approver6.username if approver.approver6 is not None else None,
                    'approver6_team': approver.approver1.department_position.name if approver.approver6 is not None else None,
                    'approver6_status': approver.approver6_status,
                    'approver6_date': approver.approver6_date,
                })

            # cc목록 로딩
            cc_list = ApvCC.objects.filter(document=apv_master)
            cc_data = [{
                'user_id': cc.user.id if cc.user else '',
                'username': cc.user.username if cc.user else '',
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
                'content': comment.content,
                'created_by': {
                    'id': comment.created_by.id,
                    'username': comment.created_by.username,
                },
                'created_at': comment.created_at,
                'updated_at': comment.updated_at,
            } for comment in comments]


        results = [get_obj(row) for row in qs]
        for result in results:
            result['sub_items'] = sub_item_data
            result['approvers'] = approver_data
            result['apv_cc'] = cc_data
            result['attachments'] = attachment_data
            result['comments'] = comment_data

        context = {
            'results': results
        }

        return JsonResponse(context, safe=False)



class ApvCreate(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=user_id)
        d_today = datetime.today().strftime('%Y-%m-%d')

        doc_no = generate_doc_no()
        apv_category_id = request.POST.get('apv_category_id', '')
        apv_status = request.POST.get('apv_status', '')
        doc_title = request.POST.get('doc_title', '')
        leave_reason = request.POST.get('leave_reason', '')
        period_from = self.get_date_from_string(request.POST.get('period_from', ''))
        period_to = self.get_date_from_string(request.POST.get('period_to', ''))
        period_count = self.get_float_from_string(request.POST.get('period_count', ''))
        special_comment = request.POST.get('special_comment', '')

        approver_ids = [request.POST.get(f'approver{i}', None) for i in range(1, 7)]
        approvers = [get_object_or_404(UserMaster, pk=id) for id in approver_ids if id]

        apv_cc_ids = request.POST.getlist('apv_cc[]', [])
        apv_cc_users = UserMaster.objects.filter(pk__in=apv_cc_ids) if apv_cc_ids else []

        context = {}

        try:
            ApvMaster_obj = ApvMaster.objects.create(
                apv_category_id=apv_category_id,
                apv_status=apv_status,
                doc_no=doc_no,
                doc_title=doc_title,
                leave_reason=leave_reason,
                period_from=period_from,
                period_to=period_to,
                period_count=period_count,
                special_comment=special_comment,
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

            self.save_attachments(request, ApvMaster_obj)

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
    context['period_to'] = obj.period_to
    context['period_count'] = obj.period_count
    context['special_comment'] = obj.special_comment
    # context['attached_files'] = [file.id for file in obj.attached_files.all()]
    # context['approver1'] = obj.approver1
    # context['approver2'] = obj.approver2
    # context['approver3'] = obj.approver3
    # context['approver4'] = obj.approver4
    # context['approver5'] = obj.approver5
    # context['approver6'] = obj.approver6
    # context['apv_cc'] = obj.apv_cc
    context['created_by'] = obj.created_by.id
    context['created_at'] = obj.created_at
    context['updated_at'] = obj.updated_at

    return context


def generate_doc_no():
    today = date.today()
    count_today = ApvMaster.objects.filter(created_at__date=today).count() + 1
    doc_no = f'AP{today.strftime("%y%m%d")}-{count_today:03d}'
    return doc_no



class ApvUpdate(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=user_id)
        d_today = datetime.today().strftime('%Y-%m-%d')

        doc_no = request.POST.get('doc_no', '')
        apv_category_id = request.POST.get('apv_category_id', '')
        apv_status = request.POST.get('apv_status', '')
        doc_title = request.POST.get('doc_title', '')
        leave_reason = request.POST.get('leave_reason', '')
        period_from = self.get_date_from_string(request.POST.get('period_from', ''))
        period_to = self.get_date_from_string(request.POST.get('period_to', ''))
        period_count = self.get_float_from_string(request.POST.get('period_count', ''))
        special_comment = request.POST.get('special_comment', '')

        approver_ids = [request.POST.get(f'approver{i}', None) for i in range(1, 7)]
        approvers = [get_object_or_404(UserMaster, pk=id) for id in approver_ids if id]

        apv_cc_ids = request.POST.getlist('apv_cc[]', [])
        apv_cc_users = UserMaster.objects.filter(pk__in=apv_cc_ids) if apv_cc_ids else []

        context = {}

        try:
            obj = ApvMaster.objects.get(pk=int(pk))
            obj.apv_category_id = apv_category_id,
            obj.apv_status = apv_status,
            obj.doc_no = doc_no,
            obj.doc_title = doc_title,
            obj.leave_reason = leave_reason,
            obj.period_from = period_from,
            obj.period_to = period_to,
            obj.period_count = period_count,
            obj.special_comment = special_comment,
            obj.created_by = user,
            obj.created_at = d_today,
            obj.updated_at = d_today,

            obj.save()

            ApvApprover_obj = ApvApprover.objects.create(
                document=ApvMaster_obj,
                **{f'approver{i}': approver for i, approver in enumerate(approvers, start=1)},
                **{f'approver{i}_status': '대기' for i in range(1, len(approvers) + 1)}
            )

            for apv_cc_user in apv_cc_users:
                ApvCC.objects.create(document=ApvMaster_obj, user=apv_cc_user)

            self.save_attachments(request, ApvMaster_obj)

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


# class ApvDeleteView(DeleteView):
#     model = ApvMaster
#     template_name = 'approval/apv_confirm_delete.html'
#     success_url = reverse_lazy('apv_list')


# class ApvCommentCreateView(CreateView):
#     model = ApvComment
#     form_class = ApvCommentForm
#     template_name = 'approval/apvcomment_form.html'
#
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.document = get_object_or_404(ApvMaster, pk=self.kwargs['pk'])
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('apv_detail', kwargs={'pk': self.kwargs['pk']})


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
            'username': obj.created_by.username,
            'department_position': obj.created_by.department_position.name,
        } if obj.created_by else '',
        'created_at': obj.created_at if obj.created_at is not None else '',
        'updated_at': obj.updated_at if obj.updated_at is not None else '',
        'form_template': obj.form_template if obj.form_template is not None else '',
        'form_data': obj.form_data if obj.form_data is not None else '',
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
        'period_to': obj.period_to if obj.period_to is not None else '',
        'period_count': obj.period_count if obj.period_count is not None else '',
        'leave_reason': obj.leave_reason if obj.leave_reason is not None else '',
    }


class ApvCategoryList(View):
    def get(self, request, *args, **kwargs):
        qs = ApvCategory.objects.all().order_by('name')
        categories = list(qs.values('id', 'name'))
        return JsonResponse(categories, safe=False)



class ApproveDocumentView(View):
    def post(self, request, *args, **kwargs):
        doc_id = self.kwargs.get('pk')
        document = get_object_or_404(ApvMaster, pk=doc_id)
        approver = document.apv_docs.filter(approver=request.user).first()

        if approver and approver.approver_status != 'approved':
            approver.approver_status = 'approved'
            approver.approver_date = datetime.now()
            approver.save()

            # 모든 승인자가 승인했는지 확인
            if all(a.approver_status == 'approved' for a in document.apv_docs.all()):
                document.apv_status = 'approved'
                document.save()

        return JsonResponse({'status': 'success'})


class RejectDocumentView(View):
    def post(self, request, *args, **kwargs):
        doc_id = self.kwargs.get('pk')
        document = get_object_or_404(ApvMaster, pk=doc_id)
        approver = document.apv_docs.filter(approver=request.user).first()

        if approver and approver.approver_status != 'rejected':
            approver.approver_status = 'rejected'
            approver.approver_date = datetime.now()
            approver.save()
            document.apv_status = 'rejected'
            document.save()

        return JsonResponse({'status': 'success'})