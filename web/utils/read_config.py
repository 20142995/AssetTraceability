#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import configparser
from web import app

def config_dict(cfgpath):
    config = {}
    conf = configparser.ConfigParser()
    conf.read(cfgpath, encoding="utf-8")
    sections = conf.sections()
    for item in sections:
        config.setdefault(item,{})
        config[item].update(dict(conf.items(item)))
    return config



