<template>
  <div>
<!--    <el-row>-->
<!--      <el-col :span="24">-->
<!--      <boldHeader></boldHeader>-->
<!--      </el-col>-->
<!--    </el-row>-->
    <el-row>
      <el-col :span="8">
        <div class="overview panel">
          <div class="inner">
            <div class="item">
              <h4>2,190</h4>
              <span>
                <i class="icon-dot" style="color: #006cff"></i>
                数据总数
              </span>
            </div>
            <div class="item">
              <h4>190</h4>
              <span>
                <i class="icon-dot" style="color: #6acca3"></i>
                人工智能
              </span>
            </div>
            <div class="item">
              <h4>3,001</h4>
              <span>
                <i class="icon-dot" style="color: #6acca3"></i>
                人脸识别
              </span>
            </div>
            <div class="item">
              <h4>108</h4>
              <span>
                <i class="icon-dot" style="color: #ed3f35"></i>
                其他
              </span>
            </div>
          </div>
        </div>
        <div class="times panel" >
          <div class="inner">
            <div class="caption">
            <h3 >时间统计</h3>
              <a href="javascript:;" @click="teest">2021</a>
              <a >2020</a>
              <a href="javascript:;" >2019</a>
              <a href="javascript:;" >更早</a>
            </div>
            <div class="chart" >
              <lineChart :lineData="lineData.y2021" :style="{height:0.09*screenWidth+'px' ,width:'100%'}"></lineChart>
            </div>
          </div>
        </div>
        <div style="background-color: 'red'; height: 50*screenWidth+'px'"></div>

      </el-col>
      <el-col :span="16">
        <div class="map">
          <div class="chart">
            <div class="geo">

            </div>
          </div>
          <echarts :style='{height: 0.9*screenWidth+"px"}'></echarts>
        </div>
      </el-col>
      <el-col :span="8"></el-col>
    </el-row>

<!--    <el-row>-->
<!--      <el-col :span="24">-->
<!--        <el-form :inline="true" :model="formInline" class="demo-form-inline" style="text-align:center">-->
<!--          <el-form-item label="关键字">-->
<!--            <el-input v-model="formInline.keyword" placeholder="搜索关键字"></el-input>-->
<!--          </el-form-item>-->
<!--          <el-form-item>-->
<!--            <el-button type="primary" @click="searching">搜索</el-button>-->
<!--          </el-form-item>-->
<!--        </el-form>-->
<!--      </el-col>-->
<!--    </el-row>-->
<!--    <el-row>-->
<!--      <el-col :span="16" >-->
<!--        <echarts :userJson="response" :style="{ height: screenWidth*0.3 + 'px' ,width:'100%'}" ></echarts>-->
<!--      </el-col>-->
<!--      <el-col :span="8">-->
<!--        <el-row>-->
<!--          <sentiment :userJson="sentimentResponse" ></sentiment>-->
<!--        </el-row>-->
<!--        <el-row>-->
<!--          <wordCloud :geturl="picurl"></wordCloud>-->
<!--        </el-row>-->
<!--      </el-col>-->
<!--    </el-row>-->
  </div>
</template>
/*
网页可见区域宽：document.body.clientWidth
网页可见区域高：document.body.clientHeight
网页可见区域宽：document.body.offsetWidth (包括边线的宽)
网页可见区域高：document.body.offsetHeight (包括边线的宽)
*/
<script>
  import panel from './panel';
  import echarts from './echarts'
  import boldHeader from "./boldHeader";
  import axios from 'axios';
  import sentiment from './sentiment';
  import wordCloud from './wordCloud';
  import lineChart from './lineChart';

export default {
  name: 'HelloWorld',
  data () {
    return {
      screenWidth: document.documentElement.clientWidth,
      url:"http://192.168.71.214:5000/",
      msg: 'Welcome to Your Vue.js App',
      formInline: {
        keyword: '',
      },
      response:[{'name':'上海',value:'999'}],
      sentimentResponse:[{'name':'pos','value':50},{'name':'neg','value':50}],
      picurl:null,
      lineData:{
        y2021:
          [24, 40, 101, 134, 90, 230, 210, 230, 120, 230, 210, 120],
        y2020:
          [23, 75, 12, 97, 21, 67, 98, 21, 43, 64, 76, 38],
        y2019:
          [34, 87, 32, 76, 98, 12, 32, 87, 39, 36, 29, 36],
        earlier:
          [43, 73, 62, 54, 91, 54, 84, 43, 86, 43, 54, 53],
      },
    }
  },
  mounted(){
    window.onresize = () => {
      return (() => {
        // 可以限制最小高度
        // if (document.body.clientHeight - 240 < 450) {
        //   return
        // }
        window.screenWidth =document.documentElement.clientWidth
        this.screenWidth = window.screenWidth
      })()
    };
    //this.timer();
  },
  methods:{
    teest(){
      this.lineData=[1,1,1,1,1,1,1,1,1,1,1,1];
      console.log(this.lineData);

    },
    timer(){
      var index = 0;
      var timer = setInterval(function () {
        index++;
        if (index > 4) {
          index = 0;
        };
        console.log(index);
      }, 2000);
    },
    searching() {
      console.log('submit!');
      this.$message.success("提交成功,请耐心等待输出结果");
      let data = new FormData(); // FormData 对象
      data.append("keyword", this.formInline.keyword);
      axios({
        method: 'post',
        url: this.url+'searching',
        data: data,
        headers: {'Content-Type': 'multipart/form-data'}
      }).then(res => {
        console.log(res);
        console.log(res.data);
        this.response=res.data['cityList'];
        this.sentimentResponse=res.data['sentiment'];
        this.picurl=res.data['img_stream'];
        //this.form.accuracy = res.data.probability;
      }).catch((error) => {
        // eslint-disable-next-line
        console.error(error);
      });
    },
  },
  components:{
    boldHeader,
    echarts,
    panel,
    sentiment,
    wordCloud,
    lineChart,
  },
  watch:{     //监听value的变化，进行相应的操作即可
    screenHeight (val) {
      // 为了避免频繁触发resize函数导致页面卡顿，使用定时器
      if (!this.timer) {
        // 一旦监听到的screenWidth值改变，就将其重新赋给data里的screenWidth
        this.screenHeight = val
        this.timer = true
        let that = this
        setTimeout(function () {
          // 打印screenWidth变化的值
          console.log(that.screenHeight)
          that.timer = false
        }, 400)
      }
    }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

  h1, h2 {
    font-weight: normal;
  }
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    display: inline-block;
    margin: 0 10px;
  }
  a {
    color: #42b983;
  }
</style>
