# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class ClientsModel(SqlModel):
    db_table = "clients"
    order_by = "id desc"
    name = u"Сессии юзеров"
    icon = "icon-time"

