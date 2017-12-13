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

class LoginForm(forms.Form):
    username = forms.CharField(label='用户名',required=True)
    password = forms.CharField(label='密码',widget=forms.PasswordInput(),required=True)
    def clean_username(self):
        username = self.cleaned_data.get('username').strip()
        username_exits = True
        email_exits = True
        try:
            Member._default_manager.get(username=username)
        except Member.DoesNotExist:
            username_exits = False

        try:
            Member._default_manager.get(email=username)
        except Member.DoesNotExist:
            email_exits = False
        if username_exits  or email_exits:
            return  username
        raise forms.ValidationError('用户名或邮箱不存在')

class ProfileForm(forms.ModelForm):
    blog = forms.CharField(label='博客',max_length=128,required=False,validators=[URLValidator],widget=forms.URLInput(attrs={'class' : 'form-control'}))
    location = forms.CharField(label='城市', max_length=10,required=False,widget=forms.TextInput(attrs={'class' : 'form-control'}))
    weibo_id = forms.CharField(label='微博', max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile = forms.CharField(label='个人简介',max_length=140,required=False,widget=forms.Textarea(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='邮箱', max_length=255,required=True,widget=forms.TextInput(attrs={'class':'disabled form-control'}))

    def __init__(self,*args,**kwargs):
        super(ProfileForm, self).__init__(*args,**kwargs)
        user = kwargs.pop('instance',None)
        self.old_email = user.email
    def clean_email(self):
        cleaned_date =  super(ProfileForm,self).clean()
        email = cleaned_date.get('email').strip()
        try:
            user = Member.objects.get(email=email)
        except (Member.DoesNotExist,ValueError):
            return email
        else:
            if user.email == self.old_email:
                return email
            else:
                raise forms.ValidationError('邮箱 %s 已经存在' % email)

    def clean_weibo_id(self):
        weibo = self.cleaned_data.get('weibo_id').strip()
        if weibo.startswith('@'):
            weibo = weibo[1:]
        return  weibo

    class Meta:
        model  = Member
        fields = ('blog','location','weibo_id','profile','email')
        exclude = ('is_active','is_admin','password','last_login','date_joined',
                   'email_verified','username','avatar','au','last_ip','comment_num','topic_num')

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='原密码',required=True,widget=forms.PasswordInput(attrs={'class' : 'form-control'}))
    password = forms.CharField(label='新密码', min_length=6, max_length=30, required=True, widget=forms.PasswordInput(attrs={'class' : 'form-control'}))
    password2 = forms.CharField(label='重复密码', min_length=6, max_length=30, required=True, widget=forms.PasswordInput(attrs={'class' : 'form-control'}))

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password2 and password != password2:
            return  forms.ValidationError('两次输入密码不一致')
        return  password2
