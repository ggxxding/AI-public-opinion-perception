<template>
  <div class="hello">
    <el-row>
      <el-col :span="24">
      <boldHeader></boldHeader>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <el-form :inline="true" :model="formInline" class="demo-form-inline">
          <el-form-item label="关键字">
            <el-input v-model="formInline.keyword" placeholder="搜索关键字"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searching">搜索</el-button>
          </el-form-item>
        </el-form>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="24">
        <echarts :userJson="response"></echarts>
      </el-col>
    </el-row>
  </div>
</template>

<script>
  import panel from './panel';
  import echarts from './echarts'
  import boldHeader from "./boldHeader";
  import axios from 'axios';
export default {
  name: 'HelloWorld',
  data () {
    return {
      url:"http://192.168.71.214:5000/",
      msg: 'Welcome to Your Vue.js App',
      formInline: {
        keyword: '',
      },
      response:[{'name':'上海',value:'999'}],
    }
  },
  methods:{
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
        this.response=res.data;
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
  }
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
