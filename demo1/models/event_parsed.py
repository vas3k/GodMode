# -*- encoding:utf-8 -*-
from admin.models.sql import SqlModel


class EventParsedModel(SqlModel):
    db_table = "event_parsed"
    order_by = "updated_at desc"
    name = u"Парседы"
    icon = "icon-calendaralt-cronjobs"

    class Fields(SqlModel.Fields):
        related = {
            "producer_id": "event_producers.full_name",
            "source_id": "event_sources.name",
            "stream_id": "event_streams.name",
            "category_id": "categories.name"
        }
        choices = {}
        tips = {}

    class Row(SqlModel.Row):
        fields = ["*"]

        @staticmethod
        def style(row):
            if row.is_spam or not row.is_visible:
                return {
                    "color": "#999"
                }

            if row.task_id:
                return {
                    "background-color": "rgba(128, 255, 128, 0.2)"
                }

            if row.name and row.city_id and row.category_id and row.start and row.producer_id:
                return {
                    "background-color": "rgba(255, 255, 128, 0.2)"
                }

            return {
                "background-color": "rgba(255, 128, 128, 0.2)"
            }
