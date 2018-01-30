from django.contrib import admin
from books.models import Books
# Register your models here.
admin.site.register(Books)#把Books注册到admin里面,方便管理,在后台编辑商品信息
