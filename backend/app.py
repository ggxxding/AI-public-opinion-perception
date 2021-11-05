from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import os,json
import argparse
import getDataFromWeibo

app = Flask(__name__)
CORS(app)


@app.route('/searching', methods=['POST'])
def upload():
	if request.method =='POST':
		keyword = request.form.get("keyword")
		cityDict=getDataFromWeibo.main(str(keyword))
		cityList=[{'name':str(x),'value':cityDict[x],'title':str(x)} for x in cityDict]
		print(cityList)
	return jsonify(cityList)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
