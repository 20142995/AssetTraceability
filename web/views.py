#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import re
import ipaddress
import os
import requests
import xlrd
from flask import Flask,request,render_template,flash,redirect,url_for
from .models import Assets
from .forms import EditConfigForm,SearchForm,UploadForm
from web.utils.logs import Logger
from web.utils.read_config import config_dict
from web import app,db




logger = Logger("debug",name=os.path.split(os.path.splitext(os.path.abspath(__file__))[0])[-1])

def remote_query(address,token,ip_str):
    rj = {}
    try:
        rj = requests.get(f"{address}/query",params={"ip_str":ip_str,"token":token}).json()
    except Exception as e:
        logger.error("查询失败,{}".format(e))
    return rj

def excel_to_list(excle_name,**kwargs):
    excle_list = []
    sheets = []
    workbook = xlrd.open_workbook(filename=excle_name)
    if kwargs.get("name",False):
        try:
            sheets.append(workbook.sheet_by_name(kwargs["name"]))
        except:
            logger.info("{} no have sheet name: {}".format(excle_name,kwargs["name"]))
    elif kwargs.get("index",False):
        try:
            sheets.append(workbook.sheet_by_index(kwargs["index"]))
        except:
            logger.info("{} no have index: {}".format(excle_name,kwargs["index"]))
    else:
        sheets = workbook.sheets()
    
    for i in range(0,len(sheets)):
        sheet_list = []
        if kwargs.get("row_or_col",True):
            for n in range(0,sheets[i].nrows):
                sheet_list.append(sheets[i].row_values(n))
        else:
            for n in range(0,sheets[i].ncols):
                sheet_list.append(sheets[i].col_values(n))
        excle_list.append(sheet_list)
    return excle_list

def deal_ip(ip_str):
    _list = []
    if re.search(r"^\d+\.\d+\.\d+\.\d+-\d+$",ip_str):
        net,a,b = re.findall(r"(\d+\.\d+\.\d+\.)(\d+)-(\d+)",ip_str)[0]
        if any([int(n) > 255 for n in [a,b]]):
            print("[-] error ip_net :{}".format(ip_str))
            return _list
        for i in range(int(a),int(b)+1):
            _list.append(net+str(i))
    elif re.search(r"^\d+\.\d+\.\d+\.\d+-\d+\.\d+\.\d+\.\d+$",ip_str):
        a,b,c,d,e,f,g,h = re.findall(r"(\d+)\.(\d+)\.(\d+)\.(\d+)-(\d+)\.(\d+)\.(\d+)\.(\d+)",ip_str)[0]
        if any([int(n) > 255 for n in [a,b,c,d,e,f,g,h]]):
            logger.info("[-] error:{}".format(ip_str))
            return _list
        for i in range(int(a),int(e)+1):
            for j in range(int(b),int(f)+1):
                for k in range(int(c),int(g)+1):
                    for l in range(int(d),int(h)+1):
                        _list.append("{}.{}.{}.{}".format(i,j,k,l))
    else:
        try:
            for ip in ipaddress.ip_network(ip_str).hosts():
                _list.append(ip.compressed)
            _list.append(ipaddress.ip_network(ip_str).network_address.compressed)
            _list.append(ipaddress.ip_network(ip_str).broadcast_address.compressed)
        except Exception as e:
            logger.info("[-] error ip_net :{}".format(ip_str))
            _list.append(ip_str)
    return _list

# 查询接口
@app.route('/query', methods=['GET'])
def query():
    config = config_dict(app.config["CONFIGFILE"])
    data = {}
    data.setdefault("list",[])
    ip_str = request.args.get("ip_str")
    token = request.args.get("token")
    if token == config.get("本地",{}).get("token",""):
        for ip in ip_str.split(","):
            assets = Assets.query.filter_by(ip=ip).all()
            for asset in assets:
                data['list'].append(asset.to_json())
    logger.info(f"单个查询结果:{data}")
    return data

# 查询界面
@app.route('/', methods=['GET','POST'])
def index():
    from_ip = request.remote_addr
    if from_ip != "127.0.0.1":
        return "403"
    config = config_dict(app.config["CONFIGFILE"])
    print(config)
    data = []
    form = SearchForm()
    if form.validate_on_submit():
        ip_str = ",".join([i.strip() for i in form.name.data.split("\n") if i.strip()])
        for name in config:
            address = config[name].get("address","")
            token = config[name].get("token","")
            if not address:continue
            logger.info(f"查询:{name},{address},{token},{ip_str}")
            rj = remote_query(address,token,ip_str).get("list",[])
            for i in range(len(rj)):
                rj[i].update({"name":name})
            data += rj
    logger.info(f"总个查询结果:{data}")
    return render_template('index.html', form=form, items=data)

# 修改配置
@app.route('/config', methods=['GET', 'POST'])
def config():
    from_ip = request.remote_addr
    if from_ip != "127.0.0.1":
        return "403"
    form = EditConfigForm(config=open(app.config['CONFIGFILE'],'r',encoding='utf8').read())
    if form.validate_on_submit():
        try:
            with open(app.config['CONFIGFILE'],'w',encoding='utf8') as f:
                f.write("\n".join([i.strip() for i in form.config.data.split("\n") if i.strip()]))
            logger.info("修改配置成功")
        except Exception as e:
            logger.error("修改配置失败,{}".format(e))
        flash(u'修改配置成功')
        return redirect(url_for('index'))
    return render_template('form.html', form=form,title="修改配置")

# 导入数据
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    from_ip = request.remote_addr
    if from_ip != "127.0.0.1":
        return "403"
    form = UploadForm()
    if form.validate_on_submit():
        filename = form.upfile.data.filename
        file_path = os.path.join(app.config["UPLOAD"],filename)
        if os.path.exists(file_path):
            flash("文件已存在")
            return redirect(url_for('upload'))
        form.upfile.data.save(file_path)
        flash("上传成功", 'ok')
        _list = excel_to_list(file_path,index=0)
        for item in _list[0][1:]:
            if len(item) != 5:
                continue
            if Assets.query.filter_by(network=item[0]).all():
                logger.info("[*] 网段已存在 :{}".format(item[0]))
                continue
            for ip in deal_ip(item[0]):
                Assets.query.filter_by(ip=ip).all()
                asset = Assets(ip=ip,network=item[0],attribute=item[1],equipment=item[2],department=item[3],user=item[4])
                db.session.add(asset)
                db.session.commit()
        flash("导入成功", 'ok')

    return render_template('form.html', form=form,title="导入数据")

@app.errorhandler(404)
def page_not_found(e):
    return "404"

@app.errorhandler(500)
def internal_server_error(e):
    return "500"
