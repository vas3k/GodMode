# -*- encoding:utf-8 -*-
from flask import render_template


class PagePlugin(object):
    title = "New page"
    full_body = True
    template = "plugins/page.html"

    def plugin(self, request, admin):
        data = self.run(admin)
        return render_template(
            self.template,
            request=request,
            admin=admin,
            plugin=self,
            data=data,
            full_body=self.full_body
        )

    def run(self, admin):
        # OVERWRITE ME
        return {}