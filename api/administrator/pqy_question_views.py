from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from api.models import UserMaster, Question


class PayQuestionPage(ListView):
    template_name = 'admins/administrator/pay_question/pay_question.html'
    paginate_by = 1000

    def get_queryset(self):
        search_to = self.request.GET.get('search-to', None)
        search_from = self.request.GET.get('search-from', None)
        name_filter = self.request.GET.get('search-content', None)

        queryset = Question.objects.all()

        if search_to:
            queryset = queryset.filter(Question_date__date__gte=search_to)
        if search_from:
            queryset = queryset.filter(Question_date__date__lte=search_from)
        if name_filter:
            queryset = queryset.filter(Question_name__icontains=name_filter)

        result = queryset.values(
            'id', 'Question_type', 'Question_path', 'Question_name', 'Question_company', 'Question_position',
            'Question_phone', 'Question_content', 'Question_date'
        ).order_by('-id')

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_to'] = self.request.GET.get('search-to', None)
        context['search_from'] = self.request.GET.get('search-from', None)
        context['search_content'] = self.request.GET.get('search_content', '')
        context['result'] = context['object_list']
        return context


class PayQuestionDetail(View):
    template_name = 'admins/administrator/pay_question/pay_question_detail.html'

    def get(self, request, *args, **kwargs):
        question_id = kwargs['question_id']
        question = Question.objects.get(id=question_id)

        context = {
            'obj': question,
        }

        return render(request, self.template_name, context)
