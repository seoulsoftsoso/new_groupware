import requests
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import os
import mimetypes
from wsgiref.util import FileWrapper
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from urllib.parse import quote
from api.models import BoardMaster, ReplyMaster, UserMaster, FileBoardMaster, CodeMaster


def admin_notice_page(request):
    fixed_notice = BoardMaster.objects.filter(fixed_flag=True, delete_flag="N", boardcode_id=9).annotate(
        reply_count=Count('reply_board')).order_by("-id")[:2]
    notice = BoardMaster.objects.filter(delete_flag="N", boardcode_id=9).annotate(
        reply_count=Count('reply_board')).order_by("-id")

    context = {
        'fixed_notice': fixed_notice,
        'notice': notice,
    }

    return render(request, 'admins/notice/notice.html', context)


def amdin_noticedetail_page(request, notice_id):
    notice = BoardMaster.objects.filter(pk=notice_id, delete_flag='N').annotate(reply_count=Count('reply_board')).first();

    # 조회수 증가
    notice.click_cnt += 1
    notice.save()

    # 게시글에 첨부된 파일 가져오기
    files = FileBoardMaster.objects.filter(parent_id=notice, delete_flag="N")

    # 게시글에 달린 댓글 가져오기
    replies = ReplyMaster.objects.filter(parent_id=notice, delete_flag="N")

    context = {
        'notice': notice,
        'files': files,
        'replies': replies,
    }

    return render(request, 'admins/notice/notice_detail.html', context)


def admin_noticewrite_add(request):
    if request.method == 'POST':
        formdata = request.POST
        title = formdata.get('title')
        content = formdata.get('content')
        fixed_flag = formdata.get('fixed_flag')
        files = request.FILES.getlist('file')
        created_by_id = request.user.id

        if fixed_flag == 'true':
            fixed_flag = True
        else:
            fixed_flag = False

        board_instance = BoardMaster.objects.create(
            title=title, content=content, boardcode=CodeMaster.objects.get(code='NOTICE'), fixed_flag=fixed_flag,
            file_flag=bool(files), created_by_id=created_by_id
        )

        if files:
            for file in files:
                FileBoardMaster.objects.create(
                    parent=board_instance, file_path=file, created_by_id=created_by_id
                )

    else:
        raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'admins/index.html')


def admin_noticewrite_edit(request, notice_id):
    board_instance = get_object_or_404(BoardMaster, pk=notice_id)
    if request.method == 'POST':
        formdata = request.POST
        title = formdata.get('title')
        content = formdata.get('content')
        fixed_flag = formdata.get('fixed_flag')
        files = request.FILES.getlist('file')
        created_by_id = request.user.id

        if fixed_flag == 'true':
            fixed_flag = True
        else:
            fixed_flag = False

        # 필드 업데이트
        board_instance.title = title
        board_instance.content = content
        board_instance.fixed_flag = fixed_flag
        board_instance.file_flag = bool(files)
        code_instance = CodeMaster.objects.get(code='NOTICE')
        board_instance.boardcode = code_instance
        board_instance.updated_at = timezone.now()

        board_instance.save()

        if files:
            for file in files:
                FileBoardMaster.objects.create(
                    parent=board_instance, file_path=file, created_by_id=created_by_id
                )

    else:
        raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'admins/index.html')


def download_File(request, file_id):
    file_instance = FileBoardMaster.objects.get(pk=file_id, delete_flag="N")

    file_url = file_instance.file_path.url
    response = requests.get(file_url, stream=True)

    # 파일의 확장자를 통해 MIME 타입을 추정
    content_type, _ = mimetypes.guess_type(file_url)
    # 추정이 불가능한 경우, 일반적인 바이너리 데이터를 의미하는 'application/octet-stream'을 사용
    if content_type is None:
        content_type = 'application/octet-stream'

    file_name = os.path.basename(file_url)
    file_wrapper = FileWrapper(response.raw)
    response = HttpResponse(file_wrapper, content_type=content_type)
    # 파일 이름
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(quote(file_name))

    return response


def delete_file(request):
    if request.method == "POST":
        file_id = request.POST.get("file_id")
        try:
            file_obj = get_object_or_404(FileBoardMaster, id=file_id)
            file_obj.delete_flag = "Y"
            file_obj.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


def admin_notice_delete(request):
    if request.method == "POST":
        notice_id = request.POST.get('notice_id')
        notice = BoardMaster.objects.get(id=notice_id)
        notice.delete_flag = "Y"
        notice.save()
        print('성공')
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'fail'})
