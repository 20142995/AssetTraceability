#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from web import db

class Assets(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64))
    network = db.Column(db.String(64))
    attribute = db.Column(db.String(255))
    equipment = db.Column(db.String(255))
    department = db.Column(db.String(255))
    user = db.Column(db.String(64))

    def __repr__(self):
        return '<Report %r>' %self.ip

    def to_json(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'network': self.network,
            'attribute': self.attribute,
            'equipment': self.equipment,
            'department': self.department,
            'user': self.user
        }