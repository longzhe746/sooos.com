from django.db import models


# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=32, default='Title')
    content = models.TextField(null=True)
    pub_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.title

class User(models.Model):
    user_id = models.CharField(max_length=10)
    password = models.CharField(max_length=32)