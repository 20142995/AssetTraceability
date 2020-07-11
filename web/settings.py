#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import uuid

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = str(uuid.uuid4())
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR,'app.db')
    CONFIGFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    UPLOAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload")
    SQLALCHEMY_TRACK_MODIFICATIONS = False