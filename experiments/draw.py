import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import datetime

df = pd.read_csv(r'C:\Users\sstl\Documents\GitHub\mongo_data.csv' ,sep=' ')
# text sentiment created_at
times = pd.date_range('2022-04-01',periods = 30, freq='1d')
sent_values = [0 for i in range(30)]
df = df.values
for data in df:
    if data[2][:4] == '2022':
        if data[2][5:7] == '04':
            if data[1] == 'positive':

                sent_values[int(data[2][8:10])-1]+=1
            else:
                sent_values[int(data[2][8:10])-1]-=1

    # datetime.datetime.strptime()


fig, ax = plt.subplots(1)
fig.autofmt_xdate() #自动旋转x坐标
plt.plot(times, sent_values)
#
# xfmt = mdates.DateFormatter('%d-%m-%y %H:%M')
# ax.xaxis.set_major_formatter(xfmt)

plt.show()