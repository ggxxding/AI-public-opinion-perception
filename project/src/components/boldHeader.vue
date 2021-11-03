<template>
  <div class="root">
    <el-row class="top">
      <el-col :span="24" >
            <div>
              <router-link to="/">
                <img src="../assets/logo.png" alt="logo" style="width: 100%; margin-left:0px;margin-top: 0px">
              </router-link>
            </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
name: "boldHeader"
}
</script>

<style scoped>
.root{
  background-image: url("../assets/background.svg");
  background-repeat: no-repeat;
}
.top{
  box-shadow: 0px 1px 2px 2px #f5f6f6;
}
.header{
  background: #ffffff;
  border: black;
}

</style>
