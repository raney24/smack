# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-22 04:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smack', '0012_auto_20160317_2110'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='smackpost',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='smackpost',
            name='votes',
            field=models.ManyToManyField(to='smack.Vote'),
        ),
    ]