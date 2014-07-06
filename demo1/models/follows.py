# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class FollowsModel(SqlModel):
    db_table = "follows"
    order_by = "id desc"
    name = u"Друзья"
    icon = "icon-groups-friends"

    class Fields(SqlModel.Fields):
        related = {
            "user_1_id": "users.full_name",
            "user_2_id": "users.full_name"
        }