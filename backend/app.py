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
		timeDict = {}
		cityDict = {}
		for i in  mycol.distinct('location'):
			if len(i.split(' ')[0])<5:
				cityDict[i.split(' ')[0]] = 0
		for weiboData in mycol.find({},{'created_at':1,'location':1,'isLongText':1,'text':1,'longText':1}):
			location = weiboData['location'].split(' ')[0]
			if location in cityDict.keys():
				cityDict[location]+=1

			year_month = weiboData['created_at'][:7]
			if year_month not in timeDict.keys():
				timeDict[year_month] = 1
			else:
				timeDict[year_month] += 1

		timeList = {
			'y2021': [0 for i in range(12)],
			'y2020': [0 for i in range(12)],
			'y2019': [0 for i in range(12)],
			'earlier': [0 for i in range(12)],
		}
		for key in timeDict:
			date_key = datetime.datetime.strptime(key, '%Y/%m')
			if date_key.year not in [2021,2020,2019]:
				timeList['earlier'][date_key.month-1]=timeDict[key]
			else:
				timeList['y' + str(date_key.year)][date_key.month-1]=timeDict[key]
		# print(timeList)
		# print(timeDict)

		cityList=[{'name':str(x),'value':cityDict[x],'title':str(x)} for x in cityDict]

	# sentiment=prediction.predict()
	# print(sentiment)
	# img_stream = wordCloud.draw()

	return jsonify({'cityList':cityList, 'timeList':timeList})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
