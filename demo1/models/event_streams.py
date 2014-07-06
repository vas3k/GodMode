# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class EventStreamsModel(SqlModel):
    db_table = "event_streams"
    order_by = "id desc"
    name = u"Стримы"
    icon = "icon-branch"
