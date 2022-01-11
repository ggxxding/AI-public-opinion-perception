<template>
  <div>
<!--    <el-row>-->
<!--      <el-col :span="24">-->
<!--      <boldHeader></boldHeader>-->
<!--      </el-col>-->
<!--    </el-row>-->
    <el-row>
      <el-col :span="7">
        <div class="overview panel">
          <div class="inner">
            <div  class="item" >
              <h4 >2,190</h4>
              <span >
                <i class="icon-dot" style="color: #006cff"></i>
                <a href="javascript:;" :class="{active:active_all}" @click="click_all">数据总数</a>
              </span>
            </div>
            <div   class="item">
              <h4>190</h4>
              <span>
                <i class="icon-dot" style="color: #6acca3"></i>
                <a href="javascript:;" :class="{active:active_AI}" @click="click_AI">人工智能</a>
              </span>
            </div>
            <div class="item">
              <h4>3,001</h4>
              <span>
                <i class="icon-dot" style="color: #6acca3"></i>
                <a href="javascript:;" :class="{active:active_face}" @click="click_face">人脸识别</a>
              </span>
            </div>
            <div  class="item">
              <h4>108</h4>
              <span>
                <i class="icon-dot" style="color: #ed3f35"></i>
                <a href="javascript:;" :class="{active:active_other}" @click="click_other">其他</a>
              </span>
            </div>
          </div>
        </div>
        <div class="times panel" >
          <div class="inner">
            <div class="caption">
            <h3 >时间统计</h3>
              <a  href="javascript:;" :class="{active:active_2021}" @click="click_2021">2021</a>
              <a  href="javascript:;" :class="{active:active_2020}" @click="click_2020">2020</a>
              <a href="javascript:;" :class="{active:active_2019}" @click="click_2019">2019</a>
              <a href="javascript:;" :class="{active:active_earlier}" @click="click_earlier">更早</a>
            </div>
            <div class="chart" >
              <lineChart :lineData="lineData" :active_keyword="active_keyword" :active_year="active_year" :style="{height:0.09*screenWidth+'px' ,width:'100%'}"></lineChart>
            </div>
          </div>
        </div>



      </el-col>
      <el-col :span="10" style="padding: 1.333rem 0.833rem 0;">
        <div class="map">
          <div class="chart">
            <div class="geo">
              <echarts :mapData="mapData" :active_keyword="active_keyword" :active_year="active_year" :style='{height: 0.3025*screenWidth+"px"}'></echarts>
            </div>
          </div>
        </div>
        <div class="users panel">
          <div class="inner">
            <h3>全国微博数量统计</h3>
            <div class="chart">
              <barData class="bar" :barData="barData" :active_keyword="active_keyword" :active_year="active_year"   :style="{height:0.085*screenWidth+'px' ,width:'100%'}"></barData>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="7">
        <div class="sentiment panel">
          <div class="inner">
            <h3>情感分析</h3>
            <sentiment :sentiment="sentimentResponse" :style='{height: 0.2225*screenWidth+"px"}'></sentiment>
          </div>
        </div>
        <div class="word_cloud panel">
          <div class="inner">
            <wordCloud :wordCloudList="wordCloudList" :active_keyword="active_keyword" :active_year="active_year"  :style='{height: 0.1525*screenWidth+"px"}'></wordCloud>
          </div>
        </div>
      </el-col>
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
  import barData from './barData';

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
      mapData:{'人工智能':{'y2021':[{'name':'上海',value:'999'}]}},
      sentimentResponse:[{'name':'pos','value':50},{'name':'neg','value':50}],
      picurl:null,
      lineData:{
        '人工智能': {
          'y2021': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          'y2020': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          'y2019': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          'earlier': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
      },
      barData:{
        'data': {
          '人工智能': {
            'y2021': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            'y2020': [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'y2019': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'earlier': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          },
        },
        'cities': {
          '人工智能':{
            'y2021':['上海', '上海', '上海', '上海', '上海', '', '……', '', '上海', '上海', '上海', '上海', '上海'],
        }
    }
      },
      active_year: 'y2021',
      active_keyword: '人工智能',
      active_2021:true,
      active_2020:false,
      active_2019:false,
      active_earlier:false,
      active_all:false,
      active_AI:true,
      active_face:false,
      active_other:false,
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
    this.loadWeiboData();
  },
  methods:{
    click_2021(){
      this.active_year= 'y2021',
      this.active_2021=true;this.active_2020=false;this.active_2019=false;this.active_earlier=false;
    },
    click_2020(){
      this.active_year = 'y2020',
      this.active_2021=false;this.active_2020=true;this.active_2019=false;this.active_earlier=false;
    },
    click_2019(){
      this.active_year = 'y2019',
      this.active_2021=false;this.active_2020=false;this.active_2019=true;this.active_earlier=false;
    },
    click_earlier(){
      this.active_year =  'earlier',
      this.active_2021=false;this.active_2020=false;this.active_2019=false;this.active_earlier=true;
    },
    click_all(){
      this.active_keyword= '全部',
        this.active_all=true;this.active_AI=false;this.active_face=false;this.active_other=false;
    },
    click_AI(){
      this.active_keyword = '人工智能',
        this.active_all=false;this.active_AI=true;this.active_face=false;this.active_other=false;
    },
    click_face(){
      this.active_keyword = '人脸识别',
        this.active_all=false;this.active_AI=false;this.active_face=true;this.active_other=false;
    },
    click_other(){
      this.active_keyword =  '其他',
        this.active_all=false;this.active_AI=false;this.active_face=false;this.active_other=true;
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
    loadWeiboData(){
      let data = new  FormData(); // FormData 对象
      data.append("keyword", this.formInline.keyword);  //目前直接加载全部数据，该变量暂时不需要，暂时保留
      axios({
        method: 'post',
        url: this.url+'loadWeiboData',
        data: data,
        headers: {'Content-Type': 'multipart/form-data'}
      }).then(res=>{
        console.log(res.data);
        this.mapData=res.data['cityList'];
        this.lineData = res.data['timeList'];
        this.barData = res.data['barData'];
        this.wordCloudList = res.data['wordCloudList']

      }).catch((error)=>{
        console.error(error);
      })

    },
  },
  components:{
    boldHeader,
    echarts,
    panel,
    sentiment,
    wordCloud,
    lineChart,
    barData,
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


</style>
