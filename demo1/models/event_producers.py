# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class EventProducersModel(SqlModel):
    db_table = "event_producers"
    order_by = "id desc"
    name = u"Продюсеры"
    icon = "icon-websitealt"

    class Fields(SqlModel.Fields):
        related = {
            "user_id": "users.full_name",
            "category_id": "categories.name",
        }
        choices = {}
        tips = {}