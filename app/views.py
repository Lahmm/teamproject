# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask import render_template, request, redirect, url_for, flash, session,json
from jinja2 import TemplateNotFound
from datetime import datetime
import time
import random

# App modules
from app import app, cursor, dbConn

# from app.models import Profiles

# TODO test.html用于检测生成数据，项目完成后需删除


# 定义在下文中使用的函数
#def is_login():
   # """
    #用于检测用户的登陆状态,返回一个bool值,需要在除index页面之外调用
    #由于检测对象为username 和 email, 在用户登陆后存储在session中的对应字段应为“username” 和 “email”
    #"""
    #if "username" in session and "email":
    #    return True
    #else:
    #    return False

#测试订单页session用，与上面的username有点冲突，到时候调整
#你们要用上面的函数测试的时候帮我把下面这个加注释一下
def is_login():
    if 'email' in session:
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


@app.route("/order_1")
def order_page():
    return render_template("order_1.html")

@app.route('/login')
def login(): 
    return render_template('Log_in.html')

@app.route('/loginsubmit', methods=['POST'])
def loginsubmit():
    inputemail =  request.form.get('inputemail')
    pswd =  request.form.get('pswd')
    error = False
    sql= 'use misy410group07'
    cursor.execute(sql)
    sql= 'select * from UserProfile where Email = %s'
    cursor.execute(sql,inputemail)
    input = cursor.fetchone()

    if not input:
          error = True
          flash('email not found')

    if error:
        return render_template("Log_in.html", inputemail=inputemail,pswd=pswd)
    elif pswd == input['uPassword']:
        session['email']=inputemail
        session['password']=pswd
        return redirect('/')
    else:
        flash('wrong password')
        return render_template("Log_in.html",inputemail=inputemail,pswd=pswd)
    

    


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



##发送食品订单————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
@app.route('/food_order')
def food_order():
 if is_login(): 
    return render_template('food_order.html')
 else:
    return redirect('/login')


@app.route('/ordersubmit', methods=['POST'])
def OrderSubmit():
# Get the user input values from the form
  inputemail = session.get('email')
  detime = request.form.get('detime')
  tele = request.form.get('tele')
  oraddress = request.form.get('oraddress')
  deaddress = request.form.get('deaddress')
  mname = request.form.get('mname')
  apay = request.form.get('apay')
  content = request.form.get('content')
  error = False
  Order_time = datetime.now()
 # input validation
  if float(apay) < 0 or float(apay) > 1000:
      error = True
      flash('payment should be a number > 0 and < 1000')
  if not mname:
      error = True
      flash('Please select Merchant')
  if error:
        #return to the form page
        return render_template('food_order.html',content=content,detime=detime,tele=tele,oraddress=oraddress, deaddress=deaddress,mname=mname,apay=apay)
    
  else:
#do the database operations
       sql= 'use misy410group07'
       cursor.execute(sql)
       sql = 'insert into OrderRequest (RequestTime, RequestContent, DeliveryTime, OrderTelephone,PickupAddress,DeliveryAddress, Merchant, Email, AdvancePayment) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s)'

       cursor.execute(sql,(Order_time,content,detime,int(tele),oraddress,deaddress,mname,inputemail,float(apay)))
       flash('order successfully')
       return render_template('food_order.html')

  
#发送产品订单————————————————————————————————————————————————————————————————————————————————————————————————————————————————
@app.route('/product_order')
def product_order():
    if is_login(): 
     return render_template('product_order.html')
    else:
     return redirect('/login')
 
    

@app.route('/productOrdersubmit',methods=['POST'])
def ProductOrderSubmit():
# Get the user input values from the form
  inputemail = session.get('email')
  detime = request.form.get('detime')
  tele = request.form.get('tele')
  oraddress = request.form.get('oraddress')
  deaddress = request.form.get('deaddress')
  mname = request.form.get('mname')
  apay = request.form.get('apay')
  content = request.form.get('content')
  order_type = '1'
  error = False
  Order_time = datetime.now()
 # input validation
  if float(apay) < 0 or float(apay) > 1000:
      error = True
      flash('payment should be a number > 0 and < 1000')
  if not mname:
      error = True
      flash('Please select goods')
  if error:
        #return to the form page
        return render_template('product_order.html',content=content,detime=detime,tele=tele,oraddress=oraddress, deaddress=deaddress,mname=mname,apay=apay)
    
  else:
#do the database operations
       sql= 'use misy410group07'
       cursor.execute(sql)
       sql = 'insert into OrderRequest (RequestTime, RequestContent, DeliveryTime, OrderTelephone,PickupAddress,DeliveryAddress, Merchant, Email, AdvancePayment, Type) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s)'

       cursor.execute(sql,(Order_time,content,detime,int(tele),oraddress,deaddress,mname,inputemail,float(apay),order_type))
       flash('order successfully')
       return render_template('product_order.html')
 
#我发送的订单
@app.route('/order_2')
def order_2():
   if is_login():
     information = session.get('email') 
     sql= 'use misy410group07'
     cursor.execute(sql)
     sql = 'select * from OrderRequest where Email = %s'
     cursor.execute(sql,information)
     oRequests = cursor.fetchall()
     if oRequests:
         return render_template('order_2.html',information=information,oRequests=oRequests)
     else:
         flash('no requests')
     
   else:
     return redirect('/login')

#修改食物订单
@app.route('/modify_order', methods=['POST'])  #modify my post
def modify_order():
  rid= request.form.get('rid')
  sql= 'use misy410group07'
  cursor.execute(sql)
  sql = 'select * from OrderRequest where rid = %s'
  cursor.execute(sql,rid)
  mInformation = cursor.fetchone()
  session ['rid']= rid
  return render_template('modify_food_order.html',mInformation=mInformation)
#修改产品订单
@app.route('/modify_order_product', methods=['POST'])  #modify my post
def modify_product_order():
  rid= request.form.get('rid')
  sql= 'use misy410group07'
  cursor.execute(sql)
  sql = 'select * from OrderRequest where rid = %s'
  cursor.execute(sql,rid)
  mInformation = cursor.fetchone()
  session ['rid']= rid
  return render_template('modify_product_order.html',mInformation=mInformation)

#提交修改食物订单需求
@app.route('/modifyordersubmit',methods=['POST'])
def modifysubmit():
  error = False
  detime = request.form.get('detime')
  tele = request.form.get('tele')
  oraddress = request.form.get('oraddress')
  deaddress = request.form.get('deaddress')
  mname = request.form.get('mname')
  apay =request.form.get('apay')
  content = request.form.get('content')

  rid = session.get('rid')
  sql= 'use misy410group07'
  cursor.execute(sql)
  sql = 'select * from OrderRequest where rid = %s'
  cursor.execute(sql,rid)
  mInformation = cursor.fetchone() ##这里有点问题，if error不知道怎么返回重新输入后的值
 
  if float(apay) < 0 or float(apay) > 1000:
       error = True
       flash('payment should be a number > 0 and < 1000')

  if error:
        #return to the form page
      return render_template('modify_food_order.html',content=content,detime=detime,tele=tele,oraddress=oraddress, deaddress=deaddress,mname=mname,apay=apay,mInformation=mInformation)

  else:
    sql = 'update OrderRequest set RequestContent= %s , DeliveryTime= %s, OrderTelephone=%s ,PickupAddress=%s,DeliveryAddress=%s, Merchant=%s, AdvancePayment=%s where rid=%s' 
    cursor.execute(sql,(content,detime,int(tele),oraddress,deaddress,mname,float(apay),rid))
    flash('updated successfully')
    return render_template('modify_food_order.html',mInformation=mInformation)
  
#提交产品订单修改需求
@app.route('/modifyproductsubmit',methods=['POST'])
def modifyproductsubmit():
  error = False
  detime = request.form.get('detime')
  tele = request.form.get('tele')
  oraddress = request.form.get('oraddress')
  deaddress = request.form.get('deaddress')
  mname = request.form.get('mname')
  apay =request.form.get('apay')
  content = request.form.get('content')

  rid = session.get('rid')
  sql= 'use misy410group07'
  cursor.execute(sql)
  sql = 'select * from OrderRequest where rid = %s'
  cursor.execute(sql,rid)
  mInformation = cursor.fetchone() ##这里有点问题，if error不知道怎么返回重新输入后的值
 
  if float(apay) < 0 or float(apay) > 1000:
       error = True
       flash('payment should be a number > 0 and < 1000')

  if error:
        #return to the form page
      return render_template('modify_product_order.html',content=content,detime=detime,tele=tele,oraddress=oraddress, deaddress=deaddress,mname=mname,apay=apay,mInformation=mInformation)

  else:
    sql = 'update OrderRequest set RequestContent= %s , DeliveryTime= %s, OrderTelephone=%s ,PickupAddress=%s,DeliveryAddress=%s, Merchant=%s, AdvancePayment=%s where rid=%s' 
    cursor.execute(sql,(content,detime,int(tele),oraddress,deaddress,mname,float(apay),rid))
    flash('updated successfully')
    return render_template('modify_product_order.html',mInformation=mInformation)  

#取消订单
@app.route('/deleteRequest',methods=['POST'])
def deleteRequest():
  rid = request.form.get('rid')
  sql= 'use misy410group07'
  cursor.execute(sql)
  sql = 'delete from OrderRequest where rid = %s'
  cursor.execute(sql,rid)
  return redirect('/order_2')


#order request可视化
@app.route('/request_data')
def request_data():
  if is_login():
    sql = 'select Merchant from OrderRequest'
    cursor.execute(sql)  #is a table
    merchants = cursor.fetchall()
    return render_template('request_data.html',merchants=merchants)
  else:
     return redirect('/login')


@app.route('/RequestGraph', methods=['GET'])
def request_graph():

    mname = request.args.get('mname')
    if mname:
        sql = 'select Merchant as label, count(rid) as value from OrderRequest where Merchant = %s group by Merchant'
        cursor.execute(sql,(mname))
        merchants_view = cursor.fetchall()
        chartData = json.dumps(merchants_view)
        flash(mname)
        return render_template('request_graph.html', merchants_view=chartData)
     
        #flash(merchants_view)
       # return render_template('request_data.html')
    else:
        sql = 'select Merchant as label, count(rid) as value from OrderRequest group by Merchant'
        cursor.execute(sql)
        merchants_view = cursor.fetchall()
        #flash(merchants_view)
        #return render_template('request_data.html')
        chartData = json.dumps(merchants_view)
        flash('nothing')
        return render_template('request_graph.html',merchants_view=chartData)
   


