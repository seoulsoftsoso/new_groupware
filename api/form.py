from dal import autocomplete
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from api.models import Question, UserMaster

User = get_user_model()


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['Question_type', 'Question_path', 'Question_name', 'Question_company', 'Question_position',
                  'Question_department', 'Question_phone', 'Question_email', 'Question_content']


class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserMaster
        fields = ('username', 'user_id', 'password', 'email', 'useremailreceive', 'userintro')

    def clean_password(self):
        # 비밀번호 암호화 로직
        password = self.cleaned_data.get('password')
        return make_password(password)