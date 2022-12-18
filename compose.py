import asyncio
import requests

async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")

async def main():
    await asyncio.gather(count(), count(), count())

import requests

from flask import Flask, Response, request,flash, render_template, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
from datetime import datetime


app=Flask(__name__)
CORS(app)

app.config['SECRET_KEY']='zy112612' # 密码
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://admin:zy112612@e6156-1.cudpmdtzmg9e.us-east-1.rds.amazonaws.com:3306/Purchase'
    # 协议：mysql+pymysql
    # 用户名：root
    # 密码：2333
    # IP地址：localhost
    # 端口：3306
    # 数据库名：runoob #这里的数据库需要提前建好
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)

customer_http="http://ec2-44-201-86-144.compute-1.amazonaws.com:8080/"
seller_http="http://ec2-52-55-10-164.compute-1.amazonaws.com:8081/"
order_http="http://ec2-3-84-2-51.compute-1.amazonaws.com:8082/"

# customer_http="http://127.0.0.1:8080/"
# seller_http="http://127.0.0.1:8081/"
# order_http="http://127.0.0.1:8082/"


with app.app_context():
   print("a")

@app.route('/', methods=['GET'])
def home():
    return "hello world"


# 1. customer purchase
# for each db:
# Sellers → check remaining amount for each purchased merchandise; if all are ok, then update for each; if one is not enough, return warning message
# if success:
# Customers → insert to orders; insert to places; return oid
# if oid:
# Purchases → insert to orders; insert to contains (for each purchased merchandise) 

#{"email":"wg@gmail.com", "timestamp":"2022-12-11 17:30:00","items":[{"mid":"1","amount":"1"}, {"mid":"10","amount":"2"}]}
@app.route('/customer/purchase', methods=['POST'])
def customer_purchase():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        email = data['email']
        time=data['timestamp']
        items= data["items"]
        
        sellers_check = requests.post(seller_http+'order/check_amount', data=request.get_data())
        #{response: success or fail}
        # print(json.loads(sellers_check.text)['state'])
        # print(json.loads(sellers_check.text)['message'])
        if json.loads(sellers_check.text)['state']:
            # success
            #{email: string, timestamp: time,( current time),items:dictionary{merchandise id: amount}}
            print("success")
            s= json.dumps({'email':email, 'timestamp':time, 'items':items})
            
            get_oid = requests.post(customer_http+'customer/place_order', data=s)
            # true/ false
            oid = json.loads(get_oid.text)['oid']
            if json.loads(get_oid.text)['state']:
                print("successfully")
                # { "email":"test3@gmail.com", "timestamp":"2022-12-14 17:30:00" ,"order":{"1":"10", "10":"2"}, "oid":"4"}
                s= json.dumps({'email':email, 'timestamp':time, 'items':items, "oid": oid})
                insert_item= requests.post(order_http+'order/place_order', data=s)
    return insert_item.text


# 2. seller insert merchandise
# from frontend to backend:
# 	{email, name, price, remaining_amount, description, picture}
# for each db:
# /seller/insert_item
# Sellers → insert to merchandises and provides; return mid

# if mid:
# 	/order/add_merchandise
# Purchases → insert id to merchandise

#  {"email": "test@gmail.com", "name":"test2", "price": 10, "remaining_amount":100, "description": "bbb", "picture": "aaaa"}
@app.route('/seller/insert_merchandise', methods=['POST'])
def insert_merchandise():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        email = data['email']
        name= data["name"]
        price= data["price"]
        remaining_amount= data['remaining_amount']
        description= data["description"]
        picture= data['picture']
        sellers_insert= requests.post(seller_http+'seller/insert_item', data=request.get_data())
        
        if json.loads(sellers_insert.text)['state']:
            # success
            print(json.loads(sellers_insert.text))
            mid = json.loads(sellers_insert.text)['mid']
           
            #{email: string, timestamp: time,( current time),items:dictionary{merchandise id: amount}}
            print("success")
            s= json.dumps({'mid':mid, "name": name})
            print ({'mid':mid, "name": name})
            insert_order = requests.post(order_http+'order/add_merchandise', data=s)
            
            # true/ false
            print("second")
    return insert_order.text   

#{email, name, price, remaining_amount, description, picture, mid}
@app.route('/compose/update_merchandise', methods=['POST'])
def order_detail():
    if request.method == 'POST':
        
        order_detail = requests.post(seller_http+'seller/update_item', data=request.get_data())
        order=json.loads(order_detail.text)
    # if can not search order, need to add something
        compose_detail= requests.post(order_http+'/order/update_merchandise', data=request.get_data())

        return json.loads(compose_detail.text)
        



        

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8084, debug=True)


    