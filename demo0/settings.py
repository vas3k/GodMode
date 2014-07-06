# -*- encoding:utf-8 -*-
from admin.default_settings import *

PATH = os.path.dirname(__file__)
DEBUG = True
HOST = "127.0.0.1"
PORT = 1488
SQL = "postgresql://user:password@127.0.0.1:5432/dbname"
DATABASES = [
    "sql"
]
MODELS = [

]
