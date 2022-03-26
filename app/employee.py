from flask import Flask, render_template, request,session
from app import app
from app import key_config as keys
import boto3
import numpy as np
import matplotlib.pyplot as plt

dynamodb = boto3.resource('dynamodb',region_name='us-east-1',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY)

from boto3.dynamodb.conditions import Key, Attr

#------------------------------------------------------------------------------------------------------------------

@app.route('/product_list/<product>', methods=["GET","POST"])
def product_list(product):
    table = dynamodb.Table('products')
    response = table.scan()
    items = response['Items']
    print("ITEMS------->",items)
    initial_product_list = []
    product_list = []
    final_product_list = []
    list_size = 7
    for dict in items:
        for key,val in dict.items():
            initial_product_list.append(val)
    print("initial_product_list--->",initial_product_list)
    for i in range(0,len(initial_product_list),list_size):
        product_list.append(initial_product_list[i:i+list_size])
    print("product_list-------------->",product_list)    
    for each_product in product_list:
        if(each_product[3]==product):
            final_product_list.append(each_product);
    print("final_product_list---------->",final_product_list)
    graph_product = final_product_list[0][3]
    print("graph_product---->",graph_product)
#---------------
    if (product == 'laptop'):
        response1 = table.scan(AttributesToGet=['category'])
        response2 = table.scan(AttributesToGet=['quantity'])
        response3 = table.scan(AttributesToGet=['product_name'])
        items1 = response1['Items']
        items2 = response2['Items']
        items3 = response3['Items']

 
        res1 = []
        res2 = []
        res3 = []

        for i,j,k in zip(items1,items2,items3):
            res1.extend(i.values())
            res2.extend(j.values())
            res3.extend(k.values())


        num_res2 = [int(numeric_string) for numeric_string in res2]


        only_laptop_count = []
        only_laptop = []

        for i in range(len(res1)):
            if res1[i] == 'laptop':
                only_laptop_count.append(num_res2[i])
                only_laptop.append(res3[i])
 
        plt.clf()
        plt.bar(only_laptop, only_laptop_count)
        plt.xlabel("Models")
        plt.ylabel("Count")
        plt.title("laptop")
        plt.savefig("./app/static/only_laptop.png")
        
    if (product == 'phone'):
        response1 = table.scan(AttributesToGet=['category'])
        response2 = table.scan(AttributesToGet=['quantity'])
        response3 = table.scan(AttributesToGet=['product_name'])
        items1 = response1['Items']
        items2 = response2['Items']
        items3 = response3['Items']

        res1 = []
        res2 = []
        res3 = []

        for i,j,k in zip(items1,items2,items3):
            res1.extend(i.values())
            res2.extend(j.values())
            res3.extend(k.values())

        num_res2 = [int(numeric_string) for numeric_string in res2]

        only_mobile_count = []
        only_mobile = []

        for i in range(len(res1)):
            if res1[i] == 'phone':
                only_mobile_count.append(num_res2[i])
                only_mobile.append(res3[i])
        

        plt.clf()
        plt.bar(only_mobile, only_mobile_count)
        plt.xlabel("Mobile Models")
        plt.ylabel("Mobile Count")
        plt.title("Mobile")
        plt.savefig("./app/static/only_mobile.png")

    if (product == 'smartwatch'):
        response1 = table.scan(AttributesToGet=['category'])
        response2 = table.scan(AttributesToGet=['quantity'])
        response3 = table.scan(AttributesToGet=['product_name'])
        items1 = response1['Items']
        items2 = response2['Items']
        items3 = response3['Items']


        res1 = []
        res2 = []
        res3 = []

        for i,j,k in zip(items1,items2,items3):
            res1.extend(i.values())
            res2.extend(j.values())
            res3.extend(k.values())


        num_res2 = [int(numeric_string) for numeric_string in res2]


        only_watch_count = []
        only_watch = []

        for i in range(len(res1)):
            if res1[i] == 'smartwatch':
                only_watch_count.append(num_res2[i])
                only_watch.append(res3[i])

        plt.clf()
        plt.bar(only_watch, only_watch_count)
        plt.xlabel("watch Models")
        plt.ylabel("watch Count")
        plt.title("watch")
        plt.savefig("./app/static/only_watch.png")
    
    return render_template('product_list_employee.html',final_product_list=final_product_list,graph_product=graph_product)
    

    
    
#------------------------------------------------------------------------------------------------------------------

@app.route('/employee_order',methods=["GET","POST"])
def employee_order():
    return render_template('employee_order.html')




