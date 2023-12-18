from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
from api.models import BoardMaster, ReplyMaster, UserMaster, FileBoardMaster, CodeMaster, GroupCodeMaster, \
    EnterpriseMaster
from django.db.models import Q


def amdin_board_page(request):
    fixed_board = BoardMaster.objects.filter(fixed_flag=True, delete_flag="N").order_by("-updated_at")
    boardmasters = BoardMaster.objects.filter(delete_flag="N").exclude(boardcode=9).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at")
    codemaster = CodeMaster.objects.filter(group=3).exclude(code__in=['NOTICE', 'ASK'])

    context = {
        'fixed_board': fixed_board,
        'boardmaster': boardmasters,
        'codemaster': codemaster,
    }

    return render(request, 'admins/board/board.html', context)


def admin_boardList_page(request, id):
    fixed_boardmaster = BoardMaster.objects.filter(fixed_flag=True, delete_flag="N", boardcode_id=id).exclude(
        boardcode_id=9).annotate(reply_count=Count('reply_board')).order_by("-updated_at")[:2]
    boardmaster = BoardMaster.objects.filter(delete_flag="N", boardcode_id=id).exclude(boardcode_id=9).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at")
    codemaster = CodeMaster.objects.filter(group=3).exclude(code__in=['NOTICE', 'ASK'])

    print('boardmaster : ', boardmaster)

    context = {
        'fixed_boardmaster': fixed_boardmaster,
        'boardmaster': boardmaster,
        'codemaster': codemaster
    }

    return render(request, 'admins/board/board_list.html', context)


def amdin_boardDetail_page(request, board_id):
    codemaster = CodeMaster.objects.filter(group=3).exclude(code__in=['NOTICE', 'ASK'])
    board = BoardMaster.objects.get(pk=board_id, delete_flag='N')

    # 조회수 증가
    board.click_cnt += 1
    board.save()

    # 게시글에 첨부된 파일 가져오기
    files = FileBoardMaster.objects.filter(parent_id=board, delete_flag="N")

    # 게시글에 달린 댓글 가져오기
    replies = ReplyMaster.objects.filter(parent_id=board, delete_flag="N")

    context = {
        'codemaster': codemaster,
        'board': board,
        'files': files,
        'replies': replies,
    }

    return render(request, 'admins/board/board_detail.html', context)


def admin_boardwrite_add(request):
    if request.method == 'POST':
        formdata = request.POST
        title = formdata.get('title')
        content = formdata.get('content')

        boardcode_id = formdata.get('boardcode')
        boardcode = CodeMaster.objects.get(id=boardcode_id)

        fixed_flag = formdata.get('fixed_flag')
        files = request.FILES.getlist('file')
        created_by_id = request.COOKIES.get('user_id')

        if fixed_flag == 'true':
            fixed_flag = True
        else:
            fixed_flag = False

        board_instance = BoardMaster.objects.create(
            title=title, content=content, boardcode=boardcode, fixed_flag=fixed_flag,
            file_flag=bool(files), created_by_id=created_by_id
        )

        if files:
            for file in files:
                file_path = os.path.join(settings.MEDIA_ROOT, file.name)

                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                FileBoardMaster.objects.create(
                    parent=board_instance, file_path=file_path, created_by_id=created_by_id
                )

    else:
        raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'admins/index.html')


def admin_boardwrite_edit(request, board_id):
    board_instance = get_object_or_404(BoardMaster, pk=board_id)
    if request.method == 'POST':
        formdata = request.POST
        title = formdata.get('title')
        content = formdata.get('content')
        fixed_flag = formdata.get('fixed_flag')
        files = request.FILES.getlist('file')
        created_by_id = request.COOKIES.get('user_id')

        boardcode_id = formdata.get('boardcode')
        boardcode = CodeMaster.objects.filter(id=boardcode_id).first()

        if fixed_flag == 'true':
            fixed_flag = True
        else:
            fixed_flag = False

        # 필드 업데이트
        board_instance.title = title
        board_instance.content = content
        board_instance.fixed_flag = fixed_flag
        board_instance.file_flag = bool(files)

        board_instance.boardcode_id = boardcode

        board_instance.updated_at = timezone.now()
        board_instance.save()

        if files:
            for file in files:
                file_path = os.path.join(settings.MEDIA_ROOT, file.name)

                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                FileBoardMaster.objects.create(
                    parent=board_instance, file_path=file_path, created_by_id=created_by_id
                )

    else:
        raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'admins/index.html')


def admin_boardGroup_add(request):
    if request.method == "POST":
        code = request.POST.get('board_group_code')
        name = request.POST.get('board_group_name')
        group = GroupCodeMaster.objects.get(id=3)
        enterprise = EnterpriseMaster.objects.get(id=1)
        created_by_id = request.COOKIES.get('user_id')

        new_codemaster = CodeMaster(
            code=code, name=name, group=group, enterprise=enterprise, created_by_id=created_by_id
        )

        new_codemaster.save()

        return JsonResponse({"success": True})


def admin_boardGroup_edit(request):
    if request.method == "POST":
        id = request.POST.get('id')
        code = request.POST.get('board_group_edit_code')
        name = request.POST.get('board_group_edit_name')

        code_master_to_edit = CodeMaster.objects.get(id=id)

        code_master_to_edit.code = code
        code_master_to_edit.name = name

        code_master_to_edit.save()

        return JsonResponse({"success": True})


def admin_boardGroup_delete(request):
    id = request.GET.get('id')
    print('id : ', id)

    CodeMaster.objects.filter(id=id).delete();

    return HttpResponse()


def admin_board_delete(request):
    if request.method == "POST":
        board_id = request.POST.get('board_id')
        board = BoardMaster.objects.get(id=board_id)
        board.delete_flag = "Y"
        board.save()
        print('성공')
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'fail'})
