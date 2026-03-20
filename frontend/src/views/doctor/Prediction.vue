<template>
  <div class="prediction-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>心脏病风险预测</h2>
          <el-tag v-if="apiStatus" type="success" effect="dark">
            <i class="bi bi-check-circle me-1"></i>预测服务已连接
          </el-tag>
          <el-tag v-else type="danger" effect="dark">
            <i class="bi bi-exclamation-triangle me-1"></i>预测服务未连接
          </el-tag>
        </div>
      </template>

      <div v-if="!apiStatus" class="alert alert-danger mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        无法连接到预测服务，请确保机器学习API服务器已启动（端口5003）。
      </div>

      <div v-else class="alert alert-info mb-4">
        <i class="bi bi-info-circle me-2"></i>
        请填写以下信息进行心脏病风险预测。所有带 * 的字段为必填项。
      </div>

      <el-form 
        ref="predictionForm" 
        :model="formData" 
        :rules="rules" 
        label-width="120px"
        label-position="left"
        class="prediction-form"
        :disabled="!apiStatus"
      >
        <!-- 患者信息 -->
        <h4 class="section-title">患者信息</h4>
        <div class="form-section">
          <el-form-item label="患者姓名" prop="patientName">
            <el-input v-model="formData.patientName" placeholder="请输入患者姓名" />
          </el-form-item>
        </div>
        
        <!-- 基本信息 -->
        <h4 class="section-title">基本信息</h4>
        <div class="form-section">
          <el-form-item label="性别" prop="male">
            <el-radio-group v-model="formData.male">
              <el-radio :value="1">男</el-radio>
              <el-radio :value="0">女</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="年龄" prop="age">
            <el-input-number v-model="formData.age" :min="18" :max="120" />
          </el-form-item>
          
          <el-form-item label="教育水平" prop="education">
            <el-select v-model="formData.education" placeholder="请选择教育水平">
              <el-option :value="1" label="小学及以下" />
              <el-option :value="2" label="初中" />
              <el-option :value="3" label="高中/中专" />
              <el-option :value="4" label="大学/大专" />
              <el-option :value="5" label="研究生及以上" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="BMI指数" prop="BMI">
            <el-input-number v-model="formData.BMI" :precision="1" :step="0.1" :min="10" :max="50" />
          </el-form-item>
        </div>
        
        <!-- 生活习惯 -->
        <h4 class="section-title">生活习惯</h4>
        <div class="form-section">
          <el-form-item label="当前是否吸烟" prop="currentSmoker">
            <el-radio-group v-model="formData.currentSmoker">
              <el-radio :value="0">否</el-radio>
              <el-radio :value="1">是</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="每天吸烟数量" prop="cigsPerDay">
            <el-input-number v-model="formData.cigsPerDay" :min="0" :max="100" />
          </el-form-item>
          
          <el-form-item label="是否服用降压药" prop="BPMeds">
            <el-radio-group v-model="formData.BPMeds">
              <el-radio :value="0">否</el-radio>
              <el-radio :value="1">是</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>
        
        <!-- 健康状况 -->
        <h4 class="section-title">健康状况</h4>
        <div class="form-section">
          <el-form-item label="高血压" prop="prevalentHyp">
            <el-radio-group v-model="formData.prevalentHyp">
              <el-radio :value="0">否</el-radio>
              <el-radio :value="1">是</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="糖尿病" prop="diabetes">
            <el-radio-group v-model="formData.diabetes">
              <el-radio :value="0">否</el-radio>
              <el-radio :value="1">是</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="中风史" prop="prevalentStroke">
            <el-radio-group v-model="formData.prevalentStroke">
              <el-radio :value="0">否</el-radio>
              <el-radio :value="1">是</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>
        
        <!-- 健康指标 -->
        <h4 class="section-title">健康指标</h4>
        <div class="form-section">
          <el-form-item label="总胆固醇 (mg/dL)" prop="totChol">
            <el-input-number v-model="formData.totChol" :min="100" :max="500" />
          </el-form-item>
          
          <el-form-item label="收缩压 (mmHg)" prop="sysBP">
            <el-input-number v-model="formData.sysBP" :min="70" :max="250" />
          </el-form-item>
          
          <el-form-item label="舒张压 (mmHg)" prop="diaBP">
            <el-input-number v-model="formData.diaBP" :min="40" :max="150" />
          </el-form-item>
          
          <el-form-item label="心率 (bpm)" prop="heartRate">
            <el-input-number v-model="formData.heartRate" :min="40" :max="200" />
          </el-form-item>
          
          <el-form-item label="血糖 (mg/dL)" prop="glucose">
            <el-input-number v-model="formData.glucose" :min="50" :max="500" />
          </el-form-item>
        </div>
        
        <!-- 按钮区域 -->
        <div class="form-actions">
          <el-button type="primary" @click="submitForm" :loading="loading" :disabled="!apiStatus">
            <i class="bi bi-heart-pulse me-1"></i>进行预测
          </el-button>
          <el-button @click="resetForm" :disabled="loading || !apiStatus">
            <i class="bi bi-arrow-counterclockwise me-1"></i>重置表单
          </el-button>
          <el-button type="info" @click="loadSampleData" :disabled="loading || !apiStatus">
            <i class="bi bi-database-fill me-1"></i>加载样例数据
          </el-button>
        </div>
      </el-form>

      <!-- 预测结果区域 -->
      <div v-if="predictionResult" class="prediction-result mt-4">
        <h4 class="section-title">预测结果</h4>
        <div class="result-card" :class="resultClass">
          <div class="result-icon">
            <i class="bi" :class="resultIcon"></i>
          </div>
          <div class="result-content">
            <h5 class="result-title">{{ resultTitle }}</h5>
            <p class="result-probability">
              风险概率: <strong>{{ formatProbability(predictionResult.probability) }}</strong>
            </p>
            <p class="result-note">{{ resultNote }}</p>
            <div class="result-actions">
              <el-button type="primary" @click="viewDetail" v-if="savedPredictionId">
                查看详细分析
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="alert alert-danger mt-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        {{ errorMessage }}
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { useRouter } from 'vue-router'
import predictionService from '@/services/predictionService'
import axios from 'axios'
import API_BASE_URL from '../../config.js'

export default {
  name: 'Prediction-doctor',
  setup() {
    // 路由
    const router = useRouter()
    
    // 表单引用
    const predictionForm = ref(null)
    
    // API状态
    const apiStatus = ref(false)
    const loading = ref(false)
    const predictionResult = ref(null)
    const errorMessage = ref('')
    const sampleInput = ref(null)
    const savedPredictionId = ref(null)

    // 表单数据
    const formData = reactive({
      patientName: '',
      male: 1,
      age: 50,
      education: 2,
      currentSmoker: 0,
      cigsPerDay: 0,
      BPMeds: 0,
      prevalentHyp: 0,
      diabetes: 0,
      prevalentStroke: 0,
      BMI: 25,
      totChol: 200,
      sysBP: 120,
      diaBP: 80,
      heartRate: 70,
      glucose: 90
    })

    // 表单验证规则
    const rules = {
      patientName: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
      age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
      BMI: [{ required: true, message: '请输入BMI指数', trigger: 'blur' }],
      totChol: [{ required: true, message: '请输入总胆固醇', trigger: 'blur' }],
      sysBP: [{ required: true, message: '请输入收缩压', trigger: 'blur' }],
      diaBP: [{ required: true, message: '请输入舒张压', trigger: 'blur' }],
      heartRate: [{ required: true, message: '请输入心率', trigger: 'blur' }],
      glucose: [{ required: true, message: '请输入血糖', trigger: 'blur' }],
      cigsPerDay: [{ required: true, message: '请输入每天吸烟数量', trigger: 'blur' }]
    }

    // 结果样式计算属性
    const resultClass = computed(() => {
      if (!predictionResult.value) return ''
      
      const probability = predictionResult.value.probability
      if (probability >= 0.7) return 'high-risk'
      if (probability >= 0.3) return 'medium-risk'
      return 'low-risk'
    })

    // 结果图标计算属性
    const resultIcon = computed(() => {
      if (!predictionResult.value) return ''
      
      const probability = predictionResult.value.probability
      if (probability >= 0.7) return 'bi-exclamation-triangle-fill'
      if (probability >= 0.3) return 'bi-exclamation-circle-fill'
      return 'bi-check-circle-fill'
    })

    // 结果标题计算属性
    const resultTitle = computed(() => {
      if (!predictionResult.value) return ''
      
      return predictionResult.value.risk_level || '未知风险'
    })

    // 结果注释计算属性
    const resultNote = computed(() => {
      if (!predictionResult.value) return ''
      
      const probability = predictionResult.value.probability
      if (probability >= 0.7) {
        return '您的心脏病风险较高，建议尽快就医并进行详细检查。'
      } else if (probability >= 0.3) {
        return '您的心脏病风险中等，建议定期体检并保持健康的生活方式。'
      } else {
        return '您的心脏病风险较低，请继续保持健康的生活习惯。'
      }
    })

    // 格式化概率值，确保它是有效数字
    const formatProbability = (probability) => {
      if (probability === undefined || probability === null || isNaN(probability)) {
        return '0.00%'
      }
      return `${(parseFloat(probability) * 100).toFixed(2)}%`
    }

    // 检查API状态
    const checkApiStatus = async () => {
      try {
        await predictionService.healthCheck()
        apiStatus.value = true
        errorMessage.value = ''
      } catch (error) {
        console.error('API连接失败:', error)
        apiStatus.value = false
        errorMessage.value = '无法连接到预测服务，请确保机器学习API服务器已启动（端口5003）。'
      }
    }

    // 加载样例数据
    const loadSampleData = async () => {
      if (!apiStatus.value) {
        ElMessage.warning('API服务未连接，无法加载样例数据')
        return
      }

      try {
        loading.value = true
        if (!sampleInput.value) {
          sampleInput.value = await predictionService.getSampleInput()
        }
        
        // 将样例数据填充到表单
        Object.keys(sampleInput.value).forEach(key => {
          if (key in formData) {
            formData[key] = sampleInput.value[key]
          }
        })
        
        // 设置示例患者姓名
        formData.patientName = '测试患者'
        
        ElMessage.success('样例数据已加载')
      } catch (error) {
        console.error('加载样例数据失败:', error)
        errorMessage.value = '加载样例数据失败: ' + error.message
      } finally {
        loading.value = false
      }
    }

    // 保存预测结果到数据库
    const savePredictionToDatabase = async (result) => {
      try {
        // 准备要保存的数据
        const predictionData = {
          patientName: formData.patientName,
          probability: result.probability,
          riskLevel: result.risk_level,
          result: `10年内患心脏病${result.risk_level}`,
          features: { ...formData }
        }
        
        console.log('正在保存预测结果到数据库:', predictionData)
        
        // 发送请求保存数据
        const response = await axios.post(`${API_BASE_URL}/predictions`, predictionData)
        
        console.log('保存预测结果成功:', response.data)
        
        // 保存成功后获取ID
        savedPredictionId.value = response.data.id
        
        return response.data.id
      } catch (error) {
        console.error('保存预测结果失败:', error)
        console.error('错误详情:', error.response ? error.response.data : '无响应数据')
        ElMessage.warning(`预测结果保存失败: ${error.response ? error.response.data.error || error.response.data.message : error.message}`)
        return null
      }
    }

    // 查看详情
    const viewDetail = () => {
      if (savedPredictionId.value) {
        router.push(`/doctor/prediction-detail/${savedPredictionId.value}`)
      }
    }

    // 提交表单
    const submitForm = async () => {
      if (!apiStatus.value) {
        ElMessage.warning('API服务未连接，无法进行预测')
        return
      }

      if (!predictionForm.value) return
      
      predictionForm.value.validate(async (valid) => {
        if (valid) {
          try {
            loading.value = true
            errorMessage.value = ''
            savedPredictionId.value = null
            
            // 创建加载指示器
            const loadingInstance = ElLoading.service({
              lock: true,
              text: '正在进行预测...',
              background: 'rgba(0, 0, 0, 0.7)'
            })
            
            // 发送预测请求
            const result = await predictionService.predict(formData)
            
            // 确保概率值是有效数字
            if (result.probability === undefined || result.probability === null || isNaN(result.probability)) {
              result.probability = 0
              console.warn('API返回的概率值无效，已设置为默认值0')
            }
            
            predictionResult.value = result
            
            // 保存预测结果到数据库
            await savePredictionToDatabase(result)
            
            // 关闭加载指示器
            loadingInstance.close()
            
            // 显示成功消息
            ElMessage.success('预测完成')
            
            // 滚动到结果区域
            setTimeout(() => {
              const resultElement = document.querySelector('.prediction-result')
              if (resultElement) {
                resultElement.scrollIntoView({ behavior: 'smooth' })
              }
            }, 100)
          } catch (error) {
            console.error('预测失败:', error)
            errorMessage.value = '预测失败: ' + error.message
            ElMessage.error('预测失败: ' + error.message)
          } finally {
            loading.value = false
          }
        } else {
          ElMessage.warning('请填写所有必填字段')
          return false
        }
      })
    }

    // 重置表单
    const resetForm = () => {
      if (predictionForm.value) {
        predictionForm.value.resetFields()
        predictionResult.value = null
        errorMessage.value = ''
        savedPredictionId.value = null
      }
    }

    // 组件挂载时检查API状态
    onMounted(async () => {
      await checkApiStatus()
      
      // 如果API可用，尝试获取特征信息
      if (apiStatus.value) {
        try {
          await predictionService.getFeatures()
        } catch (error) {
          console.error('获取特征信息失败:', error)
        }
      }
    })

    return {
      predictionForm,
      formData,
      rules,
      loading,
      apiStatus,
      predictionResult,
      errorMessage,
      resultClass,
      resultIcon,
      resultTitle,
      resultNote,
      savedPredictionId,
      submitForm,
      resetForm,
      loadSampleData,
      formatProbability,
      viewDetail
    }
  }
}
</script>
<style scoped>
/* 全屏动态背景 */
.page-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  min-height: 100vh;
  background: linear-gradient(-45deg, #e8f4f8, #f0f8fb, #f5fafe, #e0f7fa);
  background-size: 400% 400%;
  animation: bgMove 12s ease infinite;
  z-index: -1;
}

@keyframes bgMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 原有内容样式 */
.prediction-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
  z-index: 1;
}

.box-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  margin-top: 30px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin-top: 20px;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
  color: #409EFF;
}

.form-section {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 30px;
}

.prediction-result {
  background-color: rgba(249, 249, 249, 0.9);
  border-radius: 8px;
  padding: 20px;
  margin-top: 30px;
}

.result-card {
  display: flex;
  border-radius: 8px;
  padding: 20px;
  color: white;
}

.low-risk {
  background-color: #67C23A;
}

.medium-risk {
  background-color: #E6A23C;
}

.high-risk {
  background-color: #F56C6C;
}

.result-icon {
  font-size: 2.5rem;
  margin-right: 20px;
  display: flex;
  align-items: center;
}

.result-content {
  flex: 1;
}

.result-title {
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.result-probability {
  font-size: 1.1rem;
  margin-bottom: 10px;
}

.result-note {
  font-style: italic;
  margin-bottom: 15px;
}

.result-actions {
  margin-top: 15px;
}
</style>