from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
import os
import mimetypes
from wsgiref.util import FileWrapper
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from urllib.parse import quote
from api.models import BoardMaster, ReplyMaster, UserMaster, FileBoardMaster, CodeMaster


def reply_add(request):
    if request.method == "POST":
        reply = request.POST.get('reply')
        parent_id = request.POST.get('parent_id')
        created_by_id = request.user.id

        reply_instance = ReplyMaster.objects.create(
            reply=reply, parent_id=parent_id, created_by_id=created_by_id
        )

        reply_instance.save()

        print(reply_instance.created_by.username)

        return JsonResponse({
            'status': 'success',
            'message': '댓글이 성공적으로 추가되었습니다.',
        })

def reply_edit(request):
    if request.method == 'POST':
        reply_id = request.POST.get('reply_id')
        new_reply = request.POST.get('new_reply')

        reply = get_object_or_404(ReplyMaster, id=reply_id, created_by=request.user)
        reply.reply = new_reply
        reply.save()

        return JsonResponse({'status': 'ok'})

def reply_delete(request):
    if request.method == 'POST':
        reply_id = request.POST.get('reply_id')

        reply = get_object_or_404(ReplyMaster, id=reply_id, created_by=request.user)
        reply.delete()

        return JsonResponse({'status': 'ok'})