from flask import Flask, render_template, request,session
from app import app
from app import key_config as keys
import boto3

dynamodb = boto3.resource('dynamodb',region_name='us-east-1',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY)

from boto3.dynamodb.conditions import Key, Attr
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'ece1779flaskproject@gmail.com'
app.config['MAIL_PASSWORD'] = 'ece1779flask'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# n1 = '0'
# n2 = '0'
#function to navigate to forgot password page
@app.route('/gotorecoverpassword', methods=["GET","POST"])
def recover_password():
    return render_template('forgot_password.html')

#function to send mail to user's email id to recover password
@app.route("/recoverpassword", methods=['GET', 'POST'])
def mail_body():

    
    global n1
    global n2
    n1 = request.form['username']
    n2 = request.form['mail']
    n3 = request.form['user-type']
    if (n1 == '' or n2 == '' or n3 == ''):
        error_msg = "No field should be empty!"
        
    else:
        table = dynamodb.Table('users')
        session["user"] = n2

        response = table.query(
            KeyConditionExpression=Key('email').eq(n2)
        )
        items = response['Items']

    
   
        if n1 == items[0]['name'] and n2 == items[0]['email'] and n3 == items[0]['user_type']:

            msg = Message('Reset Password', sender='ece1779flaskproject@gmail.com', recipients=[request.form.get('mail')])
            msg.html = render_template('/mail_link.html', username=n1)
            mail.send(msg)
            error_msg = "Mail sent Successfully."
        
        else:
            error_msg = "Invalid user!"
        
    return render_template('forgot_password.html',error_msg=error_msg);        
    



#function to display reset password page
@app.route('/go_to_reset_password_page', methods=["GET"])
def go_to_reset_password_page():
    return render_template('reset_password_email.html')

#function to update the password in the database
@app.route("/resetpassword", methods=['GET', 'POST'])
def reset_password():
    new_password = request.form.get('password')
    renew_password = request.form.get('repassword')
    username = request.form.get('username')
    mail = request.form.get('mail')
    
    

    
    if (new_password == renew_password and username == n1 and mail == n2):
        #session["user"] = n2
        dynamodb_client = boto3.client("dynamodb")



        table = 'users'
        key ={
        'email':{'S':mail}
        }

        response = dynamodb_client.update_item(
                            TableName = table,
                            Key= key,
                            ExpressionAttributeNames = {
                            '#st': 'password'
                            },
                            UpdateExpression="set #st = :password",
                            ExpressionAttributeValues={
                                ':password': {
                                'S':new_password
                                }
                            }
                        )

        error_msg = "Password updated Successfully."
    elif (new_password != renew_password):
        error_msg = "Both the password should be same!"
    else:
        error_msg = "Only logged in user can update the password!"
        
    if (new_password == '' or renew_password == '' or username == '' or mail == ''):
        error_msg = "No field should be empty!"
        
    return render_template('/reset_password_email.html', error_msg=error_msg)
