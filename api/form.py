from django import forms
from django.contrib.auth import get_user_model

from api.models import Question, UserMaster

User = get_user_model()


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['Question_type', 'Question_path', 'Question_name', 'Question_company', 'Question_position',
                  'Question_department', 'Question_phone', 'Question_email', 'Question_content']

