from django.conf.urls import url
from cart import views

urlpatterns = [
    url(r'^add/$',views.cart_add,name='add'),#添加购物车数据
    url(r'^count/$',views.cart_count,name='count'),#显示购物车数量
    url(r'^$',views.cart_show,name='show'),#显示购物车
    url(r'^del/$',views.cart_del,name='delete'),#删除购物车商品记录
    url(r'^update/$',views.cart_update,name='update'),#购物车页面更新商品数据
]
