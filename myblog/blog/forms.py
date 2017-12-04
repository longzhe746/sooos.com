from django import forms
from blog.models import User

class UserForm(forms.Form):
    user_id = forms.CharField(label='用户名',required=True)
    password = forms.CharField(label='密码',required=True,widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('user_id','password')