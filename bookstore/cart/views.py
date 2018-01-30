from django.shortcuts import render
from django.http import JsonResponse
from books.models import Books
from utils.decorators import login_required
from django_redis import get_redis_connection

# Create your views here.
#前端发过来的数据 [商品id]-books_id [商品数量]-books_count  使用post方式修改数据(购物车)
def cart_add(request):
    '''向购物车添加数据'''
    #先判断用户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'请先登录'})
    #接收数据
    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')
    #进行数据校验
    if not all([books_id,books_count]):
        return JsonResponse({'res':1,'errmsg':'数据不完整'})
    #通过id获取用户选的书 判断是否存在这个id的书
    books = Books.objects.get_books_by_id(books_id=books_id)
    if books is None:
        #商品不存在
        return JsonResponse({'res':2,'errmsg':'商品不存在'})
    #try一下用户输入的购买数量
    try:
        count = int(books_count)
    except Exception as e:
        #商品数码不合法
        return JsonResponse({'res':3,'errmsg':'商品梳理必须为数字'})
    #添加商品到购物车
    #每个用户的购物车记录用一条hash数据保存,格式:cart_用户id:商品id 商品数量
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' %request.session.get('passport_id')
    #购物车信息 从redis中取出  redis的hash用法 cart_key--hash表名  books_id--key  -->值(count)
    res = conn.hget(cart_key,books_id)
    if res is None:
        #如果购物车没有添加过数据,则添加数量
        res = count
    else:
        #如果购物车已存在该商品数量,则是累加
        res = int(res) + count
    #判断用户选择的书的数量是否有库存
    if res > books.stock:
        #库存不足
        return JsonResponse({'res':4,'errmsg':'库存不足'})
    else:
        #将用户添加到购物车的信息保存到redis
        conn.hset(cart_key,books_id,res)
    #返回添加成功
    return JsonResponse({'res':5})

#实现登陆后可以看到购物车数量
def cart_count(request):
    '''获取用户购物车中商品的数量'''
    #判断用户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0})
    #计算用户购物车的数量
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' %request.session.get('passport_id')
    res = 0
    for i in conn.hvals(cart_key):
        res += int(i)
    #返回结果 去前端调用这个接口
    return JsonResponse({'res':res})

@login_required
def cart_show(request):
    '''显示用户购物车页面'''
    passport_id = request.session.get('passport_id')
    #获取用户购物车的记录
    #连接到setting里设置的redis第二个数据库 使用原生redis客户端 通过这个函数获得可重用的连接字符串
    conn = get_redis_connection('default')#进阶特性,不是所有扩展客户端都支持
    cart_key = 'cart_%d' %passport_id
    #购物车所有商品id及数量
    res_dict = conn.hgetall(cart_key)
    #购物车书籍列表
    books_li = []
    #保存所有商品的总数
    total_count = 0
    #保存所有商品的总价格
    total_price = 0
    #遍历res_dict字典获取商品的数据
    for id,count in res_dict.items():
        #根据id获取书的信息
        books = Books.objects.get_books_by_id(books_id=id)
        #保存商品的数目
        books.count = count
        #保存商品的小计
        books.amount = int(count) * books.price
        books_li.append(books)#从数据库中取出数据列出

        #进行计算总数和总价
        total_count += int(count)
        total_price += int(count) * books.price 
    #定义上下文模板
    context = {
        'books_li':books_li,
        'total_count':total_count,
        'total_price':total_price,
    }
    return render(request,'cart/cart.html',context)

#前端传过来的数据 商品id - books_id
#post   /cart/del/
def cart_del(request):
    '''删除用户购物车中的商品'''
    #判断用户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'请先登录'})
    #接收数据
    books_id = request.POST.get('books_id')
    #检验商品是否存放 -- 在不在books_id中
    if not all([books_id]):
        return JsonResponse({'res':0,'errmsg':'数据不完整'})

    #检验删除的书是否存在
    books = Books.objects.get_books_by_id(books_id=books_id)
    if books is None:
        return JsonResponse({'res':2,'errmsg':'商品不存在'})
    #删除购物车商品信息
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' %request.session.get('passport_id')
    conn.hdel(cart_key,books_id)
    return JsonResponse({'res':3})

#前端传过来的参数 商品id:books_id 更新数目 books_count
#/cart/update/
#post
def cart_update(request):
    
    '''更新购物车商品数目'''
    #判断用户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'请先登录'})
    #接收数据
    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')
    print(books_id,books_count)
    #检验商品是否存放 -- 在不在books_id中
    if not all([books_id,books_count]):
        return JsonResponse({'res':0,'errmsg':'数据不完整'})

    #检验删除的书是否存在
    books = Books.objects.get_books_by_id(books_id=books_id)
    if books is None:
        return JsonResponse({'res':2,'errmsg':'商品不存在'})
    try:
        books_count = int(books_count)
    except Exception as e:
        return JsonResponse({'res':2,'errmsg':'商品数目必须为数字'})
    #更新操作
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' %request.session.get('passport_id')
    #判断商品库存
    if books_count > books.stock:
        return JsonResponse({'res':4,'errmsg':'商品库存不足'})
    conn.hset(cart_key,books_id,books_count)
    return JsonResponse({'res':5})

    


        


        


