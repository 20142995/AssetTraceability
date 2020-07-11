#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Required

from flask_wtf.file import FileField, FileRequired, FileAllowed

class SearchForm(FlaskForm):
    name = TextAreaField(u'ip', validators=[Required(message=u'请输入ip关键字')],render_kw={"rows":5})
    submit = SubmitField(u'查询')

class EditConfigForm(FlaskForm):
    config = TextAreaField('配置文件', validators=[Required()],render_kw={"rows":15})
    submit = SubmitField(u'保存')

class UploadForm(FlaskForm):
    upfile = FileField(validators=[FileRequired(message=u'请输入选择文件'),FileAllowed(['xls','xlsx'], '只接收excel(.xls,.xlsx)类型的文件')])
    submit = SubmitField(u'上传')