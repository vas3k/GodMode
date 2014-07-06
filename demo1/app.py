# -*- encoding:utf-8 -*-
import settings
from admin.app import AdminApp

if __name__ == "__main__":
    app = AdminApp(settings)
    app.run()