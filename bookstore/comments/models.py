from django.db import models
from db.base_model import BaseModel
from users.models import Passport
from books.models import Books

# Create your models here.
class Comments(BaseModel):
    disabled = models.BooleanField(default=False,verbose_name='禁用评论')
    #谁评论的 谁与评论是一对多  一个用户可以写多条评论
    user = models.ForeignKey('users.Passport',verbose_name='用户id')
    #评论那本书 书与评论也是一对多 一本书可以有多条评论
    book = models.ForeignKey('books.Books',verbose_name='书籍id')
    content = models.CharField(max_length=1000,verbose_name='评论内容')

    class Meta:
        db_table = 's_comment_table'
