<template>
    <div  ref="myEchart" style="width:100%;height:100%" ></div>
</template>
<script>
  import * as  echarts from "echarts";
  export default {
    name: "lineChart.vue",
    props: ["lineData","year"],
    data() {
      return {
        chart: null,
      };
    },
    mounted() {
      this.setOption();
    },
    beforeDestroy() {
      if (!this.chart) {
        return;
      }
      this.chart.dispose();
      this.chart = null;
    },
    methods: {
      setOption() {
        console.log('draw!')
        console.log(this.lineData)


        let myChart = echarts.init(this.$refs.myEchart); //这里是为了获得容器所在位置
        window.onresize = myChart.resize;
        myChart.setOption({
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            // 类目类型
            type: 'category',
            // x轴刻度文字
            data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
            axisTick: {
              show: false//去除刻度线
            },
            axisLabel: {
              color: '#4c9bfd'//文本颜色
            },
            axisLine: {
              show: false//去除轴线
            },
            boundaryGap: false//去除轴内间距
          },
          yAxis: {
            // 数据作为刻度文字
            type: 'value',
            axisTick: {
              show: false//去除刻度线
            },
            axisLabel: {
              color: '#4c9bfd'//文本颜色
            },
            axisLine: {
              show: false//去除轴线
            },
            boundaryGap: false//去除轴内间距
          },
          //图例组件
          legend: {
            textStyle: {
              color: '#4c9bfd' // 图例文字颜色

            },
            right: '10%'//距离右边10%
          },
          grid: {
            show: true,// 显示边框
            top: '20%',
            left: '3%',
            right: '4%',
            bottom: '3%',
            borderColor: '#012f4a',// 边框颜色
            containLabel: true // 包含刻度文字在内
          },
          series: [
            {
              name: '当月微博数',
              data: this.lineData[this.year],
              type: 'line',
              smooth: true,
              itemStyle: {
                color: '#00f2f1'  // 线颜色
              }
            }
          ]
        })
      }
    },
    watch:{     //监听value的变化，进行相应的操作即可
      "lineData": function (newv, oldv) {
        this.setOption()
      },
      "year" : function (newv, oldv) {
        this.setOption()
      },
    },
  }
</script>
