import numpy as np
import gensim
import re
from ltp import LTP
ltp = LTP()
import pymongo

myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
mydb = myclient['spider_weibo']
mycol = mydb['selenium_weibo']


word_vectors = gensim.models.KeyedVectors.load_word2vec_format('res/word_vectors.bin', binary = True)
print('loaded')
#文本 -> 向量
def preprocess(text):
    ''''''
    sen_vec = np.zeros((1,128))
    segment,_ = ltp.seg([text]) #return = [['word1','word2'...]]

    valid_word_cnt = 0
    for word in segment[0]:
        try:
            print(word)
            sen_vec += word_vectors[word]
            valid_word_cnt+=1
        except KeyError as e:
            print(e)
            print('字典不存在，跳过')
            continue
    print('有效词汇:',valid_word_cnt,segment[0])
    if valid_word_cnt >0:
        sen_vec = sen_vec*(1.0/valid_word_cnt)
    sen_vec = sen_vec *(1.0/np.linalg.norm(sen_vec))
    return sen_vec

def singlePass(all_vec , threshold):
    '''all_vec: [arr1,arr2,arr3...] '''
    topic_cnt=0
    topic_serial=[]
    text_vec = []
    for vec in all_vec:
        if topic_cnt == 0 :
            text_vec = vec
            topic_cnt+=1
            topic_serial = [topic_cnt]
        else:
            sim_vec = np.dot(vec,text_vec.T)

            max_value = np.max(sim_vec)
            topic_ser = topic_serial[np.argmax(sim_vec)]
            print(sim_vec,max_value,topic_ser,topic_serial)
            print('topic_ser:', topic_ser, "max_value:", max_value)
            text_vec = np.vstack([text_vec, vec])
            if max_value >= threshold:
                topic_serial.append(topic_ser)
            else:
                topic_cnt+=1
                topic_serial.append(topic_cnt)
    print('最终矩阵shape:',text_vec.shape)
    return topic_cnt,topic_serial



def main():
    data=[]
    for weiboData in mycol.find({},{'label':1,'created_at':1,'location':1,'isLongText':1,'text':1,'longText':1}):
        if weiboData['isLongText']==True:
            data.append(weiboData['longText'])
        else:
            data.append(weiboData['text'])
    preprocessedData=[] #与data对应的128维向量
    for sentence in data:
        print(sentence)
        vec = preprocess(sentence)
        preprocessedData.append(vec)
    print('begin singlepass')
    topic_cnt, topic_serial = singlePass(preprocessedData, 0.1)
    print(topic_cnt)#簇数量
    print(topic_serial)#长度与data相同，表示对应data中数据所属簇
    #sorted(zip(a,b),key = lambda x:x[0])


if __name__ == '__main__':
    main()