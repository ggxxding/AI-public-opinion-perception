from urllib.parse import urlencode
import requests
import logging
from logging import handlers
from pyquery import PyQuery as pq
import time
import os
import csv
import json
import pymongo
import re
from lxml import etree
import argparse
import datetime
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from apscheduler.schedulers.blocking import BlockingScheduler
from senta import Senta
import cluster
import wordCloud
import jieba
from collections import Counter


#人工智能: 11-20-16 face:01-15-17
parser = argparse.ArgumentParser(description='description')
parser.add_argument('-k','--keyword', type=str, default='人工智能',help='searching keyword')
parser.add_argument('-s','--start', type=str, default='2022-05-23-00',help='start time, format: yyyy-mm-dd-h(2021-01-01-0)')
parser.add_argument('-e','--end', type=str, default='2022-06-29-00',help='end time, format: yyyy-mm-dd-h(2021-12-31-23)')
parser.add_argument('-u','--username', type=str, default='ggxxding',help='weibo username')
args = parser.parse_args()

username = args.username

my_senta = Senta()
use_cuda = True
my_senta.init_model(model_class="ernie_1.0_skep_large_ch", task="sentiment_classify", use_cuda=use_cuda)

myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
mydb = myclient['spider_weibo']
collist = mydb.list_collection_names()
mycol = mydb['selenium_weibo']
uid_loc_dict={}
for i in mycol.find({},{'uid':1,'location':1}):
    uid_loc_dict[str(i['uid'])]=i['location']

delay=1/0.3 #0.3次请求/秒
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    'Cookie':'SUB=_2A25PvgmmDeRhGeVK4lEU9SnOwj-IHXVsynxurDV8PUNbmtAKLRb6kW9NTCtROWxw7Ir_LTkPT5yZGn7AssSLDu7P',
    }

class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=3,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)
log = Logger('selenium_log.log', level='debug')
base_url='https://s.weibo.com/weibo?'

def get_latest_time(label):
    #2022/04/01 01:31
    max = datetime.datetime(1,1,1,1,1,1)
    for i in mycol.find({'label':label},{'created_at':1}):
        current = datetime.datetime.strptime( i['created_at'],'%Y/%m/%d %H:%M')
        if current>max:
            max = current
    return max

def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    chrome = webdriver.Chrome(options=options)
    chrome.set_window_size(1920,1080)
    return chrome

def login_weibo(chrome):
    chrome.get('https://weibo.com/login.php')
    time.sleep(10)
    button = chrome.find_elements_by_xpath('//a[@action-data="type=qrcode"]')[0]
    button.click()
    time.sleep(3)
    chrome.save_screenshot('screenshots/screenshot.png')
    input('从/home/sstl/dmj/AI-public-opinion-perception/backend/screenshots/screenshot.png 获取二维码截屏,扫码登陆账户后按回车:')
    chrome.refresh()

def get_cookies(chrome):
    Cookies = chrome.get_cookies()
    jsCookies = json.dumps(Cookies)
    with open('cookies.txt','w') as f:
        f.write(jsCookies)
    print('Cookies写入.')

def read_cookies():
    with open('cookies.txt','r',encoding='utf8') as f:
        Cookies = json.loads(f.read())
    cookies = []
    for cookie in Cookies:
        cookie_dict = {
            'domain': '.weibo.com',
            'name' : cookie.get('name'),
            'value': cookie.get('value'),
            'expires': '',
            'path': '/',
            'httpOnly': False,
            'HostOnly': False,
            'Secure': False
        }
        cookies.append(cookie_dict)
    return cookies


def check_cookies(username):
    print('Checking cookie:')
    cookies = read_cookies()
    sub = ''
    for i in cookies:
        if i['name'] == 'SUB':
            sub = i['value']
    headers['Cookie'] = 'SUB=' + sub
    res = requests.get('https://weibo.com',headers=headers)
    if username in res.text:
        return True
    else:
        return False

def update_cookies(username):# 刷新-获取cookie-检测-失败则重新登陆
    if not check_cookies(username):
        print('cookie失效,刷新页面')
        chrome.refresh()
        time.sleep(10)
        get_cookies(chrome)
    else:
        print('Cookie有效,无需更新')
        return 1
    if not check_cookies(username):
        succ = 0
        input('仍然失效,按回车后等待提示获取二维码扫码登录')
        while succ == 0 :
            login_weibo(chrome)
            chrome.refresh()
            time.sleep(10)
            get_cookies(chrome)
            Cookies = read_cookies()
            sub = None
            for i in Cookies:
                if i['name'] == 'SUB':
                    sub = i['value']
            if sub == None:
                print('获取失败，请等待刷新后重试')
                succ = 0
            else:
                headers['Cookie'] = 'SUB=' + sub
                print('cookie已更新')
                succ = 1
        return 1
    else:
        Cookies = read_cookies()
        for i in Cookies:
            if i['name'] == 'SUB':
                sub = i['value']
        headers['Cookie'] = 'SUB=' + sub
        print('刷新后Cookie有效,已更新。')
        return 1

def predict_text( text ):
    result = my_senta.predict(text)[0][1]
    return result

def get_containerid(uid):
    '''输入用户uid，输出主页包含位置信息的containerid
    部分请求返回{"ok":0,"msg":"这里还没有内容","data":{"cards":[]}}，原因可能是没有登陆，待解决
    '''
    'https://m.weibo.cn/api/container/getIndex?type=uid&value=6248471088'
    pre='https://m.weibo.cn/api/container/getIndex?'
    params = {
        'type':'uid',
        'value': uid,
    }
    url = pre + urlencode(params)
    print('从uid获取containerid的url:',url)
    try:
        time.sleep(delay)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tabsInfo=response.json().get('data').get('tabsInfo')
            containerid=None
            try:
                tabs=tabsInfo.get('tabs')#tabs0-3对应微博用户主页的4个标签，地址在第一页
                for tab in tabs:
                    if tab.get('title')=='精选':# 20211228 主页变为了精选 2302833636843074
                        containerid = tab.get('containerid')
                        break
            except:
                containerid=None
                err_info = '报错,获取containerid失败,uid: ' + str(uid)
                log.logger.error(err_info)
            return containerid
    except requests.ConnectionError as e:
        err_info = '报错,获取container连接失败,uid: ' + str(uid)
        log.logger.error(err_info)
        print('Error:', e.args)
        return None
def get_location(uid):

    'https://m.weibo.cn/api/container/getIndex?type=uid&value=6248471088&containerid=2302836248471088'
    pre='https://m.weibo.cn/api/container/getIndex?'
    containerid = get_containerid(uid)
    if containerid==None:
        print('*****containerid为空')
        return '未知'
    params = {
        'type':'uid',
        'value': uid,
        'containerid': containerid,
    }
    url = pre + urlencode(params)
    try:
        time.sleep(delay)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
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
                err_info = 'location未知, uid: '+ str(uid)
                log.logger.error(err_info)
                pass
            return location
    except requests.ConnectionError as e:
        print('ConnectionError', e.args)

def get_location_from_page(uid):
    time.sleep(1)
    'https://weibo.com/u/3473570382'
    print('get location:')
    location = uid_loc_dict.get(str(uid))
    if location:
        return location

    base = 'https://weibo.com/'
    url = base+uid
    location='未知'
    chrome.get(url)
    try:
        wait.until(lambda driver: chrome.find_element_by_xpath('//i[@class="woo-font woo-font--angleDown"]'))
    except:
        print('未找到下拉箭头,跳过')

    angleDown = chrome.find_elements_by_xpath('//i[@class="woo-font woo-font--angleDown"]')
    if angleDown:
        angleDown[0].click()
    #IP属地
    IP_i = chrome.find_elements_by_xpath('//i[@class="woo-font woo-font--ip"]')
    if IP_i:
        location = IP_i[0].find_elements_by_xpath('../..')[0].text.strip().split('：')[1]

    proPlace_i = chrome.find_elements_by_xpath('//i[@class="woo-font woo-font--proPlace"]')
    if proPlace_i:
        location = proPlace_i[0].find_elements_by_xpath('../..')[0].text.strip()
    return location


    #
    # page_text = requests.get(url, headers=headers)
    # if page_text.history:
    #     redirect_location = page_text.history[0].headers['location']
    #     print('重定向:',redirect_location)
    #     url = base[:-1] + redirect_location
    #     page_text = requests.get(url, headers=headers).text
    #     tree = etree.HTML(page_text)
    #     scrs = tree.xpath('//script/text()')
    #     for scr in scrs:
    #         if 'IP属地' in scr:
    #             # print(scr)
    #             searchObj = re.search(r'(.*)IP属地：([\u4e00-\u9fa5]+)(.*)', scr, re.M|re.I)
    #             if not searchObj:
    #                 return '未知'
    #             print('位置：',searchObj.group(2))
    #             return searchObj.group(2)
    #     return '未知'
    # else:
    #     return '未知'



def search(keyword, start, end):
    # start = '2021-01-01'
    # end   = '2021-12-30'
    log.logger.info('Begin searching from: %s to %s'%(start,end))
    one_hour = datetime.timedelta(hours=1)
    one_day  = datetime.timedelta(days=1)
    start_time = datetime.datetime.strptime(start, '%Y-%m-%d-%H')
    end_time = datetime.datetime.strptime(end, '%Y-%m-%d-%H')
    temp_time = start_time
    while((end_time-temp_time-one_hour).days>-1):
        timescope = temp_time.strftime('%Y-%m-%d-%H')+':'+(temp_time+one_hour).strftime('%Y-%m-%d-%H')
        # timescope = temp_time.strftime('%Y-%m-%d-%H') + ':' + (temp_time + one_day).strftime('%Y-%m-%d-%H')
        params = {
            'q': keyword,
            'typeall': 1,
            'suball': 1,
            'timescope': 'custom:'+timescope,
            'Refer': 'SWeibo_box',
            'page': 1,
        }
        url = base_url + urlencode(params)
        page_text = requests.get(
            url=url,
            headers=headers).text
        tree = etree.HTML(page_text)
        page_num = max(len(tree.xpath('//ul[@class="s-scroll"]/li')),1)
        #总页数
        log.logger.info('%s 的总页数: %s'%(timescope, str(page_num)))
        time.sleep(1)

        for page in range(page_num):
            parse_page(timescope = timescope,page = page,keyword = keyword)

        temp_time = temp_time+ one_hour
        # temp_time = temp_time + one_day

def parse_page(timescope, page, keyword):
    print(timescope, page, keyword)
    params = {
        'q': keyword,
        'typeall': 1,
        'suball': 1,
        'timescope': 'custom:' + timescope,
        'Refer': 'SWeibo_box',
        'page': page + 1,
    }
    log.logger.info('解析第%s页' % (str(page + 1)))
    url = base_url + urlencode(params)

    page_text = requests.get(
        url=url,
        headers=headers).text
    tree = etree.HTML(page_text)
    now = datetime.datetime.now()
    # 处理文
    cards = tree.xpath('//*[@id="pl_feedlist_index"]/div[2]//div[@class="card-feed"]')#所有微博卡片 返回列表
    for card in cards:
        wb1 = {'label': keyword, 'text': '', 'longText': ''}
        wb2 = {'label': keyword, 'text': '', 'longText': ''}
        card_info = card.xpath('./div[@class="content"]/div[@class="info"]')
        if card_info:
            # 找名字
            name = card_info[0].xpath('.//a[@class="name"]')
            if name:
                wb1['name'] = name[0].text
                name_href1 = name[0].attrib['href']

                uid1 = re.sub(r'(.*)weibo.com(\D*)(\d+)(\D*)(.*)', r'\3', name_href1)
                wb1['uid'] = uid1

                # wb1['location'] = get_location_from_page(wb1['uid'])

        # card_content = card.find_elements_by_xpath('./div[@class="content"]/p[@node-type="feed_list_content"]')
        card_content = card.xpath('./div[@class="content"]/p[@node-type="feed_list_content"]//text()')
        card_content = ' '.join(card_content).strip()
        if card_content:
            wb1['text'] = re.sub(r'(.*)(L.*的微博视频)', r'\1', card_content.split('//')[0].replace('\n', '').strip())
            print(wb1['text'])
            wb1['isLongText'] = False
        # card_time = card.find_elements_by_xpath('./div[@class="content"]/p[@class="from"]/a[@target="_blank"]')
        card_time = card.xpath('./div[@class="content"]/*[@class="from"]/a[@target="_blank"]')
        if card_time:
            if '年' in card_time[0].text:
                wb1['created_at'] = re.sub(r'(.*)年(.*)月(.*)日 (.*)', r'\1/\2/\3 \4', card_time[0].text.strip())
            elif '今天' in card_time[0].text:
                wb1['created_at'] = datetime.datetime.now().strftime('%Y/%m/%d') + ' ' + re.sub(r'今天(.*)',
                                                                                          r'\1',
                                                                                          card_time[0].text.strip())
            elif '分钟前' in card_time[0].text:
                wb1['created_at'] = (now - datetime.timedelta(
                    minutes=int(re.sub('分钟前', '', card_time[0].text.strip())))).strftime('%Y/%m/%d %H:%M')

                print(card_time[0].text)
                print(wb1['created_at'])
            else:
                wb1['created_at'] = datetime.datetime.now().strftime('%Y') + '/' + re.sub(r'(.*)月(.*)日 (.*)',
                                                                                          r'\1/\2 \3',
                                                                                          card_time[0].text.strip())
                print(wb1['created_at'])

        # 找被转发的微博
        # card_comment = card.find_elements_by_xpath('./div[@class="content"]/div[@class="card-comment"]')
        card_comment = card.xpath('./div[@class="content"]/div[@class="card-comment"]')
        if card_comment:
            name = card_comment[0].xpath('.//a[@class="name"]')
            if name:
                wb2['name'] = name[0].text[1:]
                name_href2 = name[0].attrib['href']
                uid2 = re.sub(r'(.*)weibo.com(\D*)(\d+)(\D*)(.*)', r'\3', name_href2)
                wb2['uid'] = uid2
                # wb2['location'] = get_location_from_page(uid2)
                # card_comment_content = name[0].find_elements_by_xpath('../p[@node-type="feed_list_content"]')
                card_comment_content = name[0].xpath('../p[@node-type="feed_list_content"]//text()')
                card_comment_content = ' '.join(card_comment_content).strip()
                if card_comment_content:
                    wb2['text'] = re.sub(r'(.*)(L.*的微博视频)', r'\1', card_comment_content.replace('\n', '').strip())
                    wb2['isLongText'] = False
                comment_time = card_comment[0].xpath('.//p[@class="from"]/a[@target="_blank"]')
                if comment_time:
                    if '年' in comment_time[0].text:
                        wb2['created_at'] = re.sub(r'(.*)年(.*)月(.*)日 (.*)', r'\1/\2/\3 \4', comment_time[0].text.strip())
                    elif '今天' in comment_time[0].text:
                        wb2['created_at'] = datetime.datetime.now().strftime('%Y/%m/%d') + ' ' + re.sub(r'今天(.*)',
                                                                                                        r'\1',
                                                                                                        comment_time[0].text.strip())
                    elif '分钟前' in comment_time[0].text:
                        wb2['created_at'] = (now - datetime.timedelta(minutes = int( re.sub('分钟前','',comment_time[0].text.strip()) ))).strftime('%Y/%m/%d %H:%M')
                        print(comment_time[0].text)
                        print(wb2['created_at'])
                    else:
                        wb2['created_at'] = datetime.datetime.now().strftime('%Y') + '/' + re.sub(r'(.*)月(.*)日 (.*)',
                                                                                                  r'\1/\2 \3',
                                                                                                  comment_time[0].text.strip())
            else:
                pass
        print('----')
        # mycol.update_one({'label': '人工智能1', 'text': '阿萨阿斯顿阿斯顿地方'},
        #                  {'$setOnInsert': {'text3': 'text31'},
        #                   '$set': {'text4': 'text42'}},
        #                  upsert=True)
        if wb1['text'] != '' and keyword in wb1['text']:
            wb1['location'] = get_location_from_page(wb1['uid'])
            wb1['sentiment'] = predict_text(wb1['text'])
            upserted = mycol.update_one({'label':keyword,'text':wb1['text']},
                             {'$setOnInsert':wb1},
                             upsert=True
            )
            if upserted.raw_result['updatedExisting'] == False:
                print('insert')
        elif wb1['longText'] != '' and keyword in wb1['longText']:
            wb1['location'] = get_location_from_page(wb1['uid'])
            wb1['sentiment'] = predict_text(wb1['longText'])
            upserted =  mycol.update_one({'label': keyword, 'longText': wb1['longText']},
                             {'$setOnInsert': wb1},
                             upsert=True
                             )
            if upserted.raw_result['updatedExisting'] == False:
                print('insert')
        if wb2['text'] != '' and keyword in wb2['text']  :
            wb2['location'] = get_location_from_page(wb2['uid'])
            wb2['sentiment'] = predict_text(wb2['text'])
            upserted = mycol.update_one({'label': keyword, 'text': wb2['text']},
                             {'$setOnInsert': wb2},
                             upsert=True
                             )
            if upserted.raw_result['updatedExisting'] == False:
                print('insert')
        elif wb2['longText'] != '' and keyword in wb2['longText']:
            wb2['location'] = get_location_from_page(wb2['uid'])
            wb2['sentiment'] = predict_text(wb2['longText'])
            upserted = mycol.update_one({'label': keyword, 'longText': wb2['longText']},
                             {'$setOnInsert': wb2},
                             upsert=True
                             )
            if upserted.raw_result['updatedExisting'] == False:
                print('insert')

#data processing
stopwords=['人脸','识别',' ']
with open('res/stopwords1893.csv','r') as f:
    for line in f.readlines():
        stopwords.append(line.strip().strip('\n'))
china_city=['新疆','西藏','青海','甘肃','内蒙古','河北','山西','辽宁','吉林','黑龙江','江苏','浙江','安徽',
		   '福建','江西','山东','河南','湖北','湖南','广东','海南','四川','贵州','云南','陕西','甘肃','台湾','广西',
		   '宁夏','北京','天津','上海','重庆','香港','澳门']
def loadWeiboData():
    countDict={}
    timeDict={}
    cityDict={}
    timeList={}
    cityList={}
    textDict={}
    texts_from_now={}
    wordCloudList={}
    word_cloud={}
    word_cloud_stream={}
    cluster_result={}
    sentiment_result = {}
    barData={'data':{},'cities':{}}
    for label in mycol.distinct('label'):
        countDict [label] = {'24h':0,'30d':0,'90d':0,'365d':0}
        timeDict [label] = {}
        cityDict [label] = 		{'24h':{},'30d':{},'90d':{},'365d':{},}
        barData['data'][label] = {'24h':[],'30d':[],'90d':[],'365d':[],}
        barData['cities'][label] = {'24h':[],'30d':[],'90d':[],'365d':[],}
        textDict[label] =  {'2022':[],'2021':[],'2020':[],'earlier':[],}
        wordCloudList [label] = {'2022':[],'2021':[],'2020':[],'earlier':[],}
        texts_from_now[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
        word_cloud[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
        word_cloud_stream[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
        cluster_result[label] = {'24h':[],'30d':[], '90d':[], '365d':[]}
        sentiment_result[label] = {'24h':[{'name':'pos','value':0},{'name':'neg','value':0}],
                                   '30d':[{'name':'pos','value':0},{'name':'neg','value':0}],
                                   '90d':[{'name':'pos','value':0},{'name':'neg','value':0}],
                                   '365d':[{'name':'pos','value':0},{'name':'neg','value':0}]}
        for i in  mycol.distinct('location'):
            if len(i.split(' ')[0])<5 and i.split(' ')[0] in china_city:
                cityDict[label]['24h'][i.split(' ')[0]] = 0
                cityDict[label]['30d'][i.split(' ')[0]] = 0
                cityDict[label]['90d'][i.split(' ')[0]] = 0
                cityDict[label]['365d'][i.split(' ')[0]] = 0
        temp = {
                    '2022': [0 for i in range(12)],
                    '2021': [0 for i in range(12)],
                    '2020': [0 for i in range(12)],
                    'earlier': [0 for i in range(12)],
                }
        timeList[label] = temp
        cityList[label] = {'24h': [], '30d': [], '90d': [], '365d': []}
    now = datetime.datetime.now()
    # now = datetime.datetime(2022,4,13,0,0,0)
    for weiboData in mycol.find({},{'label':1,'created_at':1,'location':1,'isLongText':1,'text':1,'longText':1,'sentiment':1}):
        location = weiboData['location'].split(' ')[0]
        weiboData_time = datetime.datetime.strptime(weiboData['created_at'], '%Y/%m/%d %H:%M')
        time_from_now = now - weiboData_time

        if time_from_now.days >= 0 :
            if time_from_now.days == 0:
                countDict[weiboData['label']]['24h'] += 1
                if location in cityDict[weiboData['label']]['24h'].keys():
                    cityDict[weiboData['label']]['24h'][location] += 1
                if weiboData['isLongText'] == False:
                    texts_from_now[weiboData['label']]['24h'].append(weiboData['text'])
                    if weiboData['sentiment'] == 'positive':
                        sentiment_result[weiboData['label']]['24h'][0]['value'] += 1
                    else:
                        sentiment_result[weiboData['label']]['24h'][1]['value'] += 1
            if time_from_now.days <= 29:
                countDict[weiboData['label']]['30d'] += 1
                if location in cityDict[weiboData['label']]['30d'].keys():
                    cityDict[weiboData['label']]['30d'][location] += 1
                if weiboData['isLongText']==False:
                    texts_from_now[weiboData['label']]['30d'].append(weiboData['text'])
                    # print(weiboData['text'])
                    if weiboData['sentiment'] == 'positive':
                        sentiment_result[weiboData['label']]['30d'][0]['value'] += 1
                    else:
                        sentiment_result[weiboData['label']]['30d'][1]['value'] += 1


            if time_from_now.days <= 89:
                countDict[weiboData['label']]['90d'] += 1
                if location in cityDict[weiboData['label']]['90d'].keys():
                    cityDict[weiboData['label']]['90d'][location] += 1
                if weiboData['sentiment'] == 'positive':
                    sentiment_result[weiboData['label']]['90d'][0]['value'] += 1
                else:
                    sentiment_result[weiboData['label']]['90d'][1]['value'] += 1
            if time_from_now.days <= 364:
                countDict[weiboData['label']]['365d'] += 1
                if location in cityDict[weiboData['label']]['365d'].keys():
                    cityDict[weiboData['label']]['365d'][location] += 1
                if weiboData['sentiment'] == 'positive':
                    sentiment_result[weiboData['label']]['365d'][0]['value'] += 1
                else:
                    sentiment_result[weiboData['label']]['365d'][1]['value'] += 1
        if weiboData['created_at'][:4] not in ['2022','2021','2020']:
            if weiboData['isLongText']==True:
                textDict[weiboData['label']]['earlier'].append(weiboData['longText'])
            else:
                textDict[weiboData['label']]['earlier'].append(weiboData['text'])
        else:
            if weiboData['isLongText']==True:
                textDict[weiboData['label']][weiboData['created_at'][:4]].append(weiboData['longText'])
            else:
                textDict[weiboData['label']][weiboData['created_at'][:4]].append(weiboData['text'])
        year_month = weiboData['created_at'][:7]
        if year_month not in timeDict[weiboData['label']].keys():
            timeDict[weiboData['label']][year_month] = 1
        else:
            timeDict[weiboData['label']][year_month] += 1


    #聚类 词频
    for keyword in texts_from_now:
        cluster_result[keyword]['24h'] = cluster.main(texts_from_now[keyword]['24h'])
        if texts_from_now[keyword]['24h']!= []:
            word_cloud_stream[keyword]['24h'] = wordCloud.draw(texts_from_now[keyword]['24h'], keyword)
        else:
            word_cloud_stream[keyword]['24h'] = wordCloud.draw(['empty input'], keyword)
    for keyword in cluster_result:
        for key in cluster_result[keyword]:
            temp_result = {'nodes':[],'links':[],'categories':[]}
            count = Counter([x[0] for x in cluster_result[keyword][key]])#未排序
            for num in [x[0] for x in count.most_common(5)]:
                temp_result['categories'].append({'name': str(num)})
                num_texts = [x[1] for x in  cluster_result[keyword][key] if x[0]==num]
                word_count=Counter()
                for text in num_texts:
                    cut_list = [x for x in jieba.lcut(text) if x not in stopwords]
                    word_count = word_count + Counter(cut_list)
                append_word_count = 0
                for word in [x[0] for x in word_count.most_common(5)]:
                    temp_result['nodes'].append({'id':word+'['+str(num)+']','name':word+'['+str(num)+']','value':word_count[word],'category':str(num)})
                    for node in temp_result['nodes']:
                        if node['category'] == str(num) and node['id']!= word+'['+str(num)+']':
                            temp_result['links'].append({'source':word+'['+str(num)+']','target':node['id']})
                    append_word_count += 1
                    if append_word_count >=10:
                        break
                if len(temp_result['categories']) >=5:
                    break
            cluster_result[keyword][key] = temp_result


    for keyword in timeDict:
        for key in timeDict[keyword]:
            date_key = datetime.datetime.strptime(key, '%Y/%m')
            if date_key.year not in [2022,2021,2020]:
                timeList[keyword]['earlier'][date_key.month-1]=timeDict[keyword][key]
            else:
                timeList[keyword][str(date_key.year)][date_key.month-1]=timeDict[keyword][key]

    for keyword in cityDict:
        for key in cityDict[keyword]:
            cityList[keyword][key]=[{'name':str(x),'value':cityDict[keyword][key][x],'title':str(x)} for x in cityDict[keyword][key]]
            ordered = sorted(cityDict[keyword][key].items(),key=lambda x:x[1],reverse=True)
            cityList[keyword][key].append({'name': 'max', 'value': ordered[0][1], 'title': 'max'})
            cityList[keyword][key].append({'name': 'min', 'value': ordered[-1][1], 'title': 'min'})

            avg = (ordered[-5][1]+ordered[4][1])/2
            barData['data'][keyword][key] = [ordered[0][1],ordered[1][1],ordered[2][1],ordered[3][1],ordered[4][1],
                                             avg,avg,avg,
                                             ordered[-5][1],ordered[-4][1],ordered[-3][1],ordered[-2][1],ordered[-1][1]]
            barData['cities'][keyword][key] = [ordered[0][0],ordered[1][0],ordered[2][0],ordered[3][0],ordered[4][0],
                                             '','……','',
                                             ordered[-5][0],ordered[-4][0],ordered[-3][0],ordered[-2][0],ordered[-1][0]]
    wordCloudList={}
    # return jsonify({'cityList':cityList, 'timeList':timeList, 'barData':barData, 'wordCloudList':wordCloudList,
	# 				'countDict':countDict , 'wordCloudStream':word_cloud_stream ,'clusterResult':cluster_result,
	# 				'sentiment_result':sentiment_result})
    res = {'cityList':cityList, 'timeList':timeList, 'barData':barData, 'wordCloudList':wordCloudList,'countDict':countDict , 'wordCloudStream':word_cloud_stream ,'clusterResult':cluster_result,'sentiment_result':sentiment_result}
    with open('./res/temp_result.txt','w') as f:
        f.write(json.dumps(res))
    os.rename('./res/temp_result.txt', './res/data.txt')
    return 0
def job():
    end = datetime.datetime.now().strftime('%Y-%m-%d-%H')
    one_hour = datetime.timedelta(hours=1)
    start = datetime.datetime.strptime(end, '%Y-%m-%d-%H')-one_hour
    # start = start.strftime('%Y-%m-%d-%H')
    print('开始定时任务',datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    chrome.refresh()
    time.sleep(10)
    chrome.save_screenshot('screenshots/screenshot_temp.png')

    while(chrome.get_cookie('SUB') == None):
        chrome.refresh()
        time.sleep(10)
        print('获取cookie失败,chrome重新刷新!')

    print('获取cookie!')
    get_cookies(chrome)
    print('检查cookie:',check_cookies(username))

    Cookies = read_cookies()
    for i in Cookies:
        if i['name'] == 'SUB':
            sub = i['value']

    update_cookies(username)

    # if not check_cookies(username):
    #     print('cookie失效')
    #     new_sub = input('请将'+ username +'的有效Cookie的SUB value黏贴后按回车：')# 待修改
    #     headers['Cookie']='SUB=' + new_sub
    # else:
    #     print('cookie有效,直接读取')
    #     headers['Cookie']='SUB=' + sub

    for keyword in ['人工智能','人脸识别','随申码','智慧医疗']:
        latest_time = get_latest_time(keyword)
        if latest_time < start:
            latest_time = latest_time.strftime('%Y-%m-%d-%H')
            search(keyword,latest_time,end) #cookies
        else:
            latest_time = start.strftime('%Y-%m-%d-%H')
            search(keyword, latest_time,end)
    loadWeiboData()
    print('定时任务结束')


if __name__ == '__main__':

    global chrome
    chrome = init_browser()
    global wait
    wait = ui.WebDriverWait(chrome, 5)
    login_weibo(chrome)
    time.sleep(2)
    get_cookies(chrome)
    print(check_cookies(username))
    Cookies = read_cookies()

    for i in Cookies:
        if i['name'] == 'SUB':
            sub = i['value']
    headers['Cookie']='SUB=' + sub

    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'cron', hour='*',minute=30)
    scheduler.start()



    # for keyword in ['人工智能','人脸识别','随申码','智慧医疗']:
    #     search(keyword,args.start,args.end) #cookies