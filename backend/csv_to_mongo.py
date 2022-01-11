import pandas as pd
import pymongo
import datetime

myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
mydb = myclient['spider_weibo']
collist = mydb.list_collection_names()
mycol = mydb['selenium_weibo']
uid_loc_dict={}

# Index(['label', 'text', 'longText', 'name', 'uid', 'location', 'isLongText','created_at']
df = pd.read_csv('weibo_220110_2.csv')
df = df.values

for row in df:
    created_at =  datetime.datetime.strptime(row[7].split(' ')[0],'%Y/%m/%d')
    created_at = datetime.datetime.strftime(created_at,'%Y/%m/%d')
    created_at = created_at +' '+ row[7].split(' ')[1]
    temp={'label':row[0], 'text':row[1],'longText':row[2],'name':row[3],'uid': str(row[4]),'location':row[5],
          'isLongText':row[6],'created_at':created_at,'from_mac':True}
    if type(row[1])==str and '人工智能' in row[1] and not mycol.find_one({'text':row[1]}):
        print('insert')
        temp['longText']=''
        mycol.insert_one(temp)
    elif type(row[2])==str and '人工智能' in row[2] and not mycol.find_one({'longText':row[2]}):
        print('insert')
        temp['text']=''
        mycol.insert_one(temp)