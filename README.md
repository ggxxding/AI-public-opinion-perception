# AI-public-opinion-perception
python3.8

安装哈工大LTP(4.1.5post2): pip install ltp

import ltp可能遇到找不到GLIBCXX_3.4.21,需要升级gcc到6.1.0以上,参考http://blog.sina.com.cn/s/blog_15ae676c40102wv6w.html

1 wget http://ftp.gnu.org/gnu/gcc/gcc-6.1.0/gcc-6.1.0.tar.gz
2 tar -zvxf gcc-6.1.0.tar.gz --directory=/usr/local/
3 cd /usr/local/gcc-6.1.0
4 ./contrib/download_prerequisites  
5 mkdir build && cd build  
6  ../configure -enable-checking=release -enable-languages=c,c++ -disable-multilib  
7 make && make install  

修改软连接步骤,214服务器上GLIBCXX报错目录是/lib64/libstdc++.so.6,
复制的文件目录/usr/local/gcc-6.1.0/build/prev-x86_64-pc-linux-gnu/libstdc++-v3/src/.libs/
其余参考链接即可

SKEP（百度情感分析模型）安装:https://github.com/baidu/Senta#skep

（提前安装paddlepaddle)

git clone https://github.com/baidu/Senta.git

cd Senta

python -m pip install .

