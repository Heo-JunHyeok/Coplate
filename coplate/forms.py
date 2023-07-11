from django import forms
from .models import User


class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["nickname"]  # 추가할 필드만 명시

    def signup(self, request, user):
        user.nickname = self.cleaned_data["nickname"]  # Form에 기입된 데이터 = cleaned_data
        user.save()
