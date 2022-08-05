import json
import time
from selenium import webdriver
import requests

def test(sub):
    res = requests.get('https://weibo.com',headers = {'Cookie': 'SUB=' + sub}).text
    if 'ggxxding' in res:
        return True
    else:
        return False

options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--headless')
chrome = webdriver.Chrome(options=options)
chrome.set_window_size(1920, 1080)
chrome2 = webdriver.Chrome(options=options)
chrome2.set_window_size(1920, 1080)

chrome.get('https://weibo.com/login.php')
chrome2.get('https://weibo.com/login.php')
time.sleep(5)
chrome.find_elements_by_xpath('//a[@action-data="type=qrcode"]')[0].click()
time.sleep(2)
chrome.save_screenshot('screenshots/screenshot.png')
input('等待登录')

with open('cookies.txt', 'r', encoding='utf8') as f:
    Cookies = json.loads(f.read())
for cookie in Cookies:
    chrome2.add_cookie(cookie)
chrome2.refresh()
time.sleep(5)

chrome.save_screenshot('screenshots/screenshot.png')
chrome2.save_screenshot('screenshots/screenshot2.png')
print('save screenshot')

sub1 = chrome.get_cookie('SUB')
sub2 = chrome2.get_cookie('SUB')

while (1):
    chrome.refresh()
    time.sleep(10)
    while (chrome.get_cookie('SUB') == None):
        chrome.refresh()
        time.sleep(10)
        print('chrome_1重新刷新')
    sub1_1 = chrome.get_cookie('SUB')

    chrome2.refresh()
    time.sleep(10)
    while (chrome2.get_cookie('SUB') == None):
        chrome2.refresh()
        time.sleep(10)
        print('chrome_2重新刷新')
    sub2_2 = chrome2.get_cookie('SUB')

    print('sub1  =', sub1['value'])
    print('sub1_1=', sub1_1['value'])
    print('sub1有效:', test(sub1['value']))
    print('sub1_1有效:', test(sub1_1['value']))
    print('sub1相等:', sub1['value'] == sub1_1['value'])
    print('sub2  =', sub2['value'])
    print('sub2_2=', sub2_2['value'])
    print('sub2有效:', test(sub2['value']))
    print('sub2_2有效:', test(sub2_2['value']))
    print('sub2相等:', sub2['value'] == sub2_2['value'])
    sub1 = sub1_1
    sub2 = sub2_2
    time.sleep(1800)

