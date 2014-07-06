# -*- encoding:utf-8 -*-
from admin.default_settings import *
from demo1.models.comments import CommentsModel
from demo1.models.event_parsed import EventParsedModel
from demo1.models.event_producers import EventProducersModel
from demo1.models.event_sources import EventSourcesModel
from demo1.models.event_streams import EventStreamsModel
from demo1.models.follows import FollowsModel
from demo1.models.notifications import NotificationsModel
from demo1.models.users import UsersModel
from demo1.models.clients import ClientsModel
from models.tasks import TasksModel

PATH = os.path.dirname(__file__)
DEBUG = True
HOST = "127.0.0.1"
PORT = 1488
SQL = "postgresql://user:password@127.0.0.1:5432/dbname"
DATABASES = [
    "sql"
]
MODELS = [
    UsersModel,
    ClientsModel,
    FollowsModel,
    TasksModel,
    EventParsedModel,
    EventSourcesModel,
    EventStreamsModel,
    EventProducersModel,
    CommentsModel,
    NotificationsModel
]
HIDE_MODELS = ["django_content_type", "djapian_change"]