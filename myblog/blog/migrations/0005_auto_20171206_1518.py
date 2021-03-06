# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-06 07:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-pub_date',)},
        ),
        migrations.AddField(
            model_name='article',
            name='reg_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='日期'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(null=True, verbose_name='内容'),
        ),
        migrations.AlterField(
            model_name='article',
            name='pub_date',
            field=models.DateTimeField(null=True, verbose_name='插入时间'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(default='Title', max_length=32, verbose_name='主题'),
        ),
    ]
