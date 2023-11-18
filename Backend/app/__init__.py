# __init__.py
from flask import Flask

app = Flask(__name__, template_folder='../template', static_folder='../static')

from app import app
