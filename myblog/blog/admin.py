from django.contrib import admin
from .models import Article
from .models import User, Comments
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',  'content','pub_date','reg_date')  # 显示列表的字段名
    list_filter = ('pub_date',)  # 筛选
    class Meta:
        model = Article

class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id',  'password','name')  # 显示列表的字段名
    class Meta:
        model = User
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user',  'name')  # 显示列表的字段名
    class Meta:
        model = Comments



admin.site.register(Article, ArticleAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Comments,CommentsAdmin)