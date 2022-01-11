from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os,json
import argparse
# import getDataFromWeibo
# import prediction
import wordCloud
import datetime
import pymongo
app = Flask(__name__)
CORS(app)

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
		print(cityList)
	sentiment=prediction.predict()
	print(sentiment)
	img_stream = wordCloud.draw()

	return jsonify({'cityList':cityList,'sentiment':sentiment,'img_stream':img_stream})

@app.route('/loadWeiboData', methods=['POST'])
def loadWeiboData():
	if request.method =='POST':
		keyword = request.form.get("keyword")
		timeDict={}
		cityDict={}
		timeList={}
		cityList={}
		textDict={}
		wordCloudList={}
		barData={'data':{},'cities':{}}
		for label in mycol.distinct('label'):
			timeDict [label] = {}
			cityDict [label] = {'y2021':{},'y2020':{},'y2019':{},'earlier':{},}
			barData['data'][label] = {'y2021':[],'y2020':[],'y2019':[],'earlier':[],}
			barData['cities'][label] = {'y2021':[],'y2020':[],'y2019':[],'earlier':[],}
			textDict[label] =  {'y2021':[],'y2020':[],'y2019':[],'earlier':[],}
			wordCloudList [label] = {'y2021':[],'y2020':[],'y2019':[],'earlier':[],}
			for i in  mycol.distinct('location'):
				if len(i.split(' ')[0])<5 and i.split(' ')[0] in china_city:
					cityDict[label]['y2021'][i.split(' ')[0]] = 0
					cityDict[label]['y2020'][i.split(' ')[0]] = 0
					cityDict[label]['y2019'][i.split(' ')[0]] = 0
					cityDict[label]['earlier'][i.split(' ')[0]] = 0
			temp = {
				'y2021': [0 for i in range(12)],
				'y2020': [0 for i in range(12)],
				'y2019': [0 for i in range(12)],
				'earlier': [0 for i in range(12)],
			}
			timeList[label] =  temp
			cityList[label] = {'y2021':[],'y2020':[], 'y2019':[], 'earlier':[]}

		for weiboData in mycol.find({},{'label':1,'created_at':1,'location':1,'isLongText':1,'text':1,'longText':1}):
			location = weiboData['location'].split(' ')[0]

			if weiboData['created_at'][:4] not in ['2021','2020','2019']:
				if weiboData['isLongText']==True:
					textDict[weiboData['label']]['earlier'].append(weiboData['longText'])
				else:
					textDict[weiboData['label']]['earlier'].append(weiboData['text'])

				if location in cityDict[weiboData['label']]['earlier'].keys():
					cityDict[weiboData['label']]['earlier'][location]+=1
			else:
				if weiboData['isLongText']==True:
					textDict[weiboData['label']]['y'+weiboData['created_at'][:4]].append(weiboData['longText'])
				else:
					textDict[weiboData['label']]['y'+weiboData['created_at'][:4]].append(weiboData['text'])

				if location in cityDict[weiboData['label']]['y'+weiboData['created_at'][:4]].keys():
					cityDict[weiboData['label']]['y'+weiboData['created_at'][:4]][location]+=1
			year_month = weiboData['created_at'][:7]
			if year_month not in timeDict[weiboData['label']].keys():
				timeDict[weiboData['label']][year_month] = 1
			else:
				timeDict[weiboData['label']][year_month] += 1

		for keyword in timeDict:
			for key in timeDict[keyword]:
				date_key = datetime.datetime.strptime(key, '%Y/%m')
				if date_key.year not in [2021,2020,2019]:
					timeList[keyword]['earlier'][date_key.month-1]=timeDict[keyword][key]
				else:
					timeList[keyword]['y' + str(date_key.year)][date_key.month-1]=timeDict[keyword][key]
		for keyword in cityDict:
			for key in cityDict[keyword]:
				cityList[keyword][key]=[{'name':str(x),'value':cityDict[keyword][key][x],'title':str(x)} for x in cityDict[keyword][key]]
				ordered = sorted(cityDict[keyword][key].items(),key=lambda x:x[1],reverse=False)
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

	return jsonify({'cityList':cityList, 'timeList':timeList, 'barData':barData, 'wordCloudList':wordCloudList})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
