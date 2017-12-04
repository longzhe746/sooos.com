from django.contrib import admin
from .models import Article
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title',  'content','pub_date')
    list_filter = ('pub_date',)



admin.site.register(Article, ArticleAdmin)