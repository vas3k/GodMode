# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class EventSourcesModel(SqlModel):
    db_table = "event_sources"
    order_by = "id desc"
    name = u"Источники"
    icon = "icon-branch"

    class Fields(SqlModel.Fields):
        related = {
            "producer_id": "event_producers.full_name",
        }
        choices = {}
        tips = {}

