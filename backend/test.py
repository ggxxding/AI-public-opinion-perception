import datetime
one_day = datetime.timedelta(days=1)
start_date = datetime.datetime.strptime('2021-01-01', '%Y-%m-%d')
end_date = datetime.datetime.strptime('2021-12-02', '%Y-%m-%d')
temp_date = start_date
while ((end_date - temp_date).days > 0):
    timescope = temp_date.strftime('%Y-%m-%d') + ':' + (temp_date + one_day).strftime('%Y-%m-%d')
    print(timescope)
    # params = {
    #     'q': keyword,
    #     'typeall': 1,
    #     'suball': 1,
    #     'timescope': timescope,
    #     'Refer': 'SWeibo_box',
    # }
    #
    # url = base_url + urlencode(params)
    # print(url)
    #
    # driver.get(
    #     'https://s.weibo.com/weibo?q=人工智能&typeall=1&suball=1&timescope=custom:2021-12-01:2021-12-02&Refer=SWeibo_box')
    #
    #
    temp_date = temp_date + one_day
