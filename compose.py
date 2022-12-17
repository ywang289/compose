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




@app.route('/', methods=['GET'])
def home():
    x = requests.get('http://ec2-34-201-131-112.compute-1.amazonaws.com:8080/')
    y= requests.get('http://127.0.0.1:8081')

    json_list=[]
    print(x.text)
    print(y.text)

    json_list.append(x.text)
    json_list.append(y.text)
    

    return json.dumps(json_list)


# 1. customer purchase
# for each db:
# Sellers → check remaining amount for each purchased merchandise; if all are ok, then update for each; if one is not enough, return warning message
# if success:
# Customers → insert to orders; insert to places; return oid
# if oid:
# Purchases → insert to orders; insert to contains (for each purchased merchandise) 

@app.route('/customer/purchase', methods=['POST'])
def customer_purchase():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        email = data['email']
        time=data['timestamp']
        items= data["items"]
        
        sellers_check = requests.post('http://127.0.0.1:8081/order/check_amount', data=request.get_data())
        #{response: success or fail}
        # print(json.loads(sellers_check.text)['state'])
        # print(json.loads(sellers_check.text)['message'])
        if json.loads(sellers_check.text)['state']:
            # success
            #{email: string, timestamp: time,( current time),items:dictionary{merchandise id: amount}}
            print("success")
            s= json.dumps({'email':email, 'timestamp':time, 'items':items})
            
            get_oid = requests.post('http://127.0.0.1:8080/customer/place_order', data=s)
            # true/ false
            oid = json.loads(get_oid.text)['oid']
            if json.loads(get_oid.text)['state']:
                print("successfully")
                # { "email":"test3@gmail.com", "timestamp":"2022-12-14 17:30:00" ,"order":{"1":"10", "10":"2"}, "oid":"4"}
                s= json.dumps({'email':email, 'timestamp':time, 'items':items, "oid": oid})
                insert_item= requests.post('http://127.0.0.1:8082/order/place_order', data=s)
    return insert_item.text

@app.route('/search', methods=['POST'])
def seaerch():
    # x = requests.get('http://ec2-34-201-131-112.compute-1.amazonaws.com:8080/')
    # y= requests.get('http://127.0.0.1:8081')
    json_list=[]
    if request.method == 'POST':
        data = json.loads(request.get_data())
        get_email = data['email']
        print(get_email)
        d={'email': get_email}
        # change answer to databse 
        s=json.dumps(d)
        seller_search= requests.post('http://127.0.0.1:8081/people', data=s)
        customer_search= requests.post("http://127.0.0.1:8080/people", data=s)
        
        
        print(seller_search.text)
        # print(customer_search.text)

        json_list.append(seller_search.text)
        json_list.append(customer_search.text)
        # json_list.append(customer_search.text)
    

        return json.dumps(json_list)

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
        sellers_insert= requests.post('http://127.0.0.1:8081/seller/insert_item', data=request.get_data())
        
        if json.loads(sellers_insert.text)['state']:
            # success
            mid = json.loads(sellers_insert.text)['mid']
            #{email: string, timestamp: time,( current time),items:dictionary{merchandise id: amount}}
            print("success")
            s= json.dumps({'mid':mid})
            insert_order = requests.post('http://127.0.0.1:8082//order/add_merchandise', data=s)
            # true/ false
            print("second")
    return insert_order.text   

#{"oid":"24"}
@app.route('/compose/order_details', methods=['POST'])
def order_detail():
    if request.method == 'POST':
        
        order_detail = requests.post('http://127.0.0.1:8082/customer/order_details', data=request.get_data())
        order=json.loads(order_detail.text)
        compose_detail= requests.post('http://127.0.0.1:8081/mid/get_name', data=json.dumps(order))

        return json.loads(compose_detail.text)
        

        

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8084, debug=True)


    