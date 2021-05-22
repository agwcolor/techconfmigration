import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy 
# from azure.servicebus import QueueClient


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

secret_key = app.config.get('SECRET_KEY')
connstr = app.config.get('SERVICE_BUS_CONNECTION_STRING')
print("In __init__.py connstr is", connstr)
queue_name = app.config.get('SERVICE_BUS_QUEUE_NAME')
print("In __init.py__ queue_name is", queue_name)
# queue_client = QueueClient.from_connection_string(app.config.get('SERVICE_BUS_CONNECTION_STRING'), app.config.get('SERVICE_BUS_QUEUE_NAME'))

db = SQLAlchemy(app)

from . import routes