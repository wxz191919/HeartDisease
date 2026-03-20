<template>
    <div class="doctor-prediction">
      <h1>医生预测页面</h1>
      <p>在这里医生可以进行心脏病风险预测</p>
      
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <h2>心脏病风险预测</h2>
          </div>
        </template>
        
        <el-form :model="formData" label-width="120px">
          <el-form-item label="患者姓名">
            <el-input v-model="formData.patientName" placeholder="请输入患者姓名"></el-input>
          </el-form-item>
          
          <el-form-item label="年龄">
            <el-input-number v-model="formData.age" :min="1" :max="120"></el-input-number>
          </el-form-item>
          
          <el-form-item label="性别">
            <el-radio-group v-model="formData.gender">
              <el-radio :value="'male'">男</el-radio>
              <el-radio :value="'female'">女</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handlePredict">预测</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </template>
  
  <script>
  import { reactive } from 'vue'

  export default {
    name: "DoctorPrediction",
    setup() {
      const formData = reactive({
        patientName: '',
        age: 30,
        gender: 'male'
      })
      
      const handlePredict = () => {
        console.log('预测数据:', formData)
        // 这里添加预测逻辑
      }
      
      const resetForm = () => {
        formData.patientName = ''
        formData.age = 30
        formData.gender = 'male'
      }
      
      return {
        formData,
        handlePredict,
        resetForm
      }
    }
  }
  </script>

<style scoped>
.doctor-prediction {
  padding: 20px;
}

.box-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>