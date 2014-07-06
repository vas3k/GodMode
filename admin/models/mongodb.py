# -*- encoding:utf-8 -*-
from time import time
from bson import ObjectId
from flask import render_template, request, redirect


class MongodbModel(object):
    name = None
    icon = u"icon-loadingeight"
    collection = None
    id_field = "_id"
    order_by = None
    per_page = 100
    plotable = False
    creatable = False
    editable = True
    deletable = True

    def __init__(self, admin, table):
        self.admin = admin
        self.table = table
        self.admin.app.add_url_rule("/mongo/%s/" % self.collection, "mongo_" + self.collection, self.list_view)

        if self.creatable:
            pass
            # self.admin.app.add_url_rule("/db/%s/new/" % self.db_table, self.db_table + "_new", self.new_view)
            # self.admin.app.add_url_rule("/db/%s/new/save/" % self.db_table, self.db_table + "_save_new", self.save_new_view, methods=['POST'])

        if self.deletable:
            self.admin.app.add_url_rule("/mongo/%s/delete/" % self.collection, "mongo_" + self.collection + "_delete", self.delete_view)

        if self.editable:
            self.admin.app.add_url_rule("/mongo/%s/<id>/" % self.collection, "mongo_" + self.collection + "_obj", self.object_view)
            # self.admin.app.add_url_rule("/db/%s/<id>/save/" % self.db_table, self.db_table + "_save", self.save_view, methods=['POST'])

    def list_view(self):
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", self.per_page))
        order_by = request.args.get("order_by", self.order_by)
        if order_by and order_by.startswith("-"):
            ordering = (order_by[1:], -1)
        else:
            ordering = (order_by, 1)

        dt = time()
        results = self.table.find()
        if order_by:
            results = results.sort([ordering])
        count = results.count()
        results = list(results.skip(offset).limit(limit))
        exec_time = time() - dt

        columns = self.parse_columns(results)
        rows = [self.output_row(row, columns) for row in results]

        return render_template(
            "mongo_list.html",
            request=request,
            admin=self.admin,
            model=self,
            columns=columns,
            rows=rows,
            order_by=order_by,
            limit=limit,
            offset=offset,
            count=count,
            exec_time=exec_time
        )

    def object_view(self, id):
        object = self.table.find_one({"_id": ObjectId(id)})
        return render_template(
            "mongo_object.html",
            request=request,
            admin=self.admin,
            model=self,
            object=object
        )

    def delete_view(self):
        ids = request.args.get("ids", "")
        ids = [ObjectId(id.strip()) for id in ids.split(",")]
        self.table.remove({
            "_id": {
                "$in": ids
            }
        })
        return redirect("/mongo/%s/" % self.collection)

    def output_row(self, obj, columns):
        row = []
        for column in columns:
            value = obj.get(column)

            choice = None
            if value is not None and column in self.Fields.choices:
                choice = self.Fields.choices[column].get(value)

            row.append({
                "value": value,
                "type": type(value).__name__,
                "choice": choice,
                "column": column
            })

        return {
            "style": self.Row.style(obj),
            "row": row
        }

    def parse_columns(self, results):
        if "*" in self.Row.fields:
            columns = {}
            for row in results:
                for key, value in row.iteritems():
                    columns[key] = 0
            results = []
            for column in columns.keys():
                if column == self.id_field:
                    results.insert(0, column)
                else:
                    results.append(column)
        else:
            results = self.Row.fields
        return results

    def plot(self):
        raise NotImplementedError()

    class Fields:
        related = {}
        choices = {}
        tips = {}

    class Row:
        fields = ["*"]

        @staticmethod
        def style(row):
            return {}