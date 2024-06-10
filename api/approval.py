from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import ApvMaster, ApvComment, ApvSubItem, ApvApprover, ApvCC
from django import forms


class ApvForm(forms.ModelForm):
    class Meta:
        model = ApvMaster
        fields = ['doc_title', 'apv_category', 'apv_status', 'form_template', 'form_data',
                  'special_comment', 'deadline', 'payment_method',
                  'related_team', 'related_project', 'related_info', 'total_cost',
                  'period_from', 'period_to', 'period_count', 'leave_reason']


class ApvCommentForm(forms.ModelForm):
    class Meta:
        model = ApvComment
        fields = ['content']


class ApvListView(ListView):
    model = ApvMaster
    template_name = 'approval/apv_list.html'
    context_object_name = 'apv_list'
    paginate_by = 20

    def get_queryset(self):
        return ApvMaster.objects.all().order_by('-updated_at')


class ApvDetailView(DetailView):
    model = ApvMaster
    template_name = 'approval/apv_detail.html'
    context_object_name = 'apv_detail'


class ApvCreateView(CreateView):
    model = ApvMaster
    form_class = ApvForm
    template_name = 'apv_form.html'
    success_url = reverse_lazy('apv_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ApvUpdateView(UpdateView):
    model = ApvMaster
    form_class = ApvForm
    template_name = 'apv_form.html'
    success_url = reverse_lazy('apv_list')


class ApvDeleteView(DeleteView):
    model = ApvMaster
    template_name = 'apv_confirm_delete.html'
    success_url = reverse_lazy('apv_list')


class ApvCommentCreateView(CreateView):
    model = ApvComment
    form_class = ApvCommentForm
    template_name = 'apvcomment_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.document = get_object_or_404(ApvMaster, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('apv_detail', kwargs={'pk': self.kwargs['pk']})
