# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-29 09:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='类别名称')),
            ],
        ),
        migrations.CreateModel(
            name='CoolSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='站点地址')),
                ('name', models.CharField(max_length=100, verbose_name='站点名称')),
                ('description', models.TextField(blank=True, verbose_name='站点介绍')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.Category', verbose_name='所属类别')),
            ],
        ),
    ]
