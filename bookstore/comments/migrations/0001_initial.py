# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('disabled', models.BooleanField(verbose_name='禁用评论', default=False)),
                ('content', models.CharField(max_length=1000, verbose_name='评论内容')),
                ('book', models.ForeignKey(verbose_name='书籍id', to='books.Books')),
                ('user', models.ForeignKey(verbose_name='用户id', to='users.Passport')),
            ],
            options={
                'db_table': 's_comment_table',
            },
        ),
    ]
