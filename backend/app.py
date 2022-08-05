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
	getDataFromWeibo.main('人脸识别')
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
	if request.method =='POST':
		keyword = request.form.get("keyword")
		countDict={}
		timeDict={}
		cityDict={}
		timeList={}
		cityList={}
		textDict={}
		texts_from_now={}
		wordCloudList={}
		word_cloud={}
		word_cloud_stream={}
		cluster_result={}
		sentiment_result = {}
		barData={'data':{},'cities':{}}
		for label in mycol.distinct('label'):
			countDict [label] = {'24h':0,'30d':0,'90d':0,'365d':0}
			timeDict [label] = {}
			cityDict [label] = 		{'24h':{},'30d':{},'90d':{},'365d':{},}
			barData['data'][label] = {'24h':[],'30d':[],'90d':[],'365d':[],}
			barData['cities'][label] = {'24h':[],'30d':[],'90d':[],'365d':[],}
			textDict[label] =  {'2022':[],'2021':[],'2020':[],'earlier':[],}
			wordCloudList [label] = {'2022':[],'2021':[],'2020':[],'earlier':[],}
			texts_from_now[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
			word_cloud[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
			word_cloud_stream[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
			cluster_result[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
			sentiment_result[label] = {'24h':[{'name':'pos','value':0},{'name':'neg','value':0}],
									   '30d':[{'name':'pos','value':0},{'name':'neg','value':0}],
									   '90d':[{'name':'pos','value':0},{'name':'neg','value':0}],
									   '365d':[{'name':'pos','value':0},{'name':'neg','value':0}]}
			for i in  mycol.distinct('location'):
				if len(i.split(' ')[0])<5 and i.split(' ')[0] in china_city:
					cityDict[label]['24h'][i.split(' ')[0]] = 0
					cityDict[label]['30d'][i.split(' ')[0]] = 0
					cityDict[label]['90d'][i.split(' ')[0]] = 0
					cityDict[label]['365d'][i.split(' ')[0]] = 0
			temp = {
				'2022': [0 for i in range(12)],
				'2021': [0 for i in range(12)],
				'2020': [0 for i in range(12)],
				'earlier': [0 for i in range(12)],
			}
			timeList[label] =  temp
			cityList[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
		# now = datetime.datetime.now()
		now = datetime.datetime(2022,4,13,0,0,0)
		for weiboData in mycol.find({},{'label':1,'created_at':1,'location':1,'isLongText':1,'text':1,'longText':1,'sentiment':1}):
			location = weiboData['location'].split(' ')[0]
			weiboData_time = datetime.datetime.strptime(weiboData['created_at'],'%Y/%m/%d %H:%M')
			time_from_now = now - weiboData_time

			if time_from_now.days >= 0 :
				if time_from_now.days == 0:
					countDict[weiboData['label']]['24h'] += 1
					if location in cityDict[weiboData['label']]['24h'].keys():
						cityDict[weiboData['label']]['24h'][location] += 1
					if weiboData['isLongText']==False:
						texts_from_now[weiboData['label']]['24h'].append(weiboData['text'])
						# print(weiboData['text'])
						if weiboData['sentiment'] == 'positive':
							sentiment_result[weiboData['label']]['24h'][0]['value'] += 1
						else:
							sentiment_result[weiboData['label']]['24h'][1]['value'] += 1

				if time_from_now.days <= 29:
					countDict[weiboData['label']]['30d'] += 1
					if location in cityDict[weiboData['label']]['30d'].keys():
						cityDict[weiboData['label']]['30d'][location] += 1
					if weiboData['isLongText']==False:
						texts_from_now[weiboData['label']]['30d'].append(weiboData['text'])
						# print(weiboData['text'])
						if weiboData['sentiment'] == 'positive':
							sentiment_result[weiboData['label']]['30d'][0]['value'] += 1
						else:
							sentiment_result[weiboData['label']]['30d'][1]['value'] += 1


				if time_from_now.days <= 89:
					countDict[weiboData['label']]['90d'] += 1
					if location in cityDict[weiboData['label']]['90d'].keys():
						cityDict[weiboData['label']]['90d'][location] += 1

					if weiboData['sentiment'] == 'positive':
						sentiment_result[weiboData['label']]['90d'][0]['value'] += 1
					else:
						sentiment_result[weiboData['label']]['90d'][1]['value'] += 1
				if time_from_now.days <= 364:
					countDict[weiboData['label']]['365d'] += 1
					if location in cityDict[weiboData['label']]['365d'].keys():
						cityDict[weiboData['label']]['365d'][location] += 1
					if weiboData['sentiment'] == 'positive':
						sentiment_result[weiboData['label']]['365d'][0]['value'] += 1
					else:
						sentiment_result[weiboData['label']]['365d'][1]['value'] += 1



			if weiboData['created_at'][:4] not in ['2022','2021','2020']:
				if weiboData['isLongText']==True:
					textDict[weiboData['label']]['earlier'].append(weiboData['longText'])
				else:
					textDict[weiboData['label']]['earlier'].append(weiboData['text'])
			else:
				if weiboData['isLongText']==True:
					textDict[weiboData['label']][weiboData['created_at'][:4]].append(weiboData['longText'])
				else:
					textDict[weiboData['label']][weiboData['created_at'][:4]].append(weiboData['text'])

			year_month = weiboData['created_at'][:7]
			if year_month not in timeDict[weiboData['label']].keys():
				timeDict[weiboData['label']][year_month] = 1
			else:
				timeDict[weiboData['label']][year_month] += 1


		#聚类 词频
		for keyword in texts_from_now:
			start = time.perf_counter()
			cluster_result[keyword]['24h'] = cluster.main(texts_from_now[keyword]['24h'])
			end = time.perf_counter()
			print(end-start)
			if texts_from_now[keyword]['24h']!= []:
				word_cloud_stream[keyword]['24h'] = wordCloud.draw(texts_from_now[keyword]['24h'], keyword)
			else:
				word_cloud_stream[keyword]['24h'] = wordCloud.draw(['empty input'], keyword)

		for keyword in cluster_result:
			for key in cluster_result[keyword]:
				temp_result = {'nodes':[],'links':[],'categories':[]}
				# print([x[0] for x in cluster_result[keyword][key]])
				count = Counter([x[0] for x in cluster_result[keyword][key]])#未排序

				# print(key,keyword)
				# print('count: ',count) #{4:12, 5:11,...}
				# print(cluster_result[keyword][key])
				for num in [x[0] for x in count.most_common(5)]:
					# print('num:',num)
					temp_result['categories'].append({'name': str(num)})

					num_texts = [x[1] for x in  cluster_result[keyword][key] if x[0]==num]
					word_count=Counter()
					for text in num_texts:
						cut_list = [x for x in jieba.lcut(text) if x not in stopwords]
						word_count = word_count + Counter(cut_list)
					# print('wordcount:',word_count)

					append_word_count = 0
					for word in [x[0] for x in word_count.most_common(5)]:
						temp_result['nodes'].append({'id':word+'['+str(num)+']','name':word+'['+str(num)+']','value':word_count[word],'category':str(num)})
						for node in temp_result['nodes']:
							if node['category'] == str(num) and node['id']!= word+'['+str(num)+']':
								temp_result['links'].append({'source':word+'['+str(num)+']','target':node['id']})
						append_word_count += 1
						if append_word_count >=10:
							break
					if len(temp_result['categories']) >=5:
						break
				cluster_result[keyword][key] = temp_result


		for keyword in timeDict:
			for key in timeDict[keyword]:
				date_key = datetime.datetime.strptime(key, '%Y/%m')
				if date_key.year not in [2022,2021,2020]:
					timeList[keyword]['earlier'][date_key.month-1]=timeDict[keyword][key]
				else:
					timeList[keyword][str(date_key.year)][date_key.month-1]=timeDict[keyword][key]

		for keyword in cityDict:
			for key in cityDict[keyword]:
				cityList[keyword][key]=[{'name':str(x),'value':cityDict[keyword][key][x],'title':str(x)} for x in cityDict[keyword][key]]

				ordered = sorted(cityDict[keyword][key].items(),key=lambda x:x[1],reverse=True)
				cityList[keyword][key].append({'name': 'max', 'value': ordered[0][1], 'title': 'max'})
				cityList[keyword][key].append({'name': 'min', 'value': ordered[-1][1], 'title': 'min'})

				avg = (ordered[-5][1]+ordered[4][1])/2
				barData['data'][keyword][key] = [ordered[0][1],ordered[1][1],ordered[2][1],ordered[3][1],ordered[4][1],
												 avg,avg,avg,
												 ordered[-5][1],ordered[-4][1],ordered[-3][1],ordered[-2][1],ordered[-1][1]]
				barData['cities'][keyword][key] = [ordered[0][0],ordered[1][0],ordered[2][0],ordered[3][0],ordered[4][0],
												 '','……','',
												 ordered[-5][0],ordered[-4][0],ordered[-3][0],ordered[-2][0],ordered[-1][0]]
		# for keyword in textDict:
		# 	for time in textDict[keyword]:
		# 		wordCloudList[keyword][time] = wordCloud.draw(textDict[keyword][time])
		wordCloudList={}
	# sentiment=prediction.predict()
	# print(sentiment)
	# img_stream = wordCloud.draw()

	return jsonify({'cityList':cityList, 'timeList':timeList, 'barData':barData, 'wordCloudList':wordCloudList,
					'countDict':countDict , 'wordCloudStream':word_cloud_stream ,'clusterResult':cluster_result,
					'sentiment_result':sentiment_result})

if __name__ == '__main__':
	scheduler = APScheduler()  # 实例化APScheduler
	scheduler.init_app(app)  # 把任务列表载入实例flask
	scheduler.start()  # 启动任务计划
	app.run(host='0.0.0.0')
