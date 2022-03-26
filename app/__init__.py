from flask import Flask
app = Flask(__name__)
app.secret_key = 'super secret key'
from app import login
from app import key_config
from app import product
from app import cart
from app import forgot_password
from app import employee
