<template>
  <div >
    <div  ref="myEchart" style="height:100%;width:100%"></div>
  </div>
</template>

<script>
  import * as  echarts from "echarts";
    export default {
      name: "calendar",
      props: ["calendarData","active_keyword","active_timescope","active_year"],
      data() {
        return {
          chart: null,
          myChart:"",
          timer:"",
          keyword:"人脸识别",
          timescope:"24h",
          year:"",
          processedData:[],
          monthCount:1,
        };
      },
      mounted() {
        this.myChart = echarts.init(this.$refs.myEchart);
        this.myChart.showLoading();
      },
      beforeDestroy() {
        if (!this.myChart) {
          return;
        }
        this.myChart.dispose();
        this.myChart = null;
      },
      methods: {
        switch_configure(){
          let tempData = JSON.parse(JSON.stringify(this.processedData));
          for(let i in tempData){
            if(Number(tempData[i][0].slice(5,7)) != this.monthCount){
              tempData[i][1] = this.processedData[i][1]-99999;
            }
          };
          let option = {
            tooltip: {},
            visualMap: {
              min: 0,
              max: this.processedData[this.processedData.length-1][1],
              type: 'piecewise',
              orient: 'horizontal',
              left: 'center',
              top: 0,
              textStyle:{
                color:'rgba(255,255,255,1)',
              },
            },
            calendar: {
              top: 45,
              bottom:25,
              cellSize: ['auto', 13],
              range: this.active_year,
              itemStyle: {
                borderWidth: 0.5
              },
              yearLabel: { show: false },
              textStyle:{
                color:'rgba(255,255,255,1)',
              },
              dayLabel:{color:'rgba(255,255,255,1)'},
            },
            series: {
              id:'calendar',
              type: 'heatmap',
              coordinateSystem: 'calendar',
              data: tempData,
              animationDurationUpdate:500,
              universalTransition: true,
            }
          };
          option && this.myChart.setOption(option);
          this.monthCount += 1;
          this.monthCount = this.monthCount>12 ? 1:this.monthCount;
        },
        processData(){
          let data = this.calendarData[this.active_keyword];
          let list=[]
          for (let i in data){
            if(i.slice(0,4) == this.active_year){
              list.push([echarts.time.format(echarts.time.parse(i),'{yyyy}-{MM}-{dd}', false),data[i]])
            }
          }
          list.sort(function(a,b){
            return a[1]-b[1]
          })
          return list
        },
        setOption(){
          this.processedData = this.processData()
          let tempData = JSON.parse(JSON.stringify(this.processedData));
          for(let i in tempData){
            if(Number(tempData[i][0].slice(5,7)) != this.monthCount){
              tempData[i][1] = this.processedData[i][1]-99999;
            }
          };
          this.monthCount += 1;

          this.myChart.hideLoading()
          window.onresize = this.myChart.resize;

          let option = {

            tooltip: {},
            visualMap: {
              min: 0,
              max: this.processedData[this.processedData.length-1][1],
              type: 'piecewise',
              orient: 'horizontal',
              left: 'center',
              top: 0,
              textStyle:{
                color:'rgba(255,255,255,1)',
              },
            },
            calendar: {
              top: 45,
              left:30,
              bottom:25,
              cellSize: ['auto', 13],
              range: this.active_year,
              itemStyle: {
                borderWidth: 0.5
              },
              yearLabel: { show: false },
              textStyle:{
                color:'rgba(255,255,255,1)',
              },
              dayLabel:{color:'rgba(255,255,255,1)'},
            },
            series: {
              id:'calendar',
              type: 'heatmap',
              coordinateSystem: 'calendar',
              data: tempData,
              animationDurationUpdate: 500,
              universalTransition: true,
            }
          };
          option && this.myChart.setOption(option);

          this.timer = setInterval(this.switch_configure, 4000);

        },
      },
      watch:{     //监听value的变化，进行相应的操作即可
        "calendarData": function (newv, oldv) {
          clearInterval(this.timer)
          this.setOption()
        },
        "active_timescope" : function (newv, oldv) {
          this.timescope = newv
          clearInterval(this.timer)
          this.myChart.clear()
          this.setOption()
        },
        "active_keyword" : function (newv, oldv) {
          this.keyword = newv
          clearInterval(this.timer)
          this.setOption()
        },
      },
    }
</script>

<style scoped>

</style>
