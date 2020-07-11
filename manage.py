#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# 运行管理

from web import app
from flask_migrate import MigrateCommand
from flask_script import Manager


manager = Manager(app)
manager.add_command('db',MigrateCommand)

'''
python3 manage.py db init


python3 manage.py db migrate
python3 manage.py db upgrade


python3 manage.py runserver -r -d
'''

if __name__ == '__main__':
    manager.run()

