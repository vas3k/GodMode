# -*- encoding:utf-8 -*-
import os
import jinja2
from pymongo import MongoClient
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base
from flask import Flask, render_template, request
from admin.common.template_tags import magic_params
from admin.log import app_log
from admin.models.mongodb import MongodbModel
from admin.models.sql import SqlModel

Base = automap_base()


class AdminApp(object):
    def __init__(self, settings):
        self.app = Flask(__name__)
        self.app.config["DEBUG"] = settings.DEBUG
        template_loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader([os.path.join(settings.PATH, "templates")]),
            self.app.jinja_loader,
        ])
        self.app.jinja_loader = template_loader

        self.settings = settings
        self.plugins = {}
        self.with_sql = "sql" in self.settings.DATABASES
        self.with_mongodb = "mongodb" in self.settings.DATABASES

        if self.with_sql:
            self.sql_engine = create_engine(settings.SQL, echo=self.settings.DEBUG, pool_recycle=60 * 5)
            self.sql_tables = {}
            self.sql_models = []

        if self.with_mongodb:
            splitter = settings.MONGODB.rfind("/")
            self.mongodb_engine = MongoClient(settings.MONGODB[:splitter])[settings.MONGODB[splitter + 1:]]
            self.mongodb_collections = {}
            self.mongodb_models = []

    def run(self, run=True):
        app_log.info("Running...")
        if self.with_sql:
            app_log.info("With SQL")
            self.sql_tables = self.sql_reflect()
            self.sql_models = self.sql_init_models()

        if self.with_mongodb:
            app_log.info("With MongoDB")
            self.mongodb_collections = self.mongodb_reflect()
            self.mongodb_models = self.mongodb_init_models()

        self.init_templates()
        self.init_plugins()
        self.init_app(run)

    def sql_reflect(self):
        app_log.info("Reflect SQL...")
        base = automap_base(metadata=MetaData(self.sql_engine))
        base.prepare(self.sql_engine, reflect=True)
        return dict(base.classes)

    def mongodb_reflect(self):
        app_log.info("Reflect MongoDB...")
        collections = {}
        for name in self.mongodb_engine.collection_names():
            collections.update({
                name: self.mongodb_engine[name]
            })
        return collections

    def sql_init_models(self):
        app_log.info("Init SQL models...")
        tables = []
        models = []
        for model in self.settings.MODELS:
            if issubclass(model, SqlModel):
                tables.append(model.db_table)
                models.append(model(self, self.sql_tables[model.db_table]))

        for table_name, table in self.sql_tables.iteritems():
            if table_name in self.settings.HIDE_MODELS:
                continue

            if table_name in tables:
                continue

            model = type(str(table_name), (SqlModel,), {"db_table": table_name})(self, table)
            models.append(model)
        return models

    def mongodb_init_models(self):
        app_log.info("Init MongoDB models...")
        collections = []
        models = []
        for model in self.settings.MODELS:
            if issubclass(model, MongodbModel):
                collections.append(model.collection)
                models.append(model(self, self.mongodb_collections[model.collection]))

        for collection_name, collection in self.mongodb_collections.iteritems():
            if collection_name in self.settings.HIDE_MODELS:
                continue

            if collection_name in collections:
                continue

            model = type(str(collection_name), (MongodbModel,), {"collection": collection_name})(self, collection)
            models.append(model)
        return models

    def init_plugins(self):
        self.app.add_url_rule("/plugin/<name>/", "plugin", self.render_plugin)
        for name, plugin in self.settings.PLUGINS.items():
            self.plugins[name] = plugin()

    def init_app(self, run=True):
        self.app.add_url_rule("/", "sql", self.render_sql)
        self.app.add_url_rule("/mongo/", "mongo", self.render_mongo)
        if run:
            self.app.run(self.settings.HOST, self.settings.PORT, self.settings.DEBUG)

    def init_templates(self):
        self.app.jinja_env.globals["magic_params"] = magic_params
        self.app.jinja_env.globals["str"] = unicode
        self.app.jinja_env.globals["max"] = max
        self.app.jinja_env.globals["min"] = min

    def render_sql(self):
        return render_template("sql.html", admin=self)

    def render_mongo(self):
        return render_template("mongo.html", admin=self)

    def render_plugin(self, name):
        return self.plugins[name].plugin(request=request, admin=self)

    def __call__(self, environ, start_response):
        return self.app.wsgi_app(environ, start_response)

