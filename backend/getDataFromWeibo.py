from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import time
import os
import csv
import json
import pymongo

delay=1/0.3
print(delay)
base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/3493557293',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    }
class SaveCSV(object):

    def save(self, keyword_list,path, item):
        """
        保存csv方法
        :param keyword_list: 保存文件的字段或者说是表头
        :param path: 保存文件路径和名字
        :param item: 要保存的字典对象
        :return:
        """
        try:
            # 第一次打开文件时，第一行写入表头
            if not os.path.exists(path):
                with open(path, "w", newline='', encoding='utf-8-sig') as csvfile:  # newline='' 去除空白行
                    writer = csv.DictWriter(csvfile, fieldnames=keyword_list)  # 写字典的方法
                    writer.writeheader()  # 写表头的方法

            # 接下来追加写入内容
            with open(path, "a", newline='', encoding='utf-8-sig') as csvfile:  # newline='' 一定要写，否则写入数据有空白行
                writer = csv.DictWriter(csvfile, fieldnames=keyword_list)
                writer.writerow(item)  # 按行写入数据
                print("^_^ write success")

        except Exception as e:
            print("write error==>", e)
            # 记录错误数据
            with open("error.txt", "w") as f:
                f.write(json.dumps(item) + ",\n")
            pass

def get_page(page,title): #得到页面的请求，params是我们要根据网页填的，就是下图中的Query String里的参数
    params = {
        'containerid': '100103type=1&q='+title,

        'page': page,#page是就是当前处于第几页，是我们要实现翻页必须修改的内容。

        'page_type':'searchall'
    }
    '''
            'type':'all',
        'queryVal':title,
        'featurecode':'20000320',
        'luicode':'10000011',
        'title':title,
    '''
    """https://m.weibo.cn/api/container/getIndex?containerid=231522type=1&t=10&q=#人工智能#&isnewpage=1&luicode=10000011&lfid=100103type=38&
    q=人工智能&t=0&page_type=searchall&page=2"""
    #https://m.weibo.cn/api/container/getIndex?containerid=100103type=1&q=人工智能&t=0&page_type=searchall&page=2
    url = base_url + urlencode(params)
    print(url)

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('page:',page)
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)

# 解析接口返回的json字符串
def parse_page(json , label):
    res = []
    if json:
        items = json.get('data').get('cards')
        #print(items)
        for i in items:
            if i == None:
                continue
            #item = i.get('mblog')
            card_group = i.get('card_group')
            for card in card_group:
                item = card.get('mblog')
                if item !=None:
                    break
            if item ==None:
                continue
            weibo = {}
            weibo['id'] = item.get('id')
            weibo['uid'] = item.get('user').get('id')
            weibo['label'] = label
            weibo['text'] = pq(item.get('text')).text().replace(" ", "").replace("\n" , "")
            weibo['location']=get_user_location(item)
            print('位置：',weibo['location'])
            weibo['created_at'] = item.get('created_at') #Thu Dec 16 14:51:31 +0800 2021
            weibo['isLongText'] = item.get('isLongText') #https://m.weibo.cn/statuses/extend?id=4719013772660338
            weibo['longText'] = ''
            print(weibo['isLongText'])
            print(weibo['isLongText']==True)
            if weibo['isLongText']==True:
                try:
                    time.sleep(delay)
                    url = 'https://m.weibo.cn/statuses/extend?id='+weibo['id']
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        print(weibo['id'])
                        print(response.json())
                        longText = response.json().get('data').get('longTextContent')
                        weibo['longText'] = longText
                except requests.ConnectionError as e:
                    print('Error', e.args)
                    weibo['longText'] = '获取失败'
            res.append(weibo)
    return res

def get_user_location(mblog):
    '''输入json中mblog对象，输出location字符串'''
    user=mblog.get('user')
    profile_url=user.get('profile_url')
    uid=str(user.get('id'))

    containerid=get_containerid(uid)
    if containerid==None:
        print('*****containerid为空')
        return '未知'
    'https://m.weibo.cn/api/container/getIndex?uid=1852299857&' \
    'luicode=10000011&lfid=100103type%3D1%26q%3D%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&type=uid&value=1852299857&containerid=2302831852299857'


    #pre='https://m.weibo.cn/api/container/getIndex?'
    params = {
        'type':'uid',
        'value': uid,
        'containerid': containerid,
    }
    #        'uid': uid,
    #        'luicode':'10000011',
    #   'lfid':'100103type=1',
    url = base_url + urlencode(params)
    #url=pre+'uid='+uid+'&luicode=10000011&lfid=100103type=1&type=uid&value='+uid+'&containerid='+containerid

    try:
        time.sleep(delay)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            #print(response.json())
            cards=response.json().get('data').get('cards')
            location='未知'
            if cards==[]:
                return location
            else:
                for card in cards:
                    card_group=card.get('card_group')
                    if card_group!=None:

                        for group in card_group:
                            if group.get('item_name')=='所在地':
                                location=group.get('item_content')
                                break
            if location=='未知':
                print(url)
                print(cards)
            return location
    except requests.ConnectionError as e:
        print('ConnectionError', e.args)



def get_containerid(uid):
    '''输入用户uid，输出主页包含位置信息的containerid
    部分请求返回{"ok":0,"msg":"这里还没有内容","data":{"cards":[]}}，原因可能是没有登陆，待解决
    '''
    'https://m.weibo.cn/api/container/getIndex?uid=1852299857&luicode=10000011&'
    'lfid=100103type%3D1%26q%3D%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&type=uid&value=1852299857'
    'https://m.weibo.cn/api/container/getIndex?type=uid&value=6248471088'
    pre='https://m.weibo.cn/api/container/getIndex?'
    params = {
        #'uid': uid,
        'type':'uid',
        #'luicode':'10000011',
        #'lfid':'100103type=1',
        'value': uid,
    }
    url = pre + urlencode(params)
    #print('从uid获取containerid的url:',url)
    try:
        time.sleep(delay)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tabsInfo=response.json().get('data').get('tabsInfo')
            #print('tabsinfo:',tabsInfo)
            containerid=None
            try:
                tabs=tabsInfo.get('tabs')#tabs0-3对应微博用户主页的4个标签，地址在第一页
                for tab in tabs:
                    if tab.get('title')=='精选':# 20211228 主页变为了精选 2302833636843074
                        containerid = tab.get('containerid')
                        break
            except:
                containerid=None
            # if tabsInfo==None:
            #     containerid=None
            # else:
            #     tabs=tabsInfo.get('tabs')#tabs0-3对应微博用户主页的4个标签，地址在第一页
            #     for tab in tabs:
            #         if tab.get('title')=='精选':# 20211228 主页变为了精选 2302833636843074
            #             containerid=tab.get('containerid')
            #             break
            if containerid==None:
                print('****获取主页(精选)containerid失败,response:    ',response.json())
                print(response.json().get('data'))
                print('****url:       ',url)
                print('****containerid为None')
            return containerid
    except requests.ConnectionError as e:
        print('Error', e.args)

def main(keyword, path='article.csv'):
    title = keyword
    path = path
    if os.path.exists(path):
        print('删除:', path)
        os.remove(path)
    item_list = ['id', 'uid', 'text', 'label', 'location' ,'created_at' , 'isLongText', 'longText']
    s = SaveCSV()
    for page in range(1, 10):  # 循环页面
        try:
            time.sleep(delay)  # 设置睡眠时间，防止被封号
            json = get_page(page, title)
            results = parse_page(json, title)
            if requests == None:
                continue
            for result in results:
                if result == None:
                    continue
                s.save(item_list, path, result)
        except TypeError as e:
            print("格式错误，跳过当前页")
            print(e)
            continue


    cities=[]
    with open(path) as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            print(row)
            print(row[3].split(' ')[0])
            cities.append(row[3].split(' ')[0])
    cityName=set(cities)
    cityDict={}
    for city in cityName:
        cityDict[city]=0
    for city in cities:
        cityDict[city]+=1


    return cityDict

if __name__ == '__main__':
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['spider_weibo']
    collist = mydb.list_collection_names()
    mycol = mydb['spider_weibo']#'id,text,label,location,created_at'



    title = input("请输入搜索关键词：")
    path = "article.csv"
    item_list = ['id', 'uid','text', 'label','location', 'created_at' , 'isLongText', 'longText']
    s = SaveCSV()
    for page in range(0,200):#循环页面
        try:
            time.sleep(delay)         #设置睡眠时间，防止被封号
            json = get_page(page , title )
            results = parse_page(json , title)
            if requests == None:
                continue
            for result in results:
                if result == None:
                    continue
                s.save(item_list, path , result)

                if result['id'] not in mycol.distinct('id'):#去重
                    print('write:\n')
                    print(result['id'])
                    mycol.insert_one(result)

        except TypeError as e:
            print("格式错误，跳过当前页")
            print(e)
            continue
