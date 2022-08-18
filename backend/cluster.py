import numpy as np

import gensim
import spacy
import jieba
import re
# from ltp import LTP
# ltp = LTP()
import pymongo
import pandas as pd

myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
mydb = myclient['spider_weibo']
mycol = mydb['selenium_weibo']

topic_cnt=0
topic_serial=[]
text_vec = []

# word_vectors = gensim.models.KeyedVectors.load_word2vec_format('res/word_vectors.bin', binary = True)
nlp = spacy.load('zh_core_web_md')# lg on 214
word_vectors = nlp.vocab
print('loaded')
#文本 -> 向量
def preprocess(text):
    ''''''
    sen_vec = np.zeros((1,300))
    # segment,_ = ltp.seg([text]) #return = [['word1','word2'...]]
    segment = jieba.lcut(text)

    valid_word_cnt = 0
    for word in segment[0]:
        try:
            # print(word)
            sen_vec += word_vectors[word].vector
            valid_word_cnt+=1
        except KeyError as e:
            # print(e)
            # print('字典不存在，跳过')
            continue

    if valid_word_cnt >0:
        sen_vec = sen_vec*(1.0/valid_word_cnt)
        sen_vec = sen_vec *(1.0/np.linalg.norm(sen_vec))
    return sen_vec,segment[0]

def singlePass(sen_vec , threshold):
    '''all_vec: [arr1,arr2,arr3...] '''
    global text_vec
    global topic_serial
    global topic_cnt


    if topic_cnt == 0 :
        text_vec = sen_vec
        topic_cnt+=1
        topic_serial = [topic_cnt]
    else:
        sim_vec = np.dot(sen_vec,text_vec.T)
        # print('sim_vec:',sim_vec)
        max_value = np.max(sim_vec)
        topic_ser = topic_serial[np.argmax(sim_vec)]
        # print('topic_ser:', topic_ser, "max_value:", max_value)
        text_vec = np.vstack([text_vec, sen_vec])
        if max_value >= threshold:
            topic_serial.append(topic_ser)
        else:
            topic_cnt+=1
            topic_serial.append(topic_cnt)



def main(texts):

    data = texts
    # for weiboData in mycol.find({},{'label':1,'created_at':1,'location':1,'isLongText':1,'text':1,'longText':1}).limit(100000):
    #     if weiboData['isLongText']==True:
    #         pass
    #     elif len(weiboData['text'])<100:
    #         data.append(weiboData['text'])
    print('begin singlepass')
    preprocessedData=[] #与data对应的128维向量
    for sentence in data:
        # print(sentence)
        vec, seg = preprocess(sentence) #vec:向量 seg:分词后的文本列表
        singlePass(vec, 0.5)
        preprocessedData.append(sentence)
        # print(topic_serial)#长度与data相同，表示对应data中数据所属簇
        # print('topic_count: ',topic_cnt)#簇数量
    # sorted(zip(a,b),key = lambda x:x[0])
    sorted_text = sorted(zip(topic_serial,preprocessedData), key = lambda x:x[0])
    df = pd.DataFrame(sorted_text,columns=['topic_serial', 'text'])
    df.to_csv('cluster.csv',index=False)
    return sorted_text



if __name__ == '__main__':
    main(['测试','测试测试'])