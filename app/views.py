# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask import render_template, request, redirect, url_for, flash, session
from jinja2 import TemplateNotFound
import time
import random

# App modules
from app import app, cursor, dbConn

# from app.models import Profiles

# TODO test.html用于检测生成数据，项目完成后需删除


# 定义在下文中使用的函数
def is_login():
    """
    用于检测用户的登陆状态,返回一个bool值,需要在除index页面之外调用
    由于检测对象为username 和 email, 在用户登陆后存储在session中的对应字段应为“username” 和 “email”
    """
    if "username" in session and "email":
        return True
    else:
        return False


def create_rid():
    """
    此函数用于生成一个随机的rid，生成方式为时间戳+随机数。但是依旧存在重复可能性。
    在下文中调用该函数时，请查询当前数据库中的全部rid，判断其值是否重复，若重复请重新生成
    """
    timestamp = int(time.time() * 1000)
    random_factor = random.randint(0, 1000)
    return int(f"{timestamp}{random_factor}")


def create_raid():
    """
    此函数功能和使用方法与create_rid相同
    """
    timestamp = int(time.time() * 1000)
    random_factor = random.randint(1001, 2000)
    return int(f"{timestamp}{random_factor}")


def create_pid():
    """
    同上
    """
    timestamp = int(time.time() * 1000)
    random_factor = random.randint(2001, 3000)
    return int(f"{timestamp}{random_factor}")


# App main route + generic routing
@app.route("/")
def index():
    session['username'] = 'nihao'   # TODO测试使用，需删除
    return render_template("index.html")


@app.route("/order_detials")
def order_page():
    return render_template("order_1.html")

@app.route("/login")
def login():
    return render_template("Log_in.html")


@app.route("/register")
def register():
    return render_template("create_profile.html")


@app.route("/test")
def test():
    rid = create_rid()
    raid = create_raid()
    pid = create_pid()
    return render_template("test.html", rid=rid, raid=raid, pid=pid)


@app.route("/payment")
def payment():
    return render_template("payment_details.html")


@app.route("/searchpayment", methods=["GET"])
# TODO 数据库查询语句有问题，三连表查询报错
def SearchPayment():
    user = request.args.get("user")
    print(user)

    if user:
        sql = "select OrderRequest.Email, OrderTakerEmail, pid, paidtime, paymethod, actualpay, note from Payment inner join OrderAcceptance on Payment.raid = OrderAcceptance.raid inner join OrderRequest on OrderAcceptance.rid = OrderRequest.rid where OrderRequest.Email = %s"
        cursor.execute(sql, (user))
        data = cursor.fetchall()
        print(data)
        return render_template("payment_details.html", data=data)

    return render_template("index.html")
