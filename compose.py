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

#测试连上
with app.app_context():
    sql = 'select * from Contains'
    result = db.session.execute(sql)
    print(result.fetchall())


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
  
    
        

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8084, debug=True)

# x = requests.get('http://ec2-34-201-131-112.compute-1.amazonaws.com:8080/')
# print(x.content)
# print(x.status_code)



# if __name__ == "__main__":
#     import time
#     s = time.perf_counter()
#     asyncio.run(main())
#     elapsed = time.perf_counter() - s
#     print(f"{__file__} executed in {elapsed:0.2f} seconds.")

    