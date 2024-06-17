# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    json,
)
from jinja2 import TemplateNotFound
import time
import random
from datetime import datetime
import logging

# App modules
from app import app, cursor, dbConn

# from app.models import Profiles

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


# App main route + generic routing
@app.route("/")
def index():
    session["email"] = "1"
    session["username"] = "nihao"  # TODO测试使用，需删除

    return render_template("index.html")


@app.route("/order_1")
def order_page():
    return render_template("order_1.html")


@app.route("/order_details")
def order_page():
    return render_template("order_1.html")


@app.route("/login")
def login():
    return render_template("Log_in.html")


@app.route("/loginsubmit", methods=["POST"])
def loginsubmit():
    inputemail = request.form.get("inputemail")
    pswd = request.form.get("pswd")
    error = False
    sql = "use misy410group07"
    cursor.execute(sql)
    sql = "select * from UserProfile where Email = %s"
    cursor.execute(sql, inputemail)
    input = cursor.fetchone()

    if not input:
        error = True
        flash("email not found")

    if error:
        return render_template("Log_in.html", inputemail=inputemail, pswd=pswd)
    elif pswd == input["uPassword"]:
        session["email"] = inputemail
        session["password"] = pswd
        return redirect("/")
    else:
        flash("wrong password")
        return render_template("Log_in.html", inputemail=inputemail, pswd=pswd)


@app.route("/register")
def register():
    return render_template("create_profile.html")


@app.route("/payment_details")
def payment():
    email = session["email"]

    if email:
        sql = """SELECT OrderRequest.Email, OrderTakerEmail, pid, paidtime, paymethod, actualpay, note
                 FROM Payment
                 INNER JOIN OrderAcceptance ON Payment.raid = OrderAcceptance.raid
                 INNER JOIN OrderRequest ON OrderAcceptance.rid = OrderRequest.rid
                 WHERE OrderRequest.Email = %s"""
        cursor.execute(sql, (email,))
        data = cursor.fetchall()
        print(data)

    return render_template("payment_details.html", data=data)


@app.route("/chooseOrder")
def chooseOrder():
    sql = "SELECT * FROM OrderRequest"
    cursor.execute(sql)
    OrderAcc = cursor.fetchall()
    return render_template("order_1.html", OrderAcc=OrderAcc)


@app.route("/order_details/<int:order_id>")
def order_details(order_id):
    sql = "SELECT * FROM OrderRequest WHERE rid = %s"
    cursor.execute(sql, (order_id,))
    order = cursor.fetchone()
    return render_template("order_details.html", order=order)


@app.route("/accept_order", methods=["POST"])
def accept_order():
    data = request.get_json()
    print("Received data:", data)  # 打印接收到的数据
    order_id = data.get("orderId")
    acceptance_time = datetime.fromisoformat(
        data.get("acceptanceTime").replace("Z", "+00:00")
    )
    receiving = 1
    email = data.get("email")

    if not order_id or not acceptance_time or not email:
        print(
            "Missing data:",
            {"order_id": order_id, "acceptance_time": acceptance_time, "email": email},
        )  # 打印缺失的数据
        return jsonify({"error": "Missing data"}), 400
    else:
        try:
            print(
                "Inserting into OrderAcceptance table:",
                {
                    "order_id": order_id,
                    "acceptance_time": acceptance_time,
                    "email": email,
                },
            )  # 打印插入 OrderAcceptance 表的数据
            sql = "INSERT INTO OrderAcceptance (rid, AcceptanceTime, OrderTakerEmail) VALUES (%s, %s, %s)"
            cursor.execute(sql, (order_id, acceptance_time, email))
            print(
                "Updating OrderRequest table:",
                {"receiving": receiving, "order_id": order_id},
            )  # 打印更新 OrderRequest 表的数据
            sql = "UPDATE OrderRequest SET Receiving = %s WHERE rid = %s"
            cursor.execute(sql, (receiving, order_id))
            print("Redirecting to 'chooseOrder' page")  # 打印重定向操作
            return redirect(url_for("chooseOrder"))
        except Exception as e:
            print(f"Error: {e}")  # 打印错误信息
            return jsonify({"error": str(e)}), 500


@app.route("/searchResult", methods=["GET"])
def search_products_result():
    merchant = request.args.get("merchant")
    # retrieve the product records from the database for the given sid
    if merchant:
        sql = "SELECT * FROM OrderRequest WHERE Merchant LIKE %s"
        cursor.execute(sql, ("%" + merchant + "%",))
        result = cursor.fetchall()

        # send the product table back
        return render_template("productSearchResult.html", OrderAcc=result)
    sql2 = "SELECT * FROM OrderRequest"
    cursor.execute(sql2)
    OrderAcc = cursor.fetchall()
    return render_template("Result.html", OrderAcc=OrderAcc)


@app.route("/accept")
def accept():
    sql = "SELECT * FROM OrderAcceptance oa INNER JOIN OrderRequest orq ON oa.rid = orq.rid;"
    cursor.execute(sql)
    OrderAcc = cursor.fetchall()
    return render_template("order_3.html", OrderAcc=OrderAcc)


@app.route("/cancelOrder", methods=["POST"])
def cancel_order():
    order_id = request.json.get("orderId")
    if order_id:
        sql = "DELETE FROM OrderAcceptance WHERE raid = %s;"
        cursor.execute(sql, (order_id,))
        print("Order has been successfully canceled")
        return jsonify({"message": "Order has been successfully canceled"})
    return jsonify({"message": "Order Cancellation Failed"})


# 定义一个路由，用于处理定时轮询请求


@app.route("/accData")
def accData():
    sql = "SELECT * FROM OrderAcceptance"
    cursor.execute(sql)
    accData = cursor.fetchall()
    return render_template("acceptance_data.html", accData=accData)


@app.route("/get_chart_data", methods=["POST"])
def get_chart_data():
    time_range = request.form.get("timeRange")

    if not time_range:
        return jsonify({"error": "Missing time range"}), 400

    try:
        if time_range == "day":
            sql = "SELECT DATE_FORMAT(AcceptanceTime, '%Y-%m-%d') AS label, COUNT(*) AS value FROM OrderAcceptance GROUP BY DATE_FORMAT(AcceptanceTime, '%Y-%m-%d') ORDER BY label"
            grouping = "day"
        elif time_range == "week":
            sql = "SELECT YEARWEEK(AcceptanceTime) as label, COUNT(*) as value FROM OrderAcceptance GROUP BY YEARWEEK(AcceptanceTime)"
            grouping = "week"
        elif time_range == "month":
            sql = "SELECT DATE_FORMAT(AcceptanceTime, '%Y-%m') as label, COUNT(*) as value FROM OrderAcceptance GROUP BY DATE_FORMAT(AcceptanceTime, '%Y-%m')"
            grouping = "month"
        else:
            return jsonify({"error": "Invalid time range"}), 400

        cursor.execute(sql)
        results = cursor.fetchall()
        chartData = json.dumps(results)
        group = grouping
        print("OK!!!")
        print(results)
        return render_template("acceptance_dataview.html", acc=chartData, group=group)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/selectRange", methods=["GET"])
def SearchProducts():
    # 获取 GET 请求中的参数
    time_range = request.args.get("timeRange")
    user = request.args.get("user")
    print(user)

    try:
        # 基于 time_range 构建 SQL 查询
        if time_range == "day":
            base_sql = "SELECT DATE_FORMAT(AcceptanceTime, '%%Y-%%m-%%d') AS label, COUNT(*) AS value FROM OrderAcceptance"
            grouping = "day"
        elif time_range == "week":
            base_sql = """
            SELECT DATE_FORMAT(AcceptanceTime, '%%x-%%v') AS label, COUNT(*) AS value 
            FROM OrderAcceptance"""
            grouping = "week"
        elif time_range == "month":
            base_sql = "SELECT DATE_FORMAT(AcceptanceTime, '%%Y-%%m') AS label, COUNT(*) AS value FROM OrderAcceptance"
            grouping = "month"
        else:
            return jsonify({"error": "Please select a time range"}), 400

        # 添加用户筛选条件
        if user and user != "all":
            base_sql += " WHERE OrderTakerEmail = %s"
            sql_params = (user,)
            print(sql_params)
            print(base_sql)
        else:
            sql_params = ()

        # 添加 GROUP BY 和 ORDER BY 子句
        if time_range == "day":
            base_sql += " GROUP BY label ORDER BY label"
        elif time_range == "week":
            base_sql += " GROUP BY label ORDER BY label"
        elif time_range == "month":
            base_sql += " GROUP BY label ORDER BY label"

        print(base_sql)
        print(sql_params)
        # 执行 SQL 查询
        cursor.execute(base_sql, sql_params)
        print("Fine")
        results = cursor.fetchall()
        print(results)
        chartData = json.dumps(results)
        group = grouping

        print("OK!!!")
        print(results)

        return render_template("acceptance_dataview.html", acc=chartData, group=group)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 发送食品订单
@app.route("/food_order")
def food_order():
    if is_login():
        return render_template("food_order.html")
    else:
        return redirect("/login")


@app.route("/ordersubmit", methods=["POST"])
def OrderSubmit():
    # Get the user input values from the form
    inputemail = session.get("email")
    detime = request.form.get("detime")
    tele = request.form.get("tele")
    oraddress = request.form.get("oraddress")
    deaddress = request.form.get("deaddress")
    mname = request.form.get("mname")
    apay = request.form.get("apay")
    content = request.form.get("content")
    error = False
    Order_time = datetime.now()
    # input validation
    if float(apay) < 0 or float(apay) > 1000:
        error = True
        flash("payment should be a number > 0 and < 1000")
    if not mname:
        error = True
        flash("Please select Merchant")
    if error:
        # return to the form page
        return render_template(
            "food_order.html",
            content=content,
            detime=detime,
            tele=tele,
            oraddress=oraddress,
            deaddress=deaddress,
            mname=mname,
            apay=apay,
        )

    else:
        # do the database operations
        sql = "use misy410group07"
        cursor.execute(sql)
        sql = "insert into OrderRequest (RequestTime, RequestContent, DeliveryTime, OrderTelephone,PickupAddress,DeliveryAddress, Merchant, Email, AdvancePayment) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s)"

        cursor.execute(
            sql,
            (
                Order_time,
                content,
                detime,
                int(tele),
                oraddress,
                deaddress,
                mname,
                inputemail,
                float(apay),
            ),
        )
        flash("order successfully")
        return render_template("food_order.html")


# 发送产品订单————————————————————————————————————————————————————————————————————————————————————————————————————————————————
@app.route("/product_order")
def product_order():
    if is_login():
        return render_template("product_order.html")
    else:
        return redirect("/login")


@app.route("/productOrdersubmit", methods=["POST"])
def ProductOrderSubmit():
    # Get the user input values from the form
    inputemail = session.get("email")
    detime = request.form.get("detime")
    tele = request.form.get("tele")
    oraddress = request.form.get("oraddress")
    deaddress = request.form.get("deaddress")
    mname = request.form.get("mname")
    apay = request.form.get("apay")
    content = request.form.get("content")
    order_type = "1"
    error = False
    Order_time = datetime.now()
    # input validation
    if float(apay) < 0 or float(apay) > 1000:
        error = True
        flash("payment should be a number > 0 and < 1000")
    if not mname:
        error = True
        flash("Please select goods")
    if error:
        # return to the form page
        return render_template(
            "product_order.html",
            content=content,
            detime=detime,
            tele=tele,
            oraddress=oraddress,
            deaddress=deaddress,
            mname=mname,
            apay=apay,
        )

    else:
        # do the database operations
        sql = "use misy410group07"
        cursor.execute(sql)
        sql = "insert into OrderRequest (RequestTime, RequestContent, DeliveryTime, OrderTelephone,PickupAddress,DeliveryAddress, Merchant, Email, AdvancePayment, Type) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s)"

        cursor.execute(
            sql,
            (
                Order_time,
                content,
                detime,
                int(tele),
                oraddress,
                deaddress,
                mname,
                inputemail,
                float(apay),
                order_type,
            ),
        )
        flash("order successfully")
        return render_template("product_order.html")


# 我发送的订单——————————————————————————————————————————————
@app.route("/order_2")
def order_2():
    if is_login():
        information = session.get("email")
        sql = "use misy410group07"
        cursor.execute(sql)
        sql = "select * from OrderRequest where Email = %s"
        cursor.execute(sql, information)
        oRequests = cursor.fetchall()
        if oRequests:
            return render_template(
                "order_2.html", information=information, oRequests=oRequests
            )
        else:
            flash("no requests")

    else:
        return redirect("/login")


# 修改食物订单——————————————————————————————————————————————————————————
@app.route("/modify_order", methods=["POST"])  # modify my post
def modify_order():
    rid = request.form.get("rid")
    sql = "use misy410group07"
    cursor.execute(sql)
    sql = "select * from OrderRequest where rid = %s"
    cursor.execute(sql, rid)
    mInformation = cursor.fetchone()
    session["rid"] = rid
    return render_template("modify_food_order.html", mInformation=mInformation)


# 修改产品订单——————————————————————————————————————————————————————————————
@app.route("/modify_order_product", methods=["POST"])  # modify my post
def modify_product_order():
    rid = request.form.get("rid")
    sql = "use misy410group07"
    cursor.execute(sql)
    sql = "select * from OrderRequest where rid = %s"
    cursor.execute(sql, rid)
    mInformation = cursor.fetchone()
    session["rid"] = rid
    return render_template("modify_product_order.html", mInformation=mInformation)


# 提交修改食物订单需求————————————————————————————————————————————————————
@app.route("/modifyordersubmit", methods=["POST"])
def modifysubmit():
    error = False
    detime = request.form.get("detime")
    tele = request.form.get("tele")
    oraddress = request.form.get("oraddress")
    deaddress = request.form.get("deaddress")
    mname = request.form.get("mname")
    apay = request.form.get("apay")
    content = request.form.get("content")

    rid = session.get("rid")
    sql = "use misy410group07"
    cursor.execute(sql)
    sql = "select * from OrderRequest where rid = %s"
    cursor.execute(sql, rid)
    mInformation = (
        cursor.fetchone()
    )  ##这里有点问题，if error不知道怎么返回重新输入后的值

    if float(apay) < 0 or float(apay) > 1000:
        error = True
        flash("payment should be a number > 0 and < 1000")

    if error:
        # return to the form page
        return render_template(
            "modify_food_order.html",
            content=content,
            detime=detime,
            tele=tele,
            oraddress=oraddress,
            deaddress=deaddress,
            mname=mname,
            apay=apay,
            mInformation=mInformation,
        )

    else:
        sql = "update OrderRequest set RequestContent= %s , DeliveryTime= %s, OrderTelephone=%s ,PickupAddress=%s,DeliveryAddress=%s, Merchant=%s, AdvancePayment=%s where rid=%s"
        cursor.execute(
            sql,
            (content, detime, int(tele), oraddress, deaddress, mname, float(apay), rid),
        )
        flash("updated successfully")
        return render_template("modify_food_order.html", mInformation=mInformation)


# 提交产品订单修改需求————————————————————————————————————————————————————————
@app.route("/modifyproductsubmit", methods=["POST"])
def modifyproductsubmit():
    error = False
    detime = request.form.get("detime")
    tele = request.form.get("tele")
    oraddress = request.form.get("oraddress")
    deaddress = request.form.get("deaddress")
    mname = request.form.get("mname")
    apay = request.form.get("apay")
    content = request.form.get("content")

    rid = session.get("rid")
    sql = "use misy410group07"
    cursor.execute(sql)
    sql = "select * from OrderRequest where rid = %s"
    cursor.execute(sql, rid)
    mInformation = (
        cursor.fetchone()
    )  ##这里有点问题，if error不知道怎么返回重新输入后的值

    if float(apay) < 0 or float(apay) > 1000:
        error = True
        flash("payment should be a number > 0 and < 1000")

    if error:
        # return to the form page
        return render_template(
            "modify_product_order.html",
            content=content,
            detime=detime,
            tele=tele,
            oraddress=oraddress,
            deaddress=deaddress,
            mname=mname,
            apay=apay,
            mInformation=mInformation,
        )

    else:
        sql = "update OrderRequest set RequestContent= %s , DeliveryTime= %s, OrderTelephone=%s ,PickupAddress=%s,DeliveryAddress=%s, Merchant=%s, AdvancePayment=%s where rid=%s"
        cursor.execute(
            sql,
            (content, detime, int(tele), oraddress, deaddress, mname, float(apay), rid),
        )
        flash("updated successfully")
        return render_template("modify_product_order.html", mInformation=mInformation)


# 取消订单————————————————————————————————————————————————————————————
@app.route("/deleteRequest", methods=["POST"])
def deleteRequest():
    rid = request.form.get("rid")
    sql = "use misy410group07"
    cursor.execute(sql)
    sql = "delete from OrderRequest where rid = %s"
    cursor.execute(sql, rid)
    return redirect("/order_2")


# order request可视化————————————————————————————————————————————
@app.route("/request_data")
def request_data():
    if is_login():
        sql = "select distinct Merchant from OrderRequest"
        cursor.execute(sql)  # is a table
        merchants = cursor.fetchall()
        return render_template("request_data.html", merchants=merchants)
    else:
        return redirect("/login")


@app.route("/RequestGraph", methods=["GET"])
def request_graph():
    mname = request.args.get("merchant")
    if mname:
        sql = "select Merchant as label, count(rid) as value from OrderRequest where Merchant = %s group by Merchant"
        cursor.execute(sql, (mname))
        merchants_view = cursor.fetchall()
        chartData = json.dumps(merchants_view)
        return render_template("request_graph.html", chartData=chartData)

    else:
        sql = "select Merchant as label, count(rid) as value from OrderRequest group by Merchant"
        cursor.execute(sql)
        merchants_view = cursor.fetchall()
        chartData = json.dumps(merchants_view)
        return render_template("request_graph.html", chartData=chartData)
