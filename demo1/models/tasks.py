# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class TasksModel(SqlModel):
    db_table = "tasks"
    order_by = "id desc"
    name = u"События"
    icon = "icon-calendarthree"

    class Fields(SqlModel.Fields):
        related = {
            # "city_id": "cities.name",
            "user_id": "users.name",
            # "place_id": "places.address"
        }

