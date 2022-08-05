import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import datetime

df = pd.read_csv('mongo_data.csv' ,sep=' ')
df = df.values
for data in df:
    if data[2][:4] == '2022':
        print(data[2])
    # datetime.datetime.strptime()


times = pd.date_range('2015-10-06', periods=500, freq='10min')
print(times)
print(type(times))
fig, ax = plt.subplots(1)
fig.autofmt_xdate() #自动旋转x坐标
plt.plot(df['created_at'].values[:100], range(len(df['created_at'].values[:100])))


xfmt = mdates.DateFormatter('%d-%m-%y %H:%M')
ax.xaxis.set_major_formatter(xfmt)
plt.show()