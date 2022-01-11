<template>
      <div class="demo-image__placeholder" style="background-color:#013954;width:100%;height:400px">
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
        'wordCloudList','active_keyword','active_year'
      ],
      data() {
        return {
          src: 'https://cube.elemecdn.com/6/94/4d3ea53c084bad6931a56d5158a48jpeg.jpeg'
        }
      },
      watch:{     //监听value的变化，进行相应的操作即可
        "wordCloudList": {
          immediate:false,
          handler:function(newValue, oldValue) {
            this.src = 'data:image/png;base64,' + this.wordCloudList[this.active_keyword][this.active_year];
            //console.log(typeof newValue)
          },
        },
        "active_keyword": {
          immediate:false,
          handler:function(newValue, oldValue) {
            let tempStr = newValue;
            this.src = 'data:image/png;base64,' + this.wordCloudList[this.active_keyword][this.active_year];
            //console.log(typeof newValue)
          },
        },
        "active_year": {
          immediate:false,
          handler:function(newValue, oldValue) {
            let tempStr = newValue;
            this.src = 'data:image/png;base64,' + this.wordCloudList[this.active_keyword][this.active_year];
            //console.log(typeof newValue)
          },
        }
      }
    }
</script>

<style scoped>

</style>
