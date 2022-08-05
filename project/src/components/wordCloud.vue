<template>
      <div class="demo-image__placeholder">
        <div class="block">
          <span class="demonstration"></span>
          <el-image :src="src" style="width: 100%; height: 100%" :fit="contain">
            <div slot="placeholder" class="image-slot">
              加载中<span class="dot">...</span>
            </div>
          </el-image>
        </div>
      </div>
</template>

<script>
    export default {
        name: "wordCloud",
      props: [
        'wordCloudStream','active_keyword','active_timescope'
      ],
      data() {
        return {
          src: 'https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg'
        }
      },
      watch:{     //监听value的变化，进行相应的操作即可
        "wordCloudStream": {
          immediate:false,
          handler:function(newValue, oldValue) {
            this.src = 'data:image/png;base64,' + this.wordCloudStream[this.active_keyword]['24h'];
            //console.log(typeof newValue)
          },
        },
        "active_keyword": {
          immediate:false,
          handler:function(newValue, oldValue) {
            let tempStr = newValue;
            console.log('!!!!!!')
            console.log(this.wordCloudStream)
            this.src = 'data:image/png;base64,' + this.wordCloudStream[this.active_keyword]['24h'];
            //console.log(typeof newValue)
          },
        },
        "active_timescope": {
          immediate:false,
          handler:function(newValue, oldValue) {
            let tempStr = newValue;
            this.src = 'data:image/png;base64,' + this.wordCloudStream[this.active_keyword]['24h'];
            //console.log(typeof newValue)
          },
        }
      }
    }
</script>

<style scoped>

</style>
