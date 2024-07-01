from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import transaction, DatabaseError
from django.db.models import Q
from .models import ApvMaster, ApvComment, ApvSubItem, ApvApprover, ApvCC, ApvCategory, UserMaster, ApvAttachments, ApvReadStatus, NotiCenter
from django import forms
from lib import Pagenation
from datetime import datetime, date
from django.utils import timezone
import base64
from django.core.files.base import ContentFile

class ApvListView(View):

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        user_id = request.COOKIES["user_id"]
        user = get_object_or_404(UserMaster, id=user_id)
        _page = request.GET.get('page', '')
        _size = request.GET.get('page_size', '')

        qs = NotiCenter.objects.filter(user=user).order_by('-is_read', '-created_at')

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

        results = [{
            'id': noti.id,
            'content': noti.content,
            'url': noti.url,
            'is_read': noti.is_read,
            'created_at': noti.created_at,
            'apv_docs': {
                'id': noti.apv_docs.id,
                'doc_title': noti.apv_docs.doc_title
            }
        } for noti in qs_ps]

        context = {
            'count': qs_ps.paginator.count,
            'previous': url_pre,
            'next': url_next,
            'results': results
        }

        return JsonResponse(context, safe=False)