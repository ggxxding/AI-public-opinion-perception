from wordcloud import WordCloud
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import jieba
import pandas as pd
import base64

keyword_dict = {'人工智能':'AI','人脸识别':'face','智慧医疗':'med','随申码':'code'}
def return_img_stream(img_local_path):
  """
  工具函数:
  获取本地图片流
  :param img_local_path:文件单张图片的本地绝对路径
  :return: 图片流
  """

  img_stream = ''
  with open(img_local_path, 'rb') as img_f:
    img_stream = img_f.read()
    img_stream = base64.b64encode(img_stream).decode()
  return img_stream

def draw(textList, keyword):

    font_path='res/SimHei.ttf'
    # print(textList)
    text = ' '.join(textList)
    text = jieba.cut(text)
    text = [x for x in text if len(x)>1 and x not in ['全文','码崩']]
    text = ' '.join(text)
    # print(text)
    #mask = np.array(Image.open('res/china.jpg'))
    wc = WordCloud(width = 878,height = 720,font_path=font_path, mode='RGBA', background_color=None).generate(text)

    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis('off')
    plt.show()

    wc.to_file('wordcloud_'+ keyword_dict[keyword] +'.png')
    img_stream = return_img_stream('wordcloud_'+keyword_dict[keyword]+'.png')
    return img_stream