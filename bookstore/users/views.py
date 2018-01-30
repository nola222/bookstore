from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse,JsonResponse
import re
from users.models import Passport,Address
from order.models import OrderInfo,OrderBooks
from utils.decorators import login_required
#进行邮箱激活的需要导入的模板,是一个产生token的库  同步发送邮件
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from bookstore import settings
#itsdangerous 由flask的作者编写
from django.core.mail import send_mail
#在视图函数中导入异步任务
from users.tasks import send_active_email

# Create your views here.
def register(request):
    '''显示用户注册页面'''
    return render(request,'users/register.html')

#注册页面表单提交功能
def register_handle(request):
    '''进行用户注册处理'''
    #接收数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')

    #进行数据校验
    if not all([username,password,email]):
        #数据没有填,提示参数不能为空
        return render(request,'users/register.html',{'errmsg':'参数不能为空!'})

    #判断邮箱是否合法--正则
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        #邮箱不合法
        return render(request,'users/register.html',{'errmsg':'邮箱不合法!'})
    #进行业务处理:注册,向账户系统中添加数据
    p = Passport.objects.check_passport(username=username)
    if p:
        return render(request,'users/register.html',{'errmsg':'用户名已存在!'})
    passport = Passport.objects.add_one_passport(username=username,password=password,email=email)
    #生成激活的token itsdangerous
    serializer = Serializer(settings.SECRET_KEY,3600)
    token = serializer.dumps({'confirm': passport.id})
    token = token.decode()
    # 同步发送邮件
    # #给用户的邮箱发送激活邮件
    #send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email],html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)
    
    # 异步发送邮件
    send_active_email.delay(token, username, email)
    #注册完,还是返回注册页
    return redirect(reverse('books:index'))

def login(request):
    '''显示登录页面'''
    username = request.COOKIES.get('username','')
    print(username)
    checked = ''

    context = {
        'username' : username,
        'checked' : checked,
    }
    return render(request,'users/login.html',context)

def login_check(request):
    print(request)
    '''进行用户登录验证'''
    #1.获取数据
    username = request.POST.get('username')
    password = request.POST.get('password')
    remember = request.POST.get('remember')
    print(username,password,remember)
    #2.数据校验
    if not all([username,password,remember]):
        #数据为空
        return JsonResponse({'res':2})
    #3.根据用户名密码查找用户信息
    passport = Passport.objects.get_one_passport(username=username,password=password)

    if passport:
        #用户名密码正确
        #获取session中的url_path
        #if request.session.has_key('url_path'):
        #   next_url = request.session.get('url_path')
        #else:
        #   next_url = reverse('books:index')
        next_url = request.session.get('url_path',reverse('books:index'))
        jres = JsonResponse({'res':1,'next_url':next_url})
        #判断是否记住用户名
        if remember == 'true':
            jres.set_cookie('username',username,max_age=7*24*3600)
        else:
            jres.delete_cookie('username')
        #记住用户名的登录状态
        request.session['islogin'] = True
        request.session['username'] = username
        request.session['passport_id'] = passport.id
        return jres
    else:
        #用户名或者密码错误
        return JsonResponse({'res':0})

def logout(request):
    '''用户退出登录'''
    #清空用户session
    request.session.flush()
    #跳转到首页
    return redirect(reverse('books:index'))

@login_required
def user(request):
    #用户中心--信息页
    passport_id = request.session.get('passport_id')
    #获取用户基本信息
    addr = Address.objects.get_default_address(passport_id=passport_id)
    books_li = []#最近浏览记录
    context = {
        'addr':addr,
        'page':'user',
        'books_li':books_li
    }
    return render(request,'users/user_center_info.html',context)

@login_required
def address(request):
    print(11111111111)
    '''用户中心----地址页'''
    #获取用户登录的id
    passport_id = request.session.get('passport_id')
    if request.method == 'GET':
        #显示地址页
        #查询用户默认的收货地址
        addr = Address.objects.get_default_address(passport_id=passport_id)
        return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})
    else:
        #post请求 添加收货地址
        #接收数据
        recipient_name = request.POST.get('username')
        recipient_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone')

        #进行校验
        if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
            return render(request,'users/user_center_site.html',{'errmsg':'参数不能为空!'})
        else:
            #添加数据
            Address.objects.add_one_address(
                passport_id=passport_id,
                recipient_name=recipient_name,
                recipient_addr=recipient_addr,
                zip_code=zip_code,
                recipient_phone=recipient_phone,
            )
        #返回应答
        return redirect(reverse('user:address'))


@login_required
def order(request):
    '''用户中心订单页'''
    #查询用户订单信息
    passport_id = request.session.get('passport_id')
    #获取订单信息
    print(passport_id)
    order_li = OrderInfo.objects.filter(passport_id=passport_id)
    #遍历获取订单的商品信息  order ---> OrderInfo实例对象
    for order in order_li:
        #根据订单id查询订单商品信息
        order_id = order.order_id
        order_books_li = OrderBooks.objects.filter(order_id=order_id)

        #计算商品的小计  order_books ----> OrderBooks实例对象
        for order_books in order_books_li:
            count = order_books.count
            price = order_books.price
            amount = count * price
            #保存订单中每一个商品的小计
            order_books.amount = amount
        #给order动态添加一个属性order_books_li,保存订单中商品的信息
        order.order_books_li = order_books_li

    context = {
        'order_li' : order_li,
        'page' : 'order'
    }
    print(context)
    return render(request,'users/user_center_order.html',context)



    
