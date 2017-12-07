from django.db import models


# Create your models here.
class Article(models.Model):
    title = models.CharField(verbose_name='主题',max_length=32, default='Title')
    content = models.TextField(verbose_name='内容',null=True)
    pub_date = models.DateTimeField(verbose_name='插入时间',null=True)
    reg_date = models.DateTimeField(auto_now_add=True,verbose_name='日期')

    class Meta:
        ordering = ('-pub_date',) # 倒序前面加 -

    def __str__(self):
        return self.title

class User(models.Model):
    user_id = models.CharField(max_length=10)
    password = models.CharField(max_length=32)
    name = models.CharField(verbose_name='姓名',max_length=32)

    def __str__(self):
        return self.name

class Comments(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(verbose_name='姓名',max_length=32)
    def __str__(self):
        return self.name