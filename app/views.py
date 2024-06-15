# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask import render_template, request, redirect, url_for, flash, session,jsonify
from jinja2 import TemplateNotFound
import time
import random
from datetime import datetime
import logging

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


@app.route("/order_details")
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


@app.route("/payment_details")
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

@app.route('/chooseOrder')
def chooseOrder():
    sql = "SELECT * FROM OrderRequest"
    cursor.execute(sql)
    OrderAcc = cursor.fetchall()
    return render_template('order_1.html',OrderAcc=OrderAcc)



@app.route('/order_details/<int:order_id>')
def order_details(order_id):
    sql = "SELECT * FROM OrderRequest WHERE rid = %s"
    cursor.execute(sql, (order_id,))
    order = cursor.fetchone()
    return render_template('order_details.html', order=order)

@app.route('/accept_order', methods=['POST'])
def accept_order():
    data = request.get_json()
    print("Received data:", data)  # 打印接收到的数据
    order_id = data.get('orderId')
    acceptance_time = datetime.fromisoformat(data.get('acceptanceTime').replace('Z', '+00:00'))
    receiving = 1
    email = data.get('email')

    if not order_id or not acceptance_time or not email:
        print("Missing data:", {'order_id': order_id, 'acceptance_time': acceptance_time, 'email': email})  # 打印缺失的数据
        return jsonify({'error': 'Missing data'}), 400
    else:
        try:
            print("Inserting into OrderAcceptance table:", {'order_id': order_id, 'acceptance_time': acceptance_time, 'email': email})  # 打印插入 OrderAcceptance 表的数据
            sql = "INSERT INTO OrderAcceptance (rid, AcceptanceTime, OrderTakerEmail) VALUES (%s, %s, %s)"
            cursor.execute(sql, (order_id, acceptance_time, email))
            print("Updating OrderRequest table:", {'receiving': receiving, 'order_id': order_id})  # 打印更新 OrderRequest 表的数据
            sql = "UPDATE OrderRequest SET Receiving = %s WHERE rid = %s"
            cursor.execute(sql, (receiving, order_id))
            print("Redirecting to 'chooseOrder' page")  # 打印重定向操作
            return redirect(url_for('chooseOrder'))
        except Exception as e:
            print(f"Error: {e}")  # 打印错误信息
            return jsonify({'error': str(e)}), 500

@app.route('/searchResult', methods=['GET'])
def search_products_result():
    merchant = request.args.get('merchant')
    #retrieve the product records from the database for the given sid
    if merchant:
        sql="SELECT * FROM OrderRequest WHERE Merchant LIKE %s"
        cursor.execute(sql,('%'+merchant+'%',))
        result = cursor.fetchall()

        #send the product table back
        return render_template('productSearchResult.html',OrderAcc=result)
    sql2 = "SELECT * FROM OrderRequest"
    cursor.execute(sql2)
    OrderAcc = cursor.fetchall()
    return render_template('Result.html',OrderAcc=OrderAcc)

@app.route('/accept')
def accept():
    sql = "SELECT * FROM OrderAcceptance oa INNER JOIN OrderRequest orq ON oa.rid = orq.rid;"
    cursor.execute(sql)
    OrderAcc = cursor.fetchall()
    return render_template('order_3.html',OrderAcc=OrderAcc)

@app.route('/cancelOrder', methods=['POST'])
def cancel_order():
    order_id = request.json.get('orderId')
    if order_id:
        sql="DELETE FROM OrderAcceptance WHERE rid = %s;"
        cursor.execute(sql,(order_id,))
        print("Order has been successfully canceled")
        return jsonify({'message': 'Order has been successfully canceled'})
    return jsonify({'message': 'Order Cancellation Failed'})

# 定义一个路由，用于处理定时轮询请求
@app.route('/checkForUpdates')
def check_for_updates():
    global updates_available
    if updates_available:
        # 如果有更新，则返回更新信息
        return jsonify({'updatesAvailable': True})
    else:
        # 如果没有更新，则返回没有更新的信息
        return jsonify({'updatesAvailable': False})















