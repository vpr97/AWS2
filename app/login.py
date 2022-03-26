from flask import Flask, render_template, request,session
from app import app
from app import key_config as keys
import numpy as np
import matplotlib.pyplot as plt
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY)

from boto3.dynamodb.conditions import Key, Attr


#---------------------------------------------------------------------------------------------

@app.route('/', methods=["GET","POST"])
def index():
    return render_template('login_page.html') 
#---------------------------------------------------------------------------------------------    

@app.route('/backtoproduct', methods=["GET","POST"])
def backtoproduct():
    return render_template("customer_home_page.html")

#---------------------------------------------------------------------------------------------


@app.route('/employee_home', methods=["GET","POST"])
def employee_home():
    return render_template("employee_page.html")

#---------------------------------------------------------------------------------------------

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=='POST':
        
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user-type']
        session["user"] = email
        
        if email=='' or password =='' or user_type=="default":
            error_msg = "All the fields are mandatory!"
            return render_template("login_page.html",error_msg=error_msg)
        
        
        
        print("usertype---->",user_type)
        print("email--->",email)
        table = dynamodb.Table('users')
        response = table.query(
                KeyConditionExpression=Key('email').eq(email)
        )
        print("response--->",response)
        items = response['Items']
        if(len(items)>0):
            print("All Items---->",items)
            print("Password",items[0]['password'])
            print("user-type", items[0]['user_type'])
            if password == items[0]['password']:
                print("Into if loop")
                if user_type == 'customer' and user_type == items[0]['user_type']:
                    return render_template("customer_home_page.html")
                if user_type == 'employee' and user_type == items[0]['user_type']:
                    return render_template("employee_page.html")
        error_msg = "Invalid username and password!"
    #error_msg = "Username and Password is empty"
    
    
    return render_template("login_page.html",error_msg=error_msg)
    
#---------------------------------------------------------------------------------------------

@app.route('/dev/createAccount', methods=["GET","POST"])
def navigate_to_signup():
    return render_template('register_user_page.html') 
#---------------------------------------------------------------------------------------------

@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        re_password = request.form['re-password']
        print("email---->",email)
        
        if name=="" or email=="" or password=="" or re_password=="":
            msg = "All the fields are mandatory!"
            return render_template('register_user_page.html',msg=msg)
        
        if password != re_password:
            msg = "Passwords do not match!"
            return render_template('register_user_page.html',msg=msg) 
        
        if password == re_password:
            table = dynamodb.Table('users')
            
            response = table.query(
                    KeyConditionExpression=Key('email').eq(email)
            )
            items = response['Items']
            if len(items) == 0:
                table.put_item(
                    Item={
                        'name': name,
                        'email': email,
                        'password': password,
                        'user_type':'customer'
                    }
                )
                ses_client = boto3.client('ses',region_name='us-east-1',
                                            aws_access_key_id=keys.ACCESS_KEY_ID,
                                            aws_secret_access_key=keys.ACCESS_SECRET_KEY)
                response = ses_client.verify_email_identity(
                        EmailAddress=email)
                        
            
                table_cart = dynamodb.Table('cart')
                table_cart.put_item(
                        Item={
                            'email': email,
                            'product_name': [],
                            
                        }
                    )
            
                msg = "Registration Complete! Please verify your mail"
            else:
                msg = "User with the given email id already exists"
        else:
            msg = "Password doesn't match"
    msg = "User Account created Successfully"
    return render_template('register_user_page.html',msg=msg)


#---------------------------------------------------------------------------------------------


@app.route('/graph',methods=["GET","POST"])
def graph():
    dynamodb_client = boto3.client("dynamodb",region_name='us-east-1')

    table = dynamodb.Table('products')


    response1 = table.scan(AttributesToGet=['category'])
    response2 = table.scan(AttributesToGet=['quantity'])
    items1 = response1['Items']
    items2 = response2['Items']

    print(len(items1))

    res1 = []
    res2 = []

    for i,j in zip(items1,items2):
        res1.extend(i.values())
        res2.extend(j.values())
    
   
    num_res2 = [int(numeric_string) for numeric_string in res2]

    

    count_watch = 0
    count_mobile = 0
    count_laptop = 0

    

    for i in range(len(res1)):
        print (res1[i])
        if res1[i] == 'laptop':
            count_laptop = count_laptop + num_res2[i]
            print('num----->',num_res2[i])
            print(count_laptop)
        if res1[i] == 'phone':
            count_mobile = count_mobile + num_res2[i]
            print('num----->',num_res2[i])
            print(count_mobile)
        if res1[i] == 'smartwatch':
            count_watch = count_watch + num_res2[i]
 


    array_gadgets = ['smartwatch','laptop','phone']


    array_gadgets_count = [count_watch,count_laptop,count_mobile]
                    
    plt.clf()
    plt.bar(array_gadgets, array_gadgets_count)
    plt.xlabel("Gadgets")
    plt.ylabel("Gadgets count")
    plt.title("Gadgets Information")
    plt.savefig("./app/static/gadgets_info.png")
    
    return render_template('graph.html')