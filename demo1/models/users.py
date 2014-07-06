# -*- encoding:utf-8 -*-
from sqlalchemy.orm import create_session
from admin.models.sql import SqlModel


class UsersModel(SqlModel):
    db_table = "users"
    order_by = "id desc"
    name = u"Юзеры"
    icon = "icon-user"
    plotable = True

    def plot(self):
        session = create_session(self.admin.sql_engine)
        results = session.execute("select count(id), date(created_at) from users group by date(created_at)")
        labels = []
        values = []
        for result in results:
            value, label = result
            if not label or not value:
                continue
            labels.append(label.strftime("%d.%m"))
            values.append(value)
        session.close()

        return {
            "labels": labels,
            "datasets": [
                {
                    "fillColor": "rgba(120,120,120,0.5)",
                    "strokeColor": "rgba(120,120,120,1)",
                    "pointColor": "rgba(120,120,120,1)",
                    "pointStrokeColor": "#fff",
                    "data": values
                }
            ]
        }

    class Fields(SqlModel.Fields):
        related = {}
        choices = {}
        tips = {}
