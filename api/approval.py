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


class ApvForm(forms.ModelForm):
    class Meta:
        model = ApvMaster
        fields = [
            'doc_title', 'apv_category', 'apv_status', 'form_template', 'form_data',
            'special_comment', 'deadline', 'payment_method',
            'related_team', 'related_project', 'related_info', 'total_cost',
            'period_from', 'period_to', 'period_count', 'leave_reason'
        ]
        labels = {
            'doc_title': '제목',
            'apv_category': '카테고리',
            'apv_status': '결재 상태',
            'form_template': '양식 템플릿',
            'form_data': '양식 데이터',
            'special_comment': '특별 의견',
            'deadline': '마감 기한',
            'payment_method': '결제 방법',
            'related_team': '관련 팀',
            'related_project': '관련 프로젝트',
            'related_info': '관련 정보',
            'total_cost': '총 비용',
            'period_from': '시작 기간',
            'period_to': '종료 기간',
            'period_count': '기간 수',
            'leave_reason': '휴가 사유'
        }


class ApvCommentForm(forms.ModelForm):
    class Meta:
        model = ApvComment
        fields = ['content']


class ApvListView(View):

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '')
        _size = request.GET.get('page_size', '')
        date_sch_from = request.GET.get('date_sch_from', '')
        date_sch_to = request.GET.get('date_sch_to', '')

        qs = ApvMaster.objects.filter().order_by('-updated_at')

        # 기간 검색
        if date_sch_from != '':
            qs = qs.filter(updated_at__gte=date_sch_from)

        if date_sch_to != '':
            qs = qs.filter(updated_at__lte=date_sch_to)

        # 키워드 검색
        apv_all_sch = request.GET.get("apv_all_sch", '')
        search_keywords = apv_all_sch.split(',')
        search_conditions = Q()
        for keyword in search_keywords:
            keyword = keyword.strip()
            if keyword:
                all_sch_upper = keyword.upper()
                all_sch_lower = keyword.lower()

                search_condition = (
                        Q(doc_no__icontains=keyword) |
                        Q(doc_title__icontains=keyword) |
                        Q(created_by__username__icontains=keyword) |
                        Q(apv_category__name__icontains=keyword) |

                        Q(doc_no__icontains=all_sch_lower) |
                        Q(doc_title__icontains=all_sch_lower) |
                        Q(created_by__username__icontains=all_sch_lower) |
                        Q(apv_category__name__icontains=all_sch_lower) |

                        Q(doc_no__icontains=all_sch_upper) |
                        Q(doc_title__icontains=all_sch_upper) |
                        Q(created_by__username__icontains=all_sch_upper) |
                        Q(apv_category__name__icontains=all_sch_upper)
                )
                search_conditions |= search_condition  # OR 연산으로 추가
        qs = qs.filter(search_conditions)

        # 결재상태 검색
        apv_status_sch = request.GET.get('apv_status_sch', '')
        if apv_status_sch == '전체' or apv_status_sch == '':
            qs = qs
        else:
            qs = qs.filter(apv_status=apv_status_sch)

        if _page == '' or _size == '':
            print(_page, _size)
            results = [get_obj(row) for row in qs]
            context = {}
            context['results'] = results

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

        context = {}
        context['count'] = qs_ps.paginator.count
        context['previous'] = url_pre
        context['next'] = url_next
        context['results'] = results

        return JsonResponse(context, safe=False)


class ApvCreate(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_id = request.COOKIES["user_id"]
        user = UserMaster.objects.get(id=user_id)
        d_today = datetime.today().strftime('%Y-%m-%d')

        apv_category_id = request.POST.get('apv_category_id', '')
        apv_status = request.POST.get('apv_status', '')

        doc_no = generate_doc_no()
        doc_title = request.POST.get('doc_title', '')
        leave_reason = request.POST.get('leave_reason', '')
        period_from = request.POST.get('period_from', '')
        period_to = request.POST.get('period_to', '')
        period_count = request.POST.get('period_count', None)
        special_comment = request.POST.get('special_comment', '')

        if period_count == '':
            period_count = None
        else:
            try:
                period_count = float(period_count) if period_count is not None else None
            except ValueError:
                period_count = None

        try:
            period_from = datetime.strptime(period_from, '%Y-%m-%d').date() if period_from else None
        except ValueError:
            period_from = None

        try:
            period_to = datetime.strptime(period_to, '%Y-%m-%d').date() if period_to else None
        except ValueError:
            period_to = None

        approver1_id = request.POST.get('approver1', None)
        approver2_id = request.POST.get('approver2', None)
        approver3_id = request.POST.get('approver3', None)
        approver4_id = request.POST.get('approver4', None)
        approver5_id = request.POST.get('approver5', None)
        approver6_id = request.POST.get('approver6', None)

        approver1 = UserMaster.objects.get(pk=approver1_id) if approver1_id else None
        approver2 = UserMaster.objects.get(pk=approver2_id) if approver2_id else None
        approver3 = UserMaster.objects.get(pk=approver3_id) if approver3_id else None
        approver4 = UserMaster.objects.get(pk=approver4_id) if approver4_id else None
        approver5 = UserMaster.objects.get(pk=approver5_id) if approver5_id else None
        approver6 = UserMaster.objects.get(pk=approver6_id) if approver6_id else None

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
                approver1=approver1,
                approver2=approver2,
                approver3=approver3,
                approver4=approver4,
                approver5=approver5,
                approver6=approver6,
                approver1_status='대기' if approver1 else None,
                approver2_status='대기' if approver2 else None,
                approver3_status='대기' if approver3 else None,
                approver4_status='대기' if approver4 else None,
                approver5_status='대기' if approver5 else None,
                approver6_status='대기' if approver6 else None,
            )

            for apv_cc_user in apv_cc_users:
                ApvCC.objects.create(
                    document=ApvMaster_obj,
                    user=apv_cc_user
                )

            attached_file_objs = []
            i = 0
            while f'attached_files[{i}][name]' in request.POST:
                file_name = request.POST[f'attached_files[{i}][name]']
                file_content_base64 = request.POST[f'attached_files[{i}][content]']
                file_content = base64.b64decode(file_content_base64)
                file = ContentFile(file_content, name=file_name)
                attached_file_objs.append(ApvAttachments(document=ApvMaster_obj, file=file))
                i += 1

            if attached_file_objs:
                ApvAttachments.objects.bulk_create(attached_file_objs)

            # attached_file_objs = []
            # i = 0
            # while f'attached_files[{i}][name]' in request.POST:
            #     file_name = request.POST[f'attached_files[{i}][name]']
            #     file_content_base64 = request.POST[f'attached_files[{i}][content]']
            #     file_content = base64.b64decode(file_content_base64)
            #     file = ContentFile(file_content, name=file_name)
            #     attachment = ApvAttachments.objects.create(file=file)
            #     attached_file_objs.append(attachment)
            #     i += 1
            #
            # if attached_file_objs:
            #     ApvMaster_obj.attached_files.add(*attached_file_objs)

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
    context['attached_files'] = [file.id for file in obj.attached_files.all()]
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


# class ApvDetailView(DetailView):
#     model = ApvMaster
#     template_name = 'approval/apv_detail.html'
#     context_object_name = 'apv_detail'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         document = self.get_object()
#         approvers = document.apv_docs.all().order_by('approver_priority')
#
#         context['approvers'] = approvers
#         context['user_is_approver'] = approvers.filter(approver=self.request.user).exists()
#         context['user_is_creator'] = document.created_by == self.request.user
#
#         return context


class ApvUpdateView(UpdateView):
    model = ApvMaster
    form_class = ApvForm
    template_name = 'approval/apv_form.html'
    success_url = reverse_lazy('apv_list')


class ApvDeleteView(DeleteView):
    model = ApvMaster
    template_name = 'approval/apv_confirm_delete.html'
    success_url = reverse_lazy('apv_list')


class ApvCommentCreateView(CreateView):
    model = ApvComment
    form_class = ApvCommentForm
    template_name = 'approval/apvcomment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.document = get_object_or_404(ApvMaster, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('apv_detail', kwargs={'pk': self.kwargs['pk']})


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
        # 'created_by': obj.created_by.username if obj.created_by is not None else '',
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