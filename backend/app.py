from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os,json
import argparse
import getDataFromWeibo
import prediction
import wordCloud
app = Flask(__name__)
CORS(app)


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

if __name__ == '__main__':
    app.run(host='0.0.0.0')
