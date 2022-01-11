import logging
from logging import handlers
import argparse
import datetime

# import pymongo
import requests
from selenium import webdriver
import time
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from random import choice
import re
from urllib.parse import urlencode
import csv

parser = argparse.ArgumentParser(description='description')
parser.add_argument('-k','--keyword', type=str, default='人脸识别',help='searching keyword')
#2021-09-26-21  2021-09-29-13
parser.add_argument('-s','--start', type=str, default='2021-01-01-00',help='start time, format: yyyy-mm-dd-h(2021-01-01-0)')
parser.add_argument('-e','--end', type=str, default='2022-01-01-0',help='end time, format: yyyy-mm-dd-h(2021-12-31-23)')
args = parser.parse_args()

# myclient = pymongo.MongoClient('mongodb://192.168.71.214:27017/')
# mydb = myclient['spider_weibo']
# collist = mydb.list_collection_names()
# mycol = mydb['selenium_weibo']
uid_loc_dict={}




delay=1/0.3 #0.3次请求/秒
driver = webdriver.Chrome()
driver.maximize_window()
driver_window1 = driver.current_window_handle
driver.execute_script('window.open("https://www.baidu.com/")')
driver_window2 = driver.window_handles[1]
driver.switch_to.window(driver_window1)
wait = ui.WebDriverWait(driver, 5)  # 设定最长等待加载时间为10秒
base_url='https://s.weibo.com/weibo?'
headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/3493557293',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
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
# log.logger.debug('debug')
# log.logger.info('info')
# log.logger.warning('警告')
# log.logger.error('报错')
# log.logger.critical('严重')
# Logger('error.log', level='error').logger.error('error')

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
    location = uid_loc_dict.get(str(uid))
    if location:
        return location
    driver.switch_to.window(driver_window2)
    url='https://weibo.com/'+str(uid)
    location="未知"
    for i in range(5):
        try:
            driver.get(url)
            wait.until(lambda driver: driver.find_element_by_class_name("more_txt"))
            break
        except:
            time.sleep(3)
            log.logger.info('等待3s,刷新url: %s' % (url))
            pass
    ficon_cd_place = driver.find_elements_by_class_name('ficon_cd_place')
    if ficon_cd_place:
        location = ficon_cd_place[0].find_element_by_xpath('../..').text.replace('2','').replace('\n','')
    driver.switch_to.window(driver_window1)
    uid_loc_dict[str(uid)] = location
    return location

def login():
    driver.get('https://weibo.com/login.php')
    wait.until(lambda driver: driver.find_element_by_xpath("//span[@node-type='submitStates']"))
    # driver.find_element_by_id('loginname').send_keys('1')
    # driver.find_element_by_name('password').send_keys('2')
    # driver.find_element_by_class_name('W_btn_a').click()
    input('手动登陆账户后按回车:')
    print('确认登录，准备开始搜索')


def search(keyword, start, end):
    # start = '2021-01-01'
    # end   = '2021-12-30'
    log.logger.info('Begin searching from: %s to %s'%(start,end))
    one_hour = datetime.timedelta(hours=1)
    start_time = datetime.datetime.strptime(start, '%Y-%m-%d-%H')
    end_time = datetime.datetime.strptime(end, '%Y-%m-%d-%H')
    temp_time = start_time
    while((end_time-temp_time-one_hour).days>-1):
        timescope = temp_time.strftime('%Y-%m-%d-%H')+':'+(temp_time+one_hour).strftime('%Y-%m-%d-%H')
        params = {
            'q': keyword,
            'typeall': 1,
            'suball': 1,
            'timescope': 'custom:'+timescope,
            'Refer': 'SWeibo_box',
            'page': 1,
        }
        url = base_url + urlencode(params)

        for i in range(10):
            try:
                driver.get(url)
                wait.until(lambda driver: driver.find_element_by_xpath("//div[@id='weibo_top_public']"))
                break
            except:
                time.sleep(3)
                log.logger.info('等待3s,刷新url: %s'%(url))
                pass
        #等待页面加载完成，一开始设想查找“下一页”按钮，但是如果只有一页内容，会找不到，所以目前的策略是等待顶部导航条加载完成
        wait.until(lambda driver: driver.find_element_by_xpath("//div[@id='weibo_top_public']"))
        #总页数
        page_num = max(len(driver.find_elements_by_xpath('//ul[@class="s-scroll"]/li')),1)
        log.logger.info('%s 的总页数: %s'%(timescope, str(page_num)))
        time.sleep(1)
        # card-feed
        #     content
        #         div class="info"
        #                 class="name"
        #         p[node-type="feed_list_content"]
        #             a[action-type="fl_unfold"]#展开全文
        #         p[node-type="feed_list_content_full"]
        #         div class="card-comment"
        #             a class="name"
        #             p node-type="feed_list_content"
        #                a[action - type = "fl_unfold"]  # 展开全文
        #             p node-type="feed_list_content_full"
        for page in range(page_num):#[0,49]
            parse_page(timescope = timescope,page = page,keyword = keyword)

        temp_time = temp_time+ one_hour
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
    for i in range(10):
        try:
            driver.get(url)
            wait.until(lambda driver: driver.find_element_by_xpath("//div[@id='weibo_top_public']"))
            break
        except:
            time.sleep(3)
            log.logger.info('等待3s,刷新url: %s' % (url))
            pass

    # 处理文本
    cards = driver.find_elements_by_class_name('card-feed')
    for card in cards:
        wb1 = {'label': keyword, 'text': '', 'longText': ''}
        wb2 = {'label': keyword, 'text': '', 'longText': ''}
        card_info = card.find_elements_by_xpath('./div[@class="content"]/div[@class="info"]')
        if card_info:
            # 找名字
            name = card_info[0].find_elements_by_class_name('name')
            if name:
                wb1['name'] = name[0].text
                name_href = name[0].get_attribute('href')
                uid1 = re.sub(r'(.*)weibo.com(\D*)(\d+)(\D*)(.*)', r'\3', name_href)
                wb1['uid'] = uid1
                # wb1['location'] = get_location_from_page(wb1['uid'])

        card_content = card.find_elements_by_xpath('./div[@class="content"]/p[@node-type="feed_list_content"]')
        if card_content:
            #  微博内容
            # 展开全文按钮
            unfold_button = card_content[0].find_elements_by_xpath('.//a[@action-type="fl_unfold"]')
            if unfold_button:
                unfold_button[0].click()
                content_full = card_content[0].find_elements_by_xpath('../p[@node-type="feed_list_content_full"]')[
                    0].text.replace('\n', '').replace('收起全文d', '')
                wb1['longText'] = re.sub(r'(.*)(L.*的微博视频)', r'\1', content_full)
                wb1['isLongText'] = True
            else:
                wb1['text'] = re.sub(r'(.*)(L.*的微博视频)', r'\1', card_content[0].text.split('//')[0].replace('\n', ''))
                wb1['isLongText'] = False
        card_time = card.find_elements_by_xpath('./div[@class="content"]/p[@class="from"]/a[@target="_blank"]')
        if card_time:
            if '年' in card_time[0].text:
                wb1['created_at'] = re.sub(r'(.*)年(.*)月(.*)日 (.*)', r'\1/\2/\3 \4', card_time[0].text)
            else:
                wb1['created_at'] = datetime.datetime.now().strftime('%Y') + '/' + re.sub(r'(.*)月(.*)日 (.*)',
                                                                                          r'\1/\2 \3',
                                                                                          card_time[0].text)

        # 找被转发的微博
        card_comment = card.find_elements_by_xpath('./div[@class="content"]/div[@class="card-comment"]')
        if card_comment:
            name = card_comment[0].find_elements_by_class_name('name')
            if name:
                wb2['name'] = name[0].text[1:]
                name_href = name[0].get_attribute('href')
                uid2 = re.sub(r'(.*)weibo.com(\D*)(\d+)(\D*)(.*)', r'\3', name_href)
                wb2['uid'] = uid2
                # wb2['location'] = get_location_from_page(uid2)

                card_comment_content = name[0].find_elements_by_xpath('../p[@node-type="feed_list_content"]')
                if card_comment_content:
                    unfold_button2 = card_comment_content[0].find_elements_by_xpath('./a[@action-type="fl_unfold"]')
                    if unfold_button2:
                        unfold_button2[0].click()
                        card_comment_content_full = \
                        card_comment_content[0].find_elements_by_xpath('../p[@node-type="feed_list_content_full"]')[
                            0].text.replace('\n', '').replace('收起全文d', '')
                        wb2['longText'] = re.sub(r'(.*)(L.*的微博视频)', r'\1', card_comment_content_full)
                        wb2['isLongText'] = True
                    else:
                        wb2['text'] = re.sub(r'(.*)(L.*的微博视频)', r'\1', card_comment_content[0].text.replace('\n', ''))
                        wb2['isLongText'] = False
                comment_time = card_comment[0].find_elements_by_xpath('.//p[@class="from"]/a[@target="_blank"]')
                if comment_time:
                    if '年' in comment_time[0].text:
                        wb2['created_at'] = re.sub(r'(.*)年(.*)月(.*)日 (.*)', r'\1/\2/\3 \4', comment_time[0].text)
                    else:
                        wb2['created_at'] = datetime.datetime.now().strftime('%Y') + '/' + re.sub(r'(.*)月(.*)日 (.*)',
                                                                                                  r'\1/\2 \3',
                                                                                                  comment_time[0].text)
            else:
                pass
        print('----')
        if wb1['text'] != '' and keyword in wb1['text']  :
            wb1['location'] = get_location_from_page(wb1['uid'])
            rows = [
                [keyword,  wb1['text'],'', wb1['name'], wb1['uid'], wb1['location'], wb1['isLongText'],wb1['created_at']]
            ]
            with open('weibo_220111_face.csv', 'a', newline='',encoding='utf-8-sig') as f:
                f_csv = csv.writer(f)
                f_csv.writerows(rows)
            # mycol.insert_one(wb1)
            print('insert')
        elif wb1['longText'] != '' and keyword in wb1['longText']:
            wb1['location'] = get_location_from_page(wb1['uid'])

            rows = [
                [keyword, '',  wb1['longText'],  wb1['name'], wb1['uid'], wb1['location'], wb1['isLongText'],wb1['created_at']]
            ]
            with open('weibo_220111_face.csv', 'a', newline='',encoding='utf-8-sig') as f:
                f_csv = csv.writer(f)
                f_csv.writerows(rows)

            # mycol.insert_one(wb1)
            print('insert')
        if wb2['text'] != '' and keyword in wb2['text']:
            wb2['location'] = get_location_from_page(wb2['uid'])
            rows = [
                [ keyword,  wb2['text'],  '', wb2['name'],  wb2['uid'], wb2['location'], wb2['isLongText'],wb2['created_at']]
            ]
            with open('weibo_220111_face.csv', 'a', newline='',encoding='utf-8-sig') as f:
                f_csv = csv.writer(f)
                f_csv.writerows(rows)
            # mycol.insert_one(wb2)
            print('insert')
        elif wb2['longText'] != '' and keyword in wb2['longText']:
            wb2['location'] = get_location_from_page(wb2['uid'])
            rows = [
                [ keyword,  '', wb2['longText'], wb2['name'], wb2['uid'], wb2['location'], wb2['isLongText'],wb2['created_at']]
            ]
            with open('weibo_220111_face.csv', 'a', newline='',encoding='utf-8-sig') as f:
                f_csv = csv.writer(f)
                f_csv.writerows(rows)
            # mycol.insert_one(wb2)
            print('insert')


def main():
    login()
    search(keyword= args.keyword, start=args.start, end=args.end)

if __name__ == '__main__':
    main()