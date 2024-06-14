import json
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.db import transaction, DatabaseError
from django.db.models import Q
from django.http import JsonResponse
from lib import Pagenation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from api.models import StoryMaster, StoryLikes

from django import forms

class StoryForm(forms.ModelForm):
    class Meta:
        model = StoryMaster
        fields = ['story_title', 'story_content', 'story_category', 'story_picture']
        widgets = {
            'story_title': forms.TextInput(attrs={'required': 'required'}),
            'story_content': forms.Textarea(attrs={'required': 'required'}),
            'story_category': forms.Select(attrs={}),
            'story_picture': forms.ClearableFileInput(attrs={}),
        }

@method_decorator(login_required, name='dispatch')
class StoryCreateView(View):
    def post(self, request, *args, **kwargs):
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user
            story.updated_by = request.user
            story.save()
            return JsonResponse({"message": "스토리가 등록되었습니다."}, status=201)
        else:
            # 디버깅을 위해 폼 에러를 로그에 출력
            # print(form.errors)
            return JsonResponse({"errors": form.errors}, status=400)


class Story_read(View):

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        _page = request.GET.get('page', '')
        _size = request.GET.get('page_size', '')
        user = request.user

        qs = StoryMaster.objects.filter().order_by('-id')

        # 카테고리
        story_category_sch = request.GET.get('story_category_sch', '')
        if story_category_sch == '':
            qs = qs
        else:
            qs = qs.filter(story_category=story_category_sch)

        story_id = request.GET.get('story_id', '')
        if story_id:
            story = get_object_or_404(StoryMaster, id=story_id)
            story.views += 1  # 조회수 증가
            story.save()
            qs = qs.filter(id=story_id)

        if _page == '' or _size == '':
            # 조건 에러시, 전체 보여주기
            print(_page, _size)
            results = [get_obj(row, user) for row in qs]

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

        results = [get_obj(row, user) for row in qs_ps]

        context = {}
        context['count'] = qs_ps.paginator.count
        context['previous'] = url_pre
        context['next'] = url_next
        context['results'] = results

        return JsonResponse(context, safe=False)


@method_decorator(login_required, name='dispatch')
class Story_update(View):
    def get(self, request, *args, **kwargs):
        story_id = request.GET.get('story_id')
        if not story_id:
            return JsonResponse({"error": "story_id is required"}, status=400)

        story = get_object_or_404(StoryMaster, pk=story_id)
        form = StoryForm(instance=story)
        return render(request, '/menu/010901/', {'form': form, 'story': story})

    def post(self, request, *args, **kwargs):
        story_id = request.GET.get('story_id')
        story = get_object_or_404(StoryMaster, pk=story_id)

        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            try:
                story = form.save(commit=False)
                story.updated_by = request.user
                story.save()
                return JsonResponse({"message": "스토리가 수정되었습니다."}, status=200)
            except DatabaseError as e:
                # 디버깅을 위해 에러를 로그에 출력
                # print(f"DatabaseError: {e}")
                return JsonResponse({"error": "데이터베이스 오류가 발생했습니다. 관리자에게 문의하세요."}, status=500)
        else:
            # 디버깅을 위해 폼 에러를 로그에 출력
            # print(form.errors)
            return JsonResponse({"errors": form.errors}, status=400)


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class Story_delete(View):
    def post(self, request, *args, **kwargs):
        story_id = request.POST.get('story_id')
        if not story_id:
            return JsonResponse({"error": "story_id is required"}, status=400)

        story = get_object_or_404(StoryMaster, pk=story_id)

        # 삭제 권한 확인 (자신이 작성한 글만 삭제할 수 있게 하는 예시)
        if story.created_by != request.user:
            return JsonResponse({"error": "삭제 권한이 없습니다."}, status=403)

        story.delete()
        return JsonResponse({"message": "스토리가 삭제되었습니다."}, status=200)


@login_required(login_url='/login/')
def toggle_like(request, story_id):
    story = get_object_or_404(StoryMaster, id=story_id)
    user = request.user

    if StoryLikes.objects.filter(story=story, user=user).exists():
        StoryLikes.objects.filter(story=story, user=user).delete()
        liked = False
    else:
        StoryLikes.objects.create(story=story, user=user)
        liked = True

    return JsonResponse({'liked': liked, 'like_count': story.likes.count()})


def get_obj(obj, user):
    liked = False
    if user.is_authenticated:
        liked = StoryLikes.objects.filter(story=obj, user=user).exists()

    return {
        'id': obj.id,
        'story_title': obj.story_title if obj.story_title is not None else '',
        'story_content': obj.story_content if obj.story_content is not None else '',
        'story_picture': obj.story_picture.url if obj.story_picture else '',
        'story_category': obj.story_category if obj.story_category is not None else '',

        'created_by': obj.created_by.username if obj.created_by is not None else '',
        'updated_by': obj.updated_by.username if obj.updated_by is not None else '',
        'created_at': obj.created_at if obj.created_at is not None else '',
        'updated_at': obj.updated_at if obj.updated_at is not None else '',

        'views': obj.views,
        'liked': liked,
        'like_count': obj.likes.count()
    }