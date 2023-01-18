map<template>
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
            <div class="filter">
              <a href="javascript:;" :class="{active:active_24h}" @click="click_24h">24小时</a>
              <a href="javascript:;" :class="{active:active_30d}" @click="click_30d">30天</a>
              <a href="javascript:;" :class="{active:active_90d}" @click="click_90d">90天</a>
              <a href="javascript:;" :class="{active:active_365d}" @click="click_365d">365天</a>
            </div>
            <div class="data">
              <div  class="item" >
                <h4 >{{this.countDict['人工智能'][this.active_timescope]}}</h4>
                <span >
                <i class="icon-dot" style="color: #006cff"></i>
                <a href="javascript:;" :class="{active:active_AI}" @click="click_AI">人工智能</a>
              </span>
              </div>
              <div   class="item">
                <h4>{{this.countDict['人脸识别'][this.active_timescope]}}</h4>
                <span>
                <i class="icon-dot" style="color: #6acca3"></i>
                <a href="javascript:;" :class="{active:active_face}" @click="click_face">人脸识别</a>
              </span>
              </div>
              <div class="item">
                <h4>{{this.countDict['智慧医疗'][this.active_timescope]}}</h4>
                <span>
                <i class="icon-dot" style="color: #6acca3"></i>
                <a href="javascript:;" :class="{active:active_medical}" @click="click_medical">智慧医疗</a>
              </span>
              </div>
              <div  class="item">
                <h4>{{this.countDict['随申码'][this.active_timescope]}}</h4>
                <span>
                <i class="icon-dot" style="color: #ed3f35"></i>
                <a href="javascript:;" :class="{active:active_health_code}" @click="click_health_code">随申码</a>
              </span>
              </div>
            </div>
          </div>
        </div>
        <div class="times panel" >
          <div class="inner">
            <div class="caption">
            <h3 >时间统计</h3>
              <a  href="javascript:;" :class="{active:active_2022}" @click="click_2022">2022</a>
              <a  href="javascript:;" :class="{active:active_2021}" @click="click_2021">2021</a>
              <a href="javascript:;" :class="{active:active_2020}" @click="click_2020">2020</a>
              <a href="javascript:;" :class="{active:active_earlier}" @click="click_earlier">更早</a>
            </div>
            <div class="chart" >
              <lineChart :lineData="lineData" :active_keyword="active_keyword" :active_year="active_year" :style="{height:0.09*screenWidth+'px' ,width:'100%'}"></lineChart>
            </div>
          </div>
        </div>
        <div class="clusterGraph panel">
          <div class="inner">
            <h3>聚类结果(24小时)</h3>
            <div class="chart">
              <clusterGraph :clusterData="clusterData" :active_keyword="active_keyword" :active_timescope="active_timescope" :style="{height:0.257*screenWidth+'px' ,width:'100%'}">
              </clusterGraph>
            </div>
          </div>
        </div>



      </el-col>
      <el-col :span="10" style="padding: 1.333rem 0.833rem 0;">
        <div class="map">
          <div class="chart">
            <div class="geo">
              <echarts :mapData="mapData" :active_keyword="active_keyword" :active_timescope="active_timescope"  :active_year="active_year" :style='{height: 0.3025*screenWidth+"px"}'></echarts>
            </div>
          </div>
        </div>
        <div class="users panel">
          <div class="inner">
            <h3>全国微博数量统计</h3>
            <div class="chart">
<!--              <barData class="bar" :barData="barData" :active_keyword="active_keyword" :active_timescope="active_timescope" :active_year="active_year"   :style="{height:0.085*screenWidth+'px' ,width:'100%'}"></barData>-->
              <calendar class="calendar" :calendarData="timeDict" :active_keyword="active_keyword" :active_timescope="active_timescope" :active_year="active_year"   :style="{height:0.085*screenWidth+'px' ,width:'100%'}"></calendar>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="7">
        <div class="sentiment panel">
          <div class="inner">
            <h3>情感分析</h3>
            <sentiment :sentiment="sentimentResponse" :active_keyword="active_keyword" :active_timescope="active_timescope" :style='{height: 0.2025*screenWidth+"px"}'></sentiment>
          </div>
        </div>
        <div class="word_cloud panel">
          <div class="inner">
            <wordCloud :wordCloudStream="wordCloudStream" :active_keyword="active_keyword"  :active_timescope="active_timescope"  :style='{height: 0.1925*screenWidth+"px"}'></wordCloud>
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
  import clusterGraph from './clusterGraph';
  import calendar from './calendar';

export default {
  name: 'HelloWorld',
  data () {
    return {
      timer:"",
      screenWidth: document.documentElement.clientWidth,
      url:"http://192.168.71.214:5000/",
      msg: 'Welcome to Your Vue.js App',
      formInline: {
        keyword: '',
      },
      countDict:{
        '人工智能':{'24h':1},
        '人脸识别':{'24h':1},
        '智慧医疗':{'24h':1},
        '随申码':{'24h':1},
      },
      mapData:{'人脸识别':{'24h':[{'name':'上海',value:'999'}]}},
      sentimentResponse:[{'name':'pos','value':50},{'name':'neg','value':50}],
      picurl:null,
      lineData:{
        '人脸识别': {
          '2022': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          '2021': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          '2020': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          'earlier': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
      },
      barData:{
        'data': {
          '人脸识别': {
            '24h': [0, 1, 1, 1, 2, 3, 4, 5, 6, 0, 0, 1, 0],
            '2021': [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            '2020': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'earlier': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          },
        },
        'cities': {
          '人脸识别':{
            '24h':['上海', '上海', '上海', '上海', '上海', '', '……', '', '上海', '上海', '上海', '上海', '上海'],
        }
    }
      },
      wordCloudStream:{
        '人脸识别':{
          '24h': 'https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg',
        }
      },

      clusterData:{
        '人脸识别':{
          '24h':{
            'nodes':[{'id':'c','name':'c','category':'a','value':77,"symbolSize": 7,}],
            'links':[],
            'categories':[{'name':'a'},{'name':'b'}],
          }
        }
      },

      active_timescope: '24h',
      active_year: '2022',
      active_keyword: '人脸识别',
      active_24h:true,
      active_30d:false,
      active_90d:false,
      active_365d:false,
      active_2022:true,
      active_2021:false,
      active_2020:false,
      active_earlier:false,
      active_AI:false,
      active_face:true,
      active_medical:false,
      active_health_code:false,
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
    this.loadWeiboData();


  },
  beforeDestroy () {
    clearInterval(this.timer);
  },
  methods:{
    switch_timescope(){
      console.log('switch')
      if(this.active_24h==true){
        this.click_30d();
      }else if (this.active_30d==true){
        this.click_90d();
      }else if (this.active_90d==true){
        this.click_365d();
      }else if (this.active_365d==true){
        this.click_24h();
      }
    },
    click_24h(){
      this.active_timescope= '24h',
        this.active_24h=true;this.active_30d=false;this.active_90d=false;this.active_365d=false;
    },
    click_30d(){
      this.active_timescope = '30d',
        this.active_24h=false;this.active_30d=true;this.active_90d=false;this.active_365d=false;
    },
    click_90d(){
      this.active_timescope = '90d',
        this.active_24h=false;this.active_30d=false;this.active_90d=true;this.active_365d=false;
    },
    click_365d(){
      this.active_timescope =  '365d',
        this.active_24h=false;this.active_30d=false;this.active_90d=false;this.active_365d=true;
    },
    click_2022(){
      this.active_year= '2022',
      this.active_2022=true;this.active_2021=false;this.active_2020=false;this.active_earlier=false;
    },
    click_2021(){
      this.active_year = '2021',
      this.active_2022=false;this.active_2021=true;this.active_2020=false;this.active_earlier=false;
    },
    click_2020(){
      this.active_year = '2020',
      this.active_2022=false;this.active_2021=false;this.active_2020=true;this.active_earlier=false;
    },
    click_earlier(){
      this.active_year =  'earlier',
      this.active_2022=false;this.active_2021=false;this.active_2020=false;this.active_earlier=true;
    },
    click_AI(){
      this.active_keyword = '人工智能',
        this.active_AI=true;this.active_face=false;this.active_medical=false;this.active_health_code=false;
    },
    click_face(){
      this.active_keyword = '人脸识别',
        this.active_AI=false;this.active_face=true;this.active_medical=false;this.active_health_code=false;
    },
    click_medical(){
      this.active_keyword =  '智慧医疗',
        this.active_AI=false;this.active_face=false;this.active_medical=true;this.active_health_code=false;
    },
    click_health_code(){
      this.active_keyword= '随申码',
        this.active_AI=false;this.active_face=false;this.active_medical=false;this.active_health_code=true;
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
        this.countDict = res.data['countDict'];
        this.mapData=res.data['cityList'];
        this.lineData = res.data['timeList'];
        this.timeDict = res.data['timeDict'];
        this.barData = res.data['barData'];
        this.wordCloudList = res.data['wordCloudList']
        this.wordCloudStream = res.data['wordCloudStream']

        this.clusterData = res.data['clusterResult']
        this.sentimentResponse = res.data['sentiment_result']
        console.log(this.wordCloud)
      }).catch((error)=>{
        console.error(error);
      })
      // this.timer = setInterval(  this.switch_timescope,4000)
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
    clusterGraph,
    calendar,
  },
  watch:{     //监听value的变化，进行相应的操作即可
    // screenHeight (val) {
    //   // 为了避免频繁触发resize函数导致页面卡顿，使用定时器
    //   if (!this.timer) {
    //     // 一旦监听到的screenWidth值改变，就将其重新赋给data里的screenWidth
    //     this.screenHeight = val
    //     this.timer = true
    //     let that = this
    //     setTimeout(function () {
    //       // 打印screenWidth变化的值
    //       console.log(that.screenHeight)
    //       that.timer = false
    //     }, 400)
    //   }
    // }
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>


</style>
