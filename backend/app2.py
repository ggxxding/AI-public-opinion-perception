from flask import Flask, jsonify, render_template, request
from flask_apscheduler  import APScheduler # 引入APScheduler
from flask_cors import CORS
import os,json
import argparse
import getDataFromWeibo
# import prediction
import wordCloud
import datetime
import pymongo
import cluster
from collections import Counter
import pandas as pd
import jieba
import time
app = Flask(__name__)
CORS(app)

# 任务配置类
class SchedulerConfig(object):
	JOBS = [
		{
			'id': 'print_job',  # 任务id
			'func': '__main__:print_job',  # 任务执行程序
			'args': None,  # 执行程序参数
			'trigger': 'interval',  # 任务执行类型，定时器
			'seconds': 5,  # 任务执行时间，单位秒
		}
	]
# 定义任务执行程序
def print_job():
	print("间隔一天，执行定时任务")
	# getDataFromWeibo.main('人脸识别')
#为实例化的flask引入定时任务配置
# app.config.from_object(SchedulerConfig())

stopwords=['人脸','识别',' ']
with open('res/stopwords1893.csv','r') as f:
	for line in f.readlines():
		stopwords.append(line.strip().strip('\n'))
# print(stopwords)

china_city=['新疆','西藏','青海','甘肃','内蒙古','河北','山西','辽宁','吉林','黑龙江','江苏','浙江','安徽',
		   '福建','江西','山东','河南','湖北','湖南','广东','海南','四川','贵州','云南','陕西','甘肃','台湾','广西',
		   '宁夏','北京','天津','上海','重庆','香港','澳门']

myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
mydb = myclient['spider_weibo']
collist = mydb.list_collection_names()
mycol = mydb['selenium_weibo']


@app.route('/searching', methods=['POST'])
def upload():
	if request.method =='POST':
		keyword = request.form.get("keyword")
		cityDict=getDataFromWeibo.main(str(keyword))
		cityList=[{'name':str(x),'value':cityDict[x],'title':str(x)} for x in cityDict]
		# print(cityList)
	sentiment=prediction.predict()
	# print(sentiment)
	img_stream = wordCloud.draw()

	return jsonify({'cityList':cityList,'sentiment':sentiment,'img_stream':img_stream})

@app.route('/loadWeiboData', methods=['POST'])
def loadWeiboData():
	with open('res/data.txt','r') as f:
		res = json.loads(f.read())

	return jsonify(res)

if __name__ == '__main__':
	scheduler = APScheduler()  # 实例化APScheduler
	scheduler.init_app(app)  # 把任务列表载入实例flask
	scheduler.start()  # 启动任务计划
	app.run(host='0.0.0.0')
