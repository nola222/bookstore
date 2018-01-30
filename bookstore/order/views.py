from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from utils.decorators import login_required
from django.http import HttpResponse,JsonResponse
from users.models import Address
from books.models import Books
from order.models import OrderInfo,OrderBooks
from django_redis import get_redis_connection
from datetime import datetime
from django.conf import settings
import time
import os
from books.enums import *
from django.db import transaction#事务


# Create your views here.
@login_required
def order_place(request):
    print(111111)
    '''显示提交订单页面'''
    #接收数据
    books_ids = request.POST.getlist('books_ids')
    #校验数据
    if not all(books_ids):
        #跳转到购物车页面
        return redirect(reverse('cart:show'))
    #获取用户收货地址
    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_default_address(passport_id=passport_id)
    #初始化用户购买商品信息
    books_li = []
    #用户购买商品的总数量和金额
    total_price = 0
    total_count = 0

    #与redis建立链接
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' %passport_id

    for id in books_ids:
        #根据id获得商品信息
        books = Books.objects.get_books_by_id(books_id=id)
        #从redis中获取用户要购买商品的数目
        count = conn.hget(cart_key,id)
        books.count = count#设置属性
        #计算商品小计
        amount = int(count) * books.price
        books.amount = amount
        #讲书添加到订单商品列表里
        books_li.append(books)
        #累计计算商品的总数目和总金额
        total_count += int(count)
        total_price += books.amount
    #商品运费和实付款 --> 这里设置运费默认10元
    transit_price = 10
    total_pay = total_price + transit_price

    #1,2,3     ---->  ','.join([1,2,3])将列表以逗号分隔为字符串
    books_ids = ','.join(books_ids)
    #组织模板上下文
    context = {
        'addr':addr,
        'books_li':books_li,
        'total_count':total_count,
        'total_price':total_price,
        'transit_price':transit_price,
        'total_pay':total_pay,
        'books_ids':books_ids,
    }

    #使用模板
    return render(request,'order/place_order.html',context)

#提交订单需要向两张表中添加信息
'''
s_order_info:订单信息表添加一条
s_order_books:订单商品表,订单中买几条商品,添加几条信息
前端需要提交过来的数据 :地址 支付方式 商品id
1.向订单表中添加一条数据
2.遍历向订单表中添加的信息
    2.1 添加订单商品信息之后,增加商品销量,减少库存
    2.2 累计计算商品的总数目和总金额
3.更新订单商品的总数目和总金额
4.清除购物车信息
'''
#用到事务
'''
事务:原子性,一组sql操作,要么成功,要么失败
开启事务:begin
事务回滚:rollback
事务提交:commit
设置保存点:savepoint 保存点
回滚到保存点:rollback to 保存点
'''
@transaction.atomic#原子性
def order_commit(request):
    '''生成订单'''
    #验证门户是否登录
    if not request.session.has_key('islogin'):
        return JsonResponse({'res':0,'errmsg':'用户未登录'})

    #接收数据
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    books_ids = request.POST.get('books_ids')
    #进行数据校验
    if not all([addr_id,pay_method,books_ids]):
        return JsonResponse({'res':1,'errmsg':'数据不完整'})
    try:
        addr = Address.objects.get(id=addr_id)
    except Exception as e:
        return JsonResponse({'res':2,'errmsg':'地址信息错误'})
    if int(pay_method) not in PAY_METHODS_ENUM.values():
        return JsonResponse({'res':3,'errmsg':'不支持的支付方式'})
    #订单创建  组织订单信息
    passport_id = request.session.get('passport_id')
    #订单id: 当前时间字符串格式 + 账户id
    order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(passport_id)
    print(passport_id,order_id)
    #初始化数据
    #运费
    transit_price = 10
    #订单商品总数目和总金额
    total_count = 0
    total_price = 0
    #创建一个保存点
    sid = transaction.savepoint()
    print(sid)
    #向订单表中添加一条信息
    try:
        order = OrderInfo.objects.create(
            order_id=order_id,
            passport_id=passport_id,
            pay_method=pay_method,
            addr_id=addr_id,
            transit_price=transit_price,
            total_count=total_count,
            total_price=total_price
        )
        print(order)
        #向订单商品信息表中添加商品的记录
        books_ids = books_ids.split(',')
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' %passport_id

        #遍历获取用户购买的商品信息
        for id in books_ids:
            books = Books.objects.get_books_by_id(books_id=id)
            #判断书是否存在
            if books is None:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':4,'errmsg':'商品信息错误'})
            #获取用户购买的商品数目
            count = conn.hget(cart_key,id)
            
            #判断书的库存
            if int(count) > books.stock:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':5,'errmsg':'商品库存不足'})

            #创建一条订单的商品记录
            OrderBooks.objects.create(
                order_id=order_id,
                books_id=id,
                count=count,
                price=books.price
            )

            #增加商品的销量,减少商品的库存
            books.sales += int(count)
            books.stock -= int(count)
            books.save()
            print(books.sales)

            #累计计算商品的总数目和总金额
            total_count += int(count)
            total_price += int(count) * books.price

        #更新订单的商品总数目和总金额
        order.total_count = total_count
        order.total_price = total_price
        order.save()
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res':7,'errmsg':'服务器报错'})
    
    #清除购物车信息
    conn.hdel(cart_key,*books_ids)
    #事务提交
    transaction.savepoint_commit(sid)
    #返回应答
    return JsonResponse({'res':6})


    
