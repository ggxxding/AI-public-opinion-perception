import pymongo
import pandas as pd

myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
mydb = myclient['spider_weibo']
collist = mydb.list_collection_names()
mycol = mydb['selenium_weibo']

# # 三个字段 name, site, age
# nme = ["Google", "Runoob", "Taobao", "Wiki"]
# st = ["www.google.com", "www.runoob.com", "www.taobao.com", "www.wikipedia.org"]
# ag = [90, 40, 80, 98]
#
# # 字典
# dict = {'name': nme, 'site': st, 'age': ag}
#
# df = pd.DataFrame(dict)
#
# # 保存 dataframe
# df.to_csv('site.csv')

uid,text,sentiment,created_at=[],[],[],[]
for i in mycol.find({'label':'随1申码','longText':''},{'text':1,'sentiment':1,'created_at':1}):
    text.append(i['text'])
    sentiment.append(i['sentiment'])
    created_at.append(i['created_at'])

df = pd.DataFrame({'text':text,'sentiment':sentiment,'created_at':created_at})
df.to_csv('mongo_data.csv',index=False, sep=' ')