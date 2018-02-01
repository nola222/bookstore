# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Books',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=False)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('type_id', models.SmallIntegerField(verbose_name='商品种类', default=1, choices=[(1, 'python'), (2, 'javascript'), (3, '数据结构与算法'), (4, '机器学习'), (5, '操作系统'), (6, '数据库')])),
                ('name', models.CharField(max_length=20, verbose_name='商品名称')),
                ('desc', models.CharField(max_length=128, verbose_name='商品简介')),
                ('price', models.DecimalField(max_digits=10, verbose_name='商品价格', decimal_places=2)),
                ('unit', models.CharField(max_length=20, verbose_name='商品单位')),
                ('stock', models.IntegerField(verbose_name='商品库存', default=1)),
                ('sales', models.IntegerField(verbose_name='商品销量', default=0)),
                ('detail', tinymce.models.HTMLField(verbose_name='商品详情')),
                ('image', models.ImageField(storage=django.core.files.storage.FileSystemStorage(location='/root/BookStore/bookstore/collect_static'), verbose_name='商品图片', upload_to='books')),
                ('status', models.SmallIntegerField(verbose_name='商品状态', default=1, choices=[(0, '下线'), (1, '上线')])),
            ],
            options={
                'db_table': 's_books',
            },
        ),
    ]
