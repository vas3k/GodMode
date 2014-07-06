# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class NotificationsModel(SqlModel):
    db_table = "notifications"
    order_by = "id desc"
    name = u"Уведомления"
    icon = "icon-notification"

    class Fields(SqlModel.Fields):
        related = {
            "producer_id": "users.full_name",
            "consumer_id": "users.full_name",
            "task_id": "tasks.name",
        }