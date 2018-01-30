PYTHON = 1
JAVASCRIPT = 2
ALGORITHMS = 3
MACHINELEARNING = 4
OPERATINGSYSTEM = 5
DATABASE = 6

BOOKS_TYPE = {
    PYTHON : 'python',
    JAVASCRIPT : 'javascript',
    ALGORITHMS : '数据结构与算法',
    MACHINELEARNING : '机器学习',
    OPERATINGSYSTEM : '操作系统',
    DATABASE : '数据库'
}

OFFLINE = 0
ONLINE = 1

STATUS_CHOICE = {
    OFFLINE : '下线',
    ONLINE : '上线',
}

#订单模块常量
PAY_METHOD_CHOICES = (
    (1,'货到付款'),
    (2,'微信支付'),
    (3,'支付宝'),
    (4,'银联支付'),
)

PAY_METHODS_ENUM = {
    'CASH' : 1,
    'WEIXIN' : 2,
    'ALIPAY' : 3,
    'UNIONPAY' : 4,
}

ORDER_STATUS_CHOICES = (
    (1,'待支付'),
    (2,'待发货'),
    (3,'待收货'),
    (4,'待评价'),
    (5,'已完成'),
)
