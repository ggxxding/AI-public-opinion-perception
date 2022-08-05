<template>
  <div  ref="myEchart" style="width:100%;height:100%" ></div>
</template>

<script>
  import * as  echarts from "echarts";
    export default {
        name: "clusterGraph.vue",
      props: ["clusterData","active_keyword","active_timescope"],
      data() {
        return {
          chart: null,
          graph:{
            "nodes": [
              {
                "id": "0",
                "name": "Myriel",
                "symbolSize": 19.12381,
                "x": -266.82776,
                "y": 299.6904,
                "value": 28.685715,
                "category": 0
              },
            ],
            "links": [
            ],
            "categories": [
              {
                "name": "A"
              }
            ]
          },
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
          window.onresize = myChart.resize;
          myChart.hideLoading();

          myChart.setOption({

            tooltip: {},
            legend: [
              {
                data: this.clusterData[this.active_keyword][this.active_timescope]['categories'].map(function (a) {
                  return a.name;
                })
              }
            ],
            series: [
              {
                name: ' ',
                type: 'graph',
                layout: 'force',
                data: this.clusterData[this.active_keyword][this.active_timescope]['nodes'],
                links: this.clusterData[this.active_keyword][this.active_timescope]['links'],
                categories: this.clusterData[this.active_keyword][this.active_timescope]['categories'],
                roam: true,
                label: {
                  show: true,
                  position: 'right',
                  formatter: '{b}',
                  fontSize:18,
                },
                // labelLayout: {
                //   hideOverlap: true
                // },
                scaleLimit: {
                  min: 0.4,
                  max: 2
                },
                force: {
                  repulsion:100,
                },
                lineStyle: {
                  color: 'none',
                  curveness: 0.3
                }
              }
            ]
          });
        },
      },
      watch:{     //监听value的变化，进行相应的操作即可
        "clusterData": function (newv, oldv) {
          console.log('loadededed')
          console.log(newv)
          this.active_timescope='24h'
          this.setOption()
        },
        "active_timescope" : function (newv, oldv) {
          this.active_timescope='24h'
          this.setOption()
        },
        "active_keyword" : function (newv, oldv) {
          this.active_timescope='24h'
          this.setOption()
        },
      },

    }
</script>

<style scoped>

</style>
