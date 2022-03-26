from flask import Flask, render_template, request,session,redirect,url_for
from app import app
from app import key_config as keys
from werkzeug.utils import secure_filename
import json
import boto3

dynamodb = boto3.resource('dynamodb',region_name='us-east-1',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY)

from boto3.dynamodb.conditions import Key, Attr

s3 = boto3.client('s3',region_name='us-east-1',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key= keys.ACCESS_SECRET_KEY
                     )
BUCKET_NAME='assignment3ece1779'

#------------------------------------------------------------------------------------------------------------------

@app.route('/product/<product>', methods=["GET","POST"])
def product_name(product):
    table = dynamodb.Table('products')
    response = table.scan()
    items = response['Items']
    initial_product_list = []
    product_list = []
    final_product_list = []
    list_size = 7
    for dict in items:
        for key,val in dict.items():
            initial_product_list.append(val)
    
    for i in range(0,len(initial_product_list),list_size):
        product_list.append(initial_product_list[i:i+list_size])
    print(product_list)    
    for each_product in product_list:
        if(each_product[3]==product):
            final_product_list.append(each_product);
    print("final_product_list---------->",final_product_list)
    return render_template('product_display.html',final_product_list=final_product_list)

#----------------------------------------------------------------------------------------------------------------

@app.route('/cart', methods=["GET","POST"])
def cart():
    
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
    
    return render_template('cart.html',final_each_product_list=final_each_product_list,cost=cost,n=n)

#------------------------------------------------------------------------------------------------------

@app.route('/upload_image', methods=["GET","POST"])
def upload_image():
    return render_template('search_by_image.html')
#------------------------------------------------------------------------------------------------------    
    
@app.route('/upload',methods=['post'])
def upload():
    if request.method == 'POST':
        img = request.files['file']
        
        if 'image' not in request.files:
            error_msg = 'Please choose an image to upload!'
            return render_template('search_by_image.html', error_msg=error_msg)
 

        if img:
                filename = secure_filename(img.filename)
                
                img.save(filename)
                s3.upload_file(
                    Bucket = BUCKET_NAME,
                    Filename=filename,
                    Key = filename
                )
                error_msg = "Upload Done ! "
                
    for item in s3.list_objects(Bucket=BUCKET_NAME)['Contents']:
            presigned_url = s3.generate_presigned_url('get_object', Params = {'Bucket': BUCKET_NAME, 'Key': item['Key']}, ExpiresIn = 10000)
    print("filename------------",filename)
    
    client = boto3.client("rekognition",region_name='us-east-1')
    fileObj = s3.get_object(Bucket = BUCKET_NAME, Key = filename)
    file_content = fileObj["Body"].read()
    response = client.detect_labels(Image = {"S3Object": {"Bucket": BUCKET_NAME, "Name": filename}}, MaxLabels=1, MinConfidence=80)
    product = (((response['Labels'])[0])["Name"]).lower()
    print("product----->",product)
    
    if (product):
        if ('laptop' or 'pc') in product:
            new_product = 'laptop'
            return redirect(url_for('product_name',product=new_product))
        elif 'watch' in product:
            new_product = 'smartwatch'
            return redirect(url_for('product_name',product=new_product))
        elif ('mobile' or 'phone') in product:
            new_product = 'phone'
            return redirect(url_for('product_name',product=new_product))
            
    return render_template("search_by_image.html",error_msg =error_msg)

#------------------------------------------------------------------------------------------------------

@app.route('/employee_place_order',methods=['post'])
def employee_place_order():
    SmartWatch_1 = request.form['SmartWatch_1']
    Laptop_3 = request.form['Laptop_3']
    Mobile_1 = request.form['Mobile_1']
    Laptop_2 = request.form['Laptop_2']
    Laptop_1 = request.form['Laptop_1']
    
    table_product = dynamodb.Table('products')
    
    
    response_1 = table_product.query(
        KeyConditionExpression=Key('product_name').eq('SmartWatch_1')
    )
    
    response_2 = table_product.query(
        KeyConditionExpression=Key('product_name').eq('Laptop_3')
    )
    
    response_3 = table_product.query(
        KeyConditionExpression=Key('product_name').eq('Mobile_1')
    )
    
    response_4 = table_product.query(
        KeyConditionExpression=Key('product_name').eq('Laptop_2')
    )
    
    response_5 = table_product.query(
        KeyConditionExpression=Key('product_name').eq('Laptop_1')
    )
    
    result_1 = int(((response_1['Items'])[0]).get("quantity")) + int(SmartWatch_1)
    table_product.put_item(
        Item = {
            'product_name': response_1['Items'][0]['product_name'],
            'category': response_1['Items'][0]['category'],
            'description': response_1['Items'][0]['description'],
            'manufacterer': response_1['Items'][0]['manufacterer'],
            'price': response_1['Items'][0]['price'],
            'quantity': result_1
        }
    )
    
    result_2 = int(((response_1['Items'])[0]).get("quantity")) + int(Laptop_3)
    table_product.put_item(
        Item = {
            'product_name': response_2['Items'][0]['product_name'],
            'category': response_2['Items'][0]['category'],
            'description': response_2['Items'][0]['description'],
            'manufacterer': response_2['Items'][0]['manufacterer'],
            'price': response_2['Items'][0]['price'],
            'quantity': result_2
        }
    )
    
    result_3 = int(((response_1['Items'])[0]).get("quantity")) + int(Mobile_1)
    table_product.put_item(
        Item = {
            'product_name': response_3['Items'][0]['product_name'],
            'category': response_3['Items'][0]['category'],
            'description': response_3['Items'][0]['description'],
            'manufacterer': response_3['Items'][0]['manufacterer'],
            'price': response_3['Items'][0]['price'],
            'quantity': result_3
        }
    )
    
    result_4 = int(((response_1['Items'])[0]).get("quantity")) + int(Laptop_2)
    table_product.put_item(
        Item = {
            'product_name': response_4['Items'][0]['product_name'],
            'category': response_4['Items'][0]['category'],
            'description': response_4['Items'][0]['description'],
            'manufacterer': response_4['Items'][0]['manufacterer'],
            'price': response_4['Items'][0]['price'],
            'quantity': result_4
        }
    )
    
    result_5 = int(((response_5['Items'])[0]).get("quantity")) + int(Laptop_1)
    table_product.put_item(
        Item = {
            'product_name': response_5['Items'][0]['product_name'],
            'category': response_5['Items'][0]['category'],
            'description': response_5['Items'][0]['description'],
            'manufacterer': response_5['Items'][0]['manufacterer'],
            'price': response_5['Items'][0]['price'],
            'quantity': result_5
        }
    )
    error_msg = "Order Placed to Supplier. Products will be shipped to the warehouse immediately!" 
    return render_template("employee_order.html",error_msg=error_msg)
    
     
     