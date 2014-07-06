# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class CommentsModel(SqlModel):
    db_table = "comments"
    order_by = "id desc"
    name = u"Комментарии"
    icon = "icon-commenttyping"

    class Fields(SqlModel.Fields):
        related = {
            "user_id": "users.full_name",
            "task_id": "tasks.name",
        }

    class Row(SqlModel.Row):
        fields = ["*"]

