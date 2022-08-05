from senta import Senta
import pymongo

myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
mydb = myclient['spider_weibo']
collist = mydb.list_collection_names()
mycol = mydb['selenium_weibo']

my_senta = Senta()
# 获取目前支持的情感预训练模型, 我们开放了以ERNIE 1.0 large(中文)、ERNIE 2.0 large(英文)和RoBERTa large(英文)作为初始化的SKEP模型
print(my_senta.get_support_model()) # ["ernie_1.0_skep_large_ch", "ernie_2.0_skep_large_en", "roberta_skep_large_en"]
# 获取目前支持的预测任务
print(my_senta.get_support_task()) # ["sentiment_classify", "aspect_sentiment_classify", "extraction"]
# 选择是否使用gpu
use_cuda = True # 设置True or False
# 预测中文句子级情感分类任务
my_senta.init_model(model_class="ernie_1.0_skep_large_ch", task="sentiment_classify", use_cuda=use_cuda)
# texts = ["中山大学是岭南第一学府"]

def predict_all():
    count=0
    for x in mycol.find({'sentiment':None}):#senntiment=null
        if 'sentiment' not in list(x.keys()):
            if x['isLongText']==True:
                result = my_senta.predict(x['longText'])[0][1]
            else:
                result = my_senta.predict(x['text'])[0][1]

            upsert = mycol.update_one({'_id':x['_id']}, {'$set':{'sentiment':result}},upsert=True)
            if upsert.modified_count == 0:
                print('err: modified_count == 0')
            if count%100==0:
                print(count)
            count+=1
def predict_text( text ):
    result = my_senta.predict(text)[0][1]
    return result

if __name__ == '__main__':
    predict_all()