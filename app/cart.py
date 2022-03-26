from flask import Flask, render_template, request, session, redirect, url_for
from app import app
from app import key_config as keys
import boto3
import json
import time

dynamodb = boto3.resource('dynamodb',region_name='us-east-1',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY)

from boto3.dynamodb.conditions import Key, Attr



#---------------------------------------------------------------------------------------------

@app.route('/add_to_cart/<product_name>/<product>', methods=["GET","POST"])
def add_to_cart(product_name,product):
    # print("Item added to cart---->",item)
    print("Into add_to_cart--------------------------------------------------------------------------------->")
    user_session = session["user"]
    # product = item[2:8]
    # product_name = item[-10:-2]
    print("product_name----->",product_name)
    print("product----->",product)
    
    table = dynamodb.Table('products')
    response = table.query(
            KeyConditionExpression=Key('product_name').eq(product_name)
    )
    product_list = []
    products_in_cart = []
    items = response['Items']
    print("items of selected product--->",items)
        
    for dict in items:
        for key,val in dict.items():
            product_list.append(val)
    print("product_list--->",product_list) 
    
    table_product = dynamodb.Table('cart')
    
    response = table_product.query(
        KeyConditionExpression=Key('email').eq(user_session)
    )
    
    items_from_cart_db =  response['Items']
    print("items_from_cart_db",items_from_cart_db)

    if len(items_from_cart_db)==0:
        table_product.put_item(
                        Item={
                            'email': user_session,
                            'product_name': [product_list[-1]]
                        }
                    )
    else:
        products_in_cart = (items_from_cart_db[-1]).get('product_name')
        print("products_in_cart",products_in_cart)
        products_in_cart.append(product_name)
        table_product.put_item(
                        Item={
                            'email': user_session,
                            'product_name': products_in_cart
                        }
                    )
    
    return redirect(url_for('product_name',product=product))
    
#---------------------------------------------------------------------------------------------

@app.route('/remove_each_from_cart/<product_name>', methods=["GET","POST"])
def remove_each_from_cart(product_name):
    user_session = session["user"]
    table = dynamodb.Table('cart')
    response = table.query(
            KeyConditionExpression=Key('email').eq(user_session)
    )
    items_from_cart_db = response['Items']
    products_in_cart = (items_from_cart_db[-1]).get('product_name')
    print("products_in_cart--->",products_in_cart)
    print("product_name---->",product_name)
    if product_name in products_in_cart:
        products_in_cart.remove(product_name)
        table.put_item(
                    Item={
                        'email': user_session,
                        'product_name': products_in_cart
                    }
                )
    
    return redirect(url_for('cart'))

#---------------------------------------------------------------------------------------------    
    
@app.route('/checkout', methods=["GET","POST"])
def checkout():
    
    email = session["user"]
    list_size = 7
    final_each_product_list = []
    table = dynamodb.Table('cart')
    response = table.query(
            KeyConditionExpression=Key('email').eq(email)
    )
    items = response['Items']
    print(items)
    products_in_cart = (items[-1]).get('product_name')
    print("products_in_cart--->",products_in_cart)
    
    all_products_list = []
    table_product = dynamodb.Table('products')
    for all_product in products_in_cart:
        response = table_product.query(
                KeyConditionExpression=Key('product_name').eq(all_product)
        )
        all_products_list.append(response['Items'])
    print("all_products_list----->",all_products_list)
    
    each_product_list = []
    
    for element1 in all_products_list:
        for item1 in element1:
            for key,val in item1.items():
                each_product_list.append(val)
    
    print("each_product_list----------->",each_product_list)
    
    
    for i in range(0,len(each_product_list),list_size):
        final_each_product_list.append(each_product_list[i:i+list_size])
    print("final_each_product_list---------->>",final_each_product_list)
    
    i=0
    cost = 0
    n = len(final_each_product_list)
    for i in range(n):
       cost =  cost + int(final_each_product_list[i][6])
       i= i+1
    
    tax = 0.13*cost
    total = cost+tax
    return render_template('checkout.html',final_each_product_list=final_each_product_list,cost=cost,tax=tax,total=total)  
    
#---------------------------------------------------------------------------------------------  

@app.route('/confirm_order', methods=["GET","POST"])
def confirm_order():
    
    print("into confirm_order")
    address = request.form['address']
    phone = request.form['phone']
    emp_alert = []
    
    
    email = session["user"]
    list_size = 6
    final_each_product_list = []
    
    table_user = dynamodb.Table('users')
    response_user = table_user.query(
            KeyConditionExpression=Key('email').eq(email)
    )
    
    items_user = response_user['Items'] 

    user_name = response_user['Items'][0]['name']
    print("Username------>",user_name)
    
    table = dynamodb.Table('cart')
    response = table.query(
            KeyConditionExpression=Key('email').eq(email)
    )
    items = response['Items']
    print(items)
    products_in_cart = (items[-1]).get('product_name')
    product = ",".join(products_in_cart)
    #print("products_in_cart--->",products_in_cart)
    total_price = 0
    table_product = dynamodb.Table('products')
    for each_product in products_in_cart:
        response = table_product.query(
                KeyConditionExpression=Key('product_name').eq(each_product)
        )
        print("each_product--->",response['Items'])
        quantity = int(response['Items'][0]['quantity'])
        price = int(response['Items'][0]['price'])
        new_quantity = quantity-1
        print("quantity--->",quantity)
        print("new_quantity--->",new_quantity)
        total_price = total_price + price
        table_product.put_item(
                    Item={
                        'product_name': response['Items'][0]['product_name'],
                        'category': response['Items'][0]['category'],
                        'description': response['Items'][0]['description'],
                        'manufacterer': response['Items'][0]['manufacterer'],
                        'price': response['Items'][0]['price'],
                        'quantity': new_quantity,
                        'image_name': response['Items'][0]['image_name'],
                    }
                )
    total_price = total_price + (total_price * 0.13)
    print("total_price-------->",total_price)
    str_total_price = str(total_price)
    
    
    lambda_client = boto3.client('lambda',
                                aws_access_key_id=keys.ACCESS_KEY_ID,
                                aws_secret_access_key=keys.ACCESS_SECRET_KEY)
    payload = {"email" : email, "product" : product, "function": "1","user_name" : user_name, "total_price" : str_total_price}
    lambda_payload_1 = json.dumps(payload)
    print("lambda_payload-----------------", lambda_payload_1)
    lambda_client.invoke(FunctionName='email_server', 
                     InvocationType='Event',
                     Payload=lambda_payload_1)
    
    for each_product in products_in_cart:
        response = table_product.query(
                KeyConditionExpression=Key('product_name').eq(each_product)
        )
        quantity = int(response['Items'][0]['quantity'])
        print("checkout_product---------", each_product)
        if quantity < 5:
            emp_alert.append(response["Items"][0]["product_name"])
            emp_alert_str = ",".join(emp_alert)
    print("emp+alert========>", emp_alert)
    if len(emp_alert) != 0:
        payload = {"email" : email, "product" : emp_alert_str, "function": "2"}
        lambda_payload_2 = json.dumps(payload)
        lambda_client.invoke(FunctionName='email_server', 
                     InvocationType='Event',
                     Payload=lambda_payload_2)
     
    table_cart = dynamodb.Table('cart')
    table_cart.put_item(
                    Item={
                        'email': email,
                        'product_name': [],
                        
                    }
                ) 
                
    '''            
    time.sleep(10)
                
    for each_product in products_in_cart:
        response = table_product.query(
                KeyConditionExpression=Key('product_name').eq(each_product)
        )
        quantity = int(response['Items'][0]['quantity']) 
        if quantity <3:
            print("Into less quantity")
            response = table.query(
                KeyConditionExpression=Key('email').eq(email)
            )
            items = response['Items']
            for customer in items:
                print("into customer loop")
                print(customer)
                cart_products = (customer).get('product_name')
                if len(cart_products) != 0:
                    if each_product in cart_products:
                        print("product match!")
                        print("each_product---------",each_product)
                        payload = {"email" : "rsgopi196@gmail.com", "product" : each_product, "function": "3"}
                        lambda_payload_3 = json.dumps(payload)
                        lambda_client.invoke(FunctionName='email_server', 
                         InvocationType='Event',
                         Payload=lambda_payload_3)
            
       '''
    
    

    
    return render_template('order_confirm.html',address=address,phone=phone)  
    
#---------------------------------------------------------------------------------------------  