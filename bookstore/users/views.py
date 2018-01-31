from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse,JsonResponse
import re
from django_redis import get_redis_connection
from books.models import Books
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
    verifycode = request.POST.get('verifycode')

    # 2.数据校验
    if not all([username, password, remember, verifycode]):
        # 有数据为空
        return JsonResponse({'res': 2})
       
    # 和session的比较，对了就返回true
    if verifycode != request.session.get('verifycode', 'error'):
        return JsonResponse({'res': 2})

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

    #获取用户最近的浏览记录
    con = get_redis_connection('default')
    key = 'history_%d' %passport_id
    #取出用户最近浏览5个商品的id
    history_li = con.lrange(key,0,4)
    books_li = []#最近浏览记录
    for id in history_li:
        books = Books.objects.get_books_by_id(books_id=id)
        books_li.append(books)
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

#登录验证码功能实现
# from django.http import HttpResponse
# def verifycode(request):
#     print('enter---------')
#     #引入绘图模块
#     from PIL import Image, ImageDraw, ImageFont
#     #引入随机函数模块
#     import random
#     #定义变量，用于画面的背景色、宽、高
#     bgcolor = (random.randrange(20, 100), random.randrange(
#         20, 100), 255)
#     width = 100
#     height = 25
#     print(bgcolor)
#     #创建画面对象
#     im = Image.new('RGB', (width, height), bgcolor)
#     print(im)
#     #创建画笔对象
#     draw = ImageDraw.Draw(im)
#     #调用画笔的point()函数绘制噪点
#     for i in range(0, 100):
#         xy = (random.randrange(0, width), random.randrange(0, height))
#         fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
#         draw.point(xy, fill=fill)
#     #定义验证码的备选值
#     str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
#     #随机选取4个值作为验证码
#     rand_str = ''
#     for i in range(0, 4):
#         rand_str += str1[random.randrange(0, len(str1))]
#     print(rand_str)
#     #构造字体对象
#     font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
#     #构造字体颜色
#     fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
#     #绘制4个字
#     draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
#     draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
#     draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
#     draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
#     #释放画笔
#     del draw
#     #存入session，用于做进一步验证
#     request.session['verifycode'] = rand_str
#     #内存文件操作
#     import io
#     buf = io.BytesIO()
#     print('buf------',buf)
#     #将图片保存在内存中，文件类型为png
#     im.save(buf, 'png')
#     print(buf.getvalue())
#     #将内存中的图片数据返回给客户端，MIME类型为图片png
#     return HttpResponse(buf.getvalue(), 'image/png')
from django.shortcuts import  HttpResponse
from PIL import Image, ImageDraw,  ImageFont
import random
import string
from io import BytesIO


# 生成随机字符串
def getRandomChar():
    # string模块包含各种字符串，以下为小写字母加数字
    ran = string.ascii_lowercase + string.digits
    char = ''
    for i in range(4):
        char += random.choice(ran)
    return char


# 返回一个随机的RGB颜色
def getRandomColor():
    return (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))


def create_code():
    # 创建图片，模式，大小，背景色
    img = Image.new('RGB', (130, 30), getRandomColor())
    # 创建画布
    draw = ImageDraw.Draw(img)
    # 设置字体, ubuntu 字体在/usr/share/fonts/truetype/freefont
    # Wind字体放在C:\Windows\Fonts， 使用的是bahnschrift.ttf
    font = ImageFont.truetype('DejaVuSans.ttf', 15)
    # 生成字符串

    code = getRandomChar()
    # 将生成的字符画在画布上
    for t in range(4):
        # 在画布上写字符串， 随机颜色
        draw.text((30 * t + 5, 0), code[t], getRandomColor(), font)

    # 生成干扰点
    for _ in range(random.randint(0, 50)):
        # 位置，颜色
        draw.point((random.randint(0, 120), random.randint(0, 30)), fill=getRandomColor())
    return img, code


# 生成验证码
def verifycode(request):
    f = BytesIO()
    img, code = create_code()
    request.session['verifycode'] = code
    img.save(f, 'PNG')
    # 定义cont_type相应内容为
    return HttpResponse(f.getvalue(), 'image/png')
                                                    
                            
