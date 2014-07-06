# -*- encoding:utf-8 -*-
from collections import defaultdict
from time import time
from datetime import datetime
from flask import render_template, request, redirect
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import create_session
from sqlalchemy.orm.exc import NoResultFound
from admin.exceptions import AdminException


class SqlModel(object):
    name = None
    icon = u"icon-loadingeight"
    db_table = None
    id_field = "id"
    order_by = "id"
    per_page = 100
    plotable = False
    creatable = True
    editable = True
    deletable = True

    def __init__(self, admin, table):
        self.admin = admin
        self.table = table
        self.columns = self.parse_columns(table)
        self.related_cache = defaultdict(dict)
        self.admin.app.add_url_rule("/db/%s/" % self.db_table, self.db_table, self.list_view)

        if self.creatable:
            self.admin.app.add_url_rule("/db/%s/new/" % self.db_table, self.db_table + "_new", self.new_view)
            self.admin.app.add_url_rule("/db/%s/new/save/" % self.db_table, self.db_table + "_save_new", self.save_new_view, methods=['POST'])

        if self.deletable:
            self.admin.app.add_url_rule("/db/%s/delete/" % self.db_table, self.db_table + "_delete", self.delete_view)

        if self.editable:
            self.admin.app.add_url_rule("/db/%s/<id>/" % self.db_table, self.db_table + "_obj", self.object_view)
            self.admin.app.add_url_rule("/db/%s/<id>/save/" % self.db_table, self.db_table + "_save", self.save_view, methods=['POST'])

    def list_view(self):
        where = request.args.get("where")
        order_by = request.args.get("order_by", self.order_by)
        limit = int(request.args.get("limit", self.per_page))
        offset = int(request.args.get("offset", 0))

        session = create_session(self.admin.sql_engine)
        try:
            dt = time()
            if where and where != "true":
                objects = session.execute("select * from %s where %s order by %s limit %s offset %s" % (self.db_table, where, order_by, limit, offset))
                exec_time = time() - dt
                count = session.execute("select count(*) from %s where %s" % (self.db_table, where)).first()[0]
            else:
                objects = session.query(self.table).order_by(order_by)[offset:offset+limit]
                exec_time = time() - dt
                count = session.query(self.table).count()
        except DatabaseError, ex:
            session.close()
            return render_template(
                "error.html",
                request=request,
                admin=self.admin,
                model=self,
                error=ex
            )

        rows = []
        if count > 0:
            for obj in objects:
                rows.append(self.output_row(obj, self.columns, "*", session))

        session.close()

        return render_template(
            "list.html",
            request=request,
            admin=self.admin,
            model=self,
            rows=rows,
            where=where,
            count=count,
            order_by=order_by,
            offset=offset,
            limit=limit,
            exec_time=exec_time
        )

    def object_view(self, id):
        session = create_session(self.admin.sql_engine)
        try:
            row = session.query(self.table).filter_by(id=id).one()
        except DatabaseError, ex:
            session.close()
            return render_template(
                "error.html",
                request=request,
                admin=self.admin,
                model=self,
                error=ex
            )

        object = {}
        for column in self.columns:
            object[column["name"]] = self.output_field(getattr(row, column["name"]), column)
        session.close()
        return render_template(
            "object.html",
            request=request,
            admin=self.admin,
            model=self,
            object=object
        )

    def save_view(self, id):
        values = {}
        for column in self.columns:
            values[column["name"]] = self.input_field(request, column)

        session = create_session(self.admin.sql_engine)
        try:
            session.query(self.table).filter(self.table.id == id).update(values)
        except DatabaseError, ex:
            session.close()
            return render_template(
                "error.html",
                request=request,
                admin=self.admin,
                model=self,
                error=ex
            )
        session.flush()
        session.close()
        return redirect(request.referrer)

    def new_view(self):
        return render_template(
            "object.html",
            request=request,
            admin=self.admin,
            model=self
        )

    def save_new_view(self):
        values = {}
        for column in self.columns:
            if column["name"] != self.id_field:
                values[column["name"]] = self.input_field(request, column)
        session = create_session(self.admin.sql_engine)
        session.add(self.table(**values))
        session.flush()
        session.close()
        return redirect(request.referrer)

    def delete_view(self):
        ids = request.args.get("ids", "")
        ids = [id.strip() for id in ids.split(",")]

        session = create_session(self.admin.sql_engine)
        if ids:
            try:
                session.query(self.table).filter(self.table.id.in_(ids)).delete(synchronize_session=False)
            except DatabaseError, ex:
                session.close()
                return render_template(
                    "error.html",
                    request=request,
                    admin=self.admin,
                    model=self,
                    error=ex
                )

        session.flush()
        session.close()

        return redirect("/db/%s/" % self.db_table)

    def output_row(self, obj, columns, requested_columns, session):
        row = []
        for column in columns:
            if "*" not in requested_columns and column["name"] not in requested_columns:
                continue

            value = getattr(obj, column["name"])
            related = None
            if value is not None and column["name"] in self.Fields.related:
                table, field = self.Fields.related[column["name"]].split(".", 1)
                related_table = self.admin.sql_tables[table]
                if related_table in self.related_cache and value in self.related_cache[related_table]:
                    related = self.related_cache[related_table][value]
                else:
                    try:
                        related_object = session.query(related_table).filter(related_table.id == value).one()
                        related = {
                            "value": getattr(related_object, field),
                            "table": table
                        }
                        self.related_cache[related_table][value] = related
                    except NoResultFound:
                        pass

            choice = None
            if value is not None and column["name"] in self.Fields.choices:
                choice = self.Fields.choices[column["name"]].get(value)

            row.append({
                "value": value,
                "related": related,
                "choice": choice,
                "column": column
            })

        return {
            "style": self.Row.style(obj),
            "row": row
        }

    def input_field(self, request, column):
        value = request.form.get(column["name"])

        if value and column["type"] in ("datetime", "timestamp with time zone"):
            try:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M")

        if column["type"] in ("boolean", "bool"):
            value = bool(value)

        if not column["column"].nullable:
            if value is None:
                raise AdminException("%s is not null" % column["name"])
        else:
            if value == "":
                value = None

        return value

    def output_field(self, value, column):
        if isinstance(value, datetime):
            value = value.strftime("%Y-%m-%dT%H:%M:%S")
        return value

    def parse_columns(self, table):
        fields = self.Row.fields
        columns = []
        for column in table.__table__.columns:
            if "*" not in fields and column.name not in fields:
                continue

            column_type_str = str(column.type).lower()
            column_type = column_type_str
            column_type_len = None
            if "(" in column_type_str:
                column_type = column_type_str[:column_type_str.find("(")]
                try:
                    column_type_len = int(column_type_str[column_type_str.find("(")+1:column_type_str.find(")")])
                except ValueError:
                    pass

            column_description = {
                "column": column,
                "name": column.name,
                "type": column_type,
                "type_len": column_type_len,
                "foreign_key": str(list(column.foreign_keys)[0].column).split(".", 1)[0] if column.foreign_keys else None
            }

            if column.name == self.id_field:
                columns.insert(0, column_description)
            else:
                columns.append(column_description)
        return columns

    def parse_where(self, string):
        if string and "=" in string:
            key, value = string.split("=", 1)
            return {
                key.strip(): value.strip()
            }
        else:
            return {}

    def plot(self):
        raise NotImplementedError()

    class Fields:
        related = {}
        choices = {}
        tips = {}

    class Object:
        fields = ["*"]

    class Row:
        fields = ["*"]

        @staticmethod
        def style(row):
            return {}