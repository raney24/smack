# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-17 20:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smack', '0009_auto_20160317_0755'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='smack_post',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='user',
        ),
        migrations.RemoveField(
            model_name='smackpost',
            name='downs',
        ),
        migrations.RemoveField(
            model_name='smackpost',
            name='score',
        ),
        migrations.RemoveField(
            model_name='smackpost',
            name='ups',
        ),
        migrations.DeleteModel(
            name='Vote',
        ),
    ]
