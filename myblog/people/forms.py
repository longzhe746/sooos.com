from django import forms
from people.models import Member
from django.core.validators import URLValidator

class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名',min_length=2, max_length=16,required=True)
    password = forms.CharField(label='密码', min_length=6, max_length=30,required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(label='重复密码',min_length=6, max_length=30, required=True, widget=forms.PasswordInput())
    email = forms.EmailField(label='邮箱',max_length=255, required=True)

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if  password and password2 and password != password2:
            raise forms.ValidationError('两次密码不相同')
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username').strip()

        if username[:1] == '_':
            raise forms.ValidationError('用户名不能与下划线大头')

        try:
            Member._default_manager.get(username=username)

        except Member.DoesNotExist:
            return username

        raise  forms.ValidationError('用户名 %s已经存在' % username)

    def clean_email(self):
        email = self.cleaned_data.get('email').strip()
        try:
            Member._default_manager.get(email=email)
        except Member.DoesNotExist:
            return  email

        raise  forms.ValidationError('邮箱 %s 已经存在' % email)
    
