<template>
  <div  ref="myEchart" style="width:100%;height:100%" ></div>
</template>

<script>
  import * as  echarts from "echarts";
    export default {
        name: "barData.vue",
      props: ["barData","active_keyword","active_timescope","active_year"],
      data() {
        return {
          chart: null,
        };
      },
      mounted() {
        var myChart = echarts.init(this.$refs.myEchart);
        myChart.showLoading();
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
          let myChart = echarts.init(this.$refs.myEchart); //这里是为了获得容器所在位置
          myChart.hideLoading();
          window.onresize = myChart.resize;
          var item = {
            name: '',
            value: this.barData['data'][this.active_keyword][this.active_timescope][6],
            // 柱子颜色
            itemStyle: {
              color: '#254065'
            },
            // 鼠标经过柱子颜色
            emphasis: {
              itemStyle: {
                color: '#254065'
              }
            },
            // 工具提示隐藏
            tooltip: {
              extraCssText: 'opacity:0'
            }
          };
          this.barData['data'][this.active_keyword][this.active_timescope][5] = item;
          this.barData['data'][this.active_keyword][this.active_timescope][6] = item;
          this.barData['data'][this.active_keyword][this.active_timescope][7] = item;

          myChart.setOption({
            // 工具提示
            tooltip: {
              // 触发类型  经过轴触发axis  经过轴触发item
              trigger: 'item',
              // 轴触发提示才有效
              axisPointer: {
                // 默认为直线，可选为：'line' 线效果 | 'shadow' 阴影效果
                type: 'shadow'
              }
            },
            // 图表边界控制
            grid: {
              // 距离 上右下左 的距离
              left: '0',
              right: '3%',
              bottom: '3%',
              top: '5%',
              // 大小是否包含文本【类似于boxsizing】
              containLabel: true,
              //显示边框
              show: true,
              //边框颜色
              borderColor: 'rgba(0, 240, 255, 0.3)'
            },
            // 控制x轴
            xAxis: [
              {
                // 使用类目，必须有data属性
                type: 'category',
                // 使用 data 中的数据设为刻度文字
                data: this.barData['cities'][this.active_keyword][this.active_timescope],
                // 刻度设置
                axisTick: {
                  // true意思：图形在刻度中间
                  // false意思：图形在刻度之间
                  alignWithLabel: false,
                  show: false
                },
                //文字
                axisLabel: {
                  color: '#4c9bfd'
                }
              }
            ],
            // 控制y轴
            yAxis: [
              {
                // 使用数据的值设为刻度文字
                type: 'value',
                axisTick: {
                  // true意思：图形在刻度中间
                  // false意思：图形在刻度之间
                  alignWithLabel: false,
                  show: false
                },
                //文字
                axisLabel: {
                  color: '#4c9bfd'
                },
                splitLine: {
                  lineStyle: {
                    color: 'rgba(0, 240, 255, 0.3)'
                  }
                },
              }
            ],
            // 控制x轴
            series: [
              {
                // series配置
                // 颜色
                itemStyle: {
                  // 提供的工具函数生成渐变颜色
                  color: new echarts.graphic.LinearGradient(
                    // (x1,y2) 点到点 (x2,y2) 之间进行渐变
                    0, 0, 0, 1,
                    [
                      { offset: 0, color: '#00fffb' }, // 0 起始颜色
                      { offset: 1, color: '#0061ce' }  // 1 结束颜色
                    ]
                  )
                },
                // 图表数据名称
                name: '',
                // 图表类型
                type: 'bar',
                // 柱子宽度
                barWidth: '60%',
                // 数据
                data: this.barData['data'][this.active_keyword][this.active_timescope],
              }
            ]
            }
          )
        }
      },
      watch:{     //监听value的变化，进行相应的操作即可
        "barData": function (newv, oldv) {
          this.setOption()
        },
        "active_timescope" : function (newv, oldv) {
          this.setOption()
        },
        "active_keyword" : function (newv, oldv) {
          this.setOption()
        },
      },
    }
</script>

<style scoped>

</style>
