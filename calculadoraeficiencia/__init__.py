from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("PI")
app.config['SECRET_KEY'] = 'admin'
database = SQLAlchemy(app)

# Configurações do Flask-Mail para Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'taticosolucoes@gmail.com'  # Seu email do Gmail
app.config['MAIL_PASSWORD'] = 'acra pdbm qlrs lvjt'  # Sua senha do Gmail
app.config['MAIL_DEFAULT_SENDER'] = ('Tático Soluções', 'taticosolucoes@gmail.com')

mail = Mail(app)

from calculadoraeficiencia import routes