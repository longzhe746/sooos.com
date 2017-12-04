from django.contrib import admin
from .models import Article
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',  'content','pub_date')  # 显示列表的字段名
    list_filter = ('pub_date',)  # 筛选



admin.site.register(Article, ArticleAdmin)