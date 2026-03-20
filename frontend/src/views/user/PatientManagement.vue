<template>
  <div class="doctor-prediction-container modern-ui pb-5">

    <div class="tech-header shadow-sm mb-4">
      <div class="pulse-ring"></div>
      <div class="header-text">
        <h2 class="m-0 fw-bold title-gradient"><i class="el-icon-s-data"></i> 临床心血管风险预测系统</h2>
        <p class="text-muted m-0 mt-2">基于本地 XGBoost 机器学习模型的患病风险精准测算</p>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="18">
        <el-card class="box-card shadow-sm border-0 form-card" body-style="padding: 30px;">
          <el-form
            ref="predictionForm"
            :model="formData"
            :rules="rules"
            label-position="top"
            class="prediction-form"
          >
            <div class="section-container">
              <h4 class="section-title"><i class="el-icon-user-solid text-primary"></i> 核心患者档案</h4>
              <div class="form-grid">
                <el-form-item label="患者姓名" prop="patientName">
                  <el-input v-model="formData.patientName" placeholder="录入患者姓名" prefix-icon="el-icon-user" />
                </el-form-item>
                <el-form-item label="选择现有患者库">
                  <el-select v-model="selectedPatient" filterable placeholder="快速调取档案" @change="handlePatientSelect" style="width: 100%;">
                    <el-option v-for="item in patientsList" :key="item.id" :label="item.name" :value="item.id">
                      <span style="float: left">{{ item.name }}</span>
                      <span style="float: right; color: #8492a6; font-size: 13px">{{ item.gender === 'male' ? '男' : '女' }} | {{ item.age }}岁</span>
                    </el-option>
                  </el-select>
                </el-form-item>
              </div>
            </div>

            <div class="section-container">
              <h4 class="section-title"><i class="el-icon-info text-success"></i> 基础体征</h4>
              <div class="form-grid">
                <el-form-item label="生理性别" prop="male">
                  <el-radio-group v-model="formData.male" class="custom-radio">
                    <el-radio :label="1" border>男性</el-radio>
                    <el-radio :label="0" border>女性</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="年龄 (岁)" prop="age">
                  <el-input-number v-model="formData.age" :min="18" :max="120" style="width: 100%;"></el-input-number>
                </el-form-item>
                <el-form-item label="身体质量指数 (BMI)" prop="BMI">
                  <el-input-number v-model="formData.BMI" :min="10" :max="50" :precision="1" :step="0.1" style="width: 100%;"></el-input-number>
                </el-form-item>
              </div>
            </div>

            <div class="section-container">
              <h4 class="section-title"><i class="el-icon-document-checked text-warning"></i> 既往病史与习惯</h4>
              <div class="form-grid">
                <el-form-item label="当前是否吸烟" prop="currentSmoker">
                  <el-radio-group v-model="formData.currentSmoker">
                    <el-radio :label="0" border>否</el-radio>
                    <el-radio :label="1" border>是</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="高血压病史" prop="prevalentHyp">
                  <el-radio-group v-model="formData.prevalentHyp">
                    <el-radio :label="0" border>无病史</el-radio>
                    <el-radio :label="1" border>有病史</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="糖尿病病史" prop="diabetes">
                  <el-radio-group v-model="formData.diabetes">
                    <el-radio :label="0" border>无病史</el-radio>
                    <el-radio :label="1" border>有病史</el-radio>
                  </el-radio-group>
                </el-form-item>
              </div>
            </div>

            <div class="section-container">
              <h4 class="section-title"><i class="el-icon-data-line text-danger"></i> 核心生化指标</h4>
              <div class="form-grid">
                <el-form-item label="总胆固醇 (mg/dL)" prop="totChol">
                  <el-input-number v-model="formData.totChol" :min="100" :max="500" style="width: 100%;"></el-input-number>
                </el-form-item>
                <el-form-item label="收缩压/高压 (mmHg)" prop="sysBP">
                  <el-input-number v-model="formData.sysBP" :min="70" :max="250" style="width: 100%;"></el-input-number>
                </el-form-item>
                <el-form-item label="舒张压/低压 (mmHg)" prop="diaBP">
                  <el-input-number v-model="formData.diaBP" :min="40" :max="150" style="width: 100%;"></el-input-number>
                </el-form-item>
                <el-form-item label="静息心率 (bpm)" prop="heartRate">
                  <el-input-number v-model="formData.heartRate" :min="40" :max="200" style="width: 100%;"></el-input-number>
                </el-form-item>
                <el-form-item label="空腹血糖 (mg/dL)" prop="glucose">
                  <el-input-number v-model="formData.glucose" :min="50" :max="500" style="width: 100%;"></el-input-number>
                </el-form-item>
              </div>
            </div>

            <div class="action-bar text-center mt-4">
              <el-button type="primary" size="large" @click="submitForm" :loading="loading" class="predict-btn mx-2 glow-btn" round>
                <i class="el-icon-data-line"></i> 运行风险预测算法
              </el-button>
              <el-button size="large" @click="resetForm" :disabled="loading" class="mx-2" round>重置特征数据</el-button>
            </div>
          </el-form>
        </el-card>

        <transition name="fade-slide">
          <el-card v-if="predictionResult" class="box-card mt-4 result-card border-0 shadow-lg prediction-result">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <div class="result-icon-box" :style="{ background: predictionResult.probability >= 0.7 ? '#ef4444' : (predictionResult.probability >= 0.3 ? '#f59e0b' : '#10b981') }">
                  <i :class="predictionResult.probability >= 0.3 ? 'el-icon-warning' : 'el-icon-success'" class="text-white"></i>
                </div>
                <div class="ms-4" style="margin-left: 20px;">
                  <h3 class="m-0 mb-1 fw-bold">系统定级:
                    <span :style="{ color: predictionResult.probability >= 0.7 ? '#ef4444' : (predictionResult.probability >= 0.3 ? '#f59e0b' : '#10b981') }">
                      {{ resultTitle }}
                    </span>
                  </h3>
                  <p class="text-muted m-0 fs-6">
                    经本地模型测算，该患者患心血管疾病的风险概率为 <strong style="font-size: 1.2rem; color: #409eff;">{{ formatProbability(predictionResult.probability) }}</strong>。
                  </p>
                  <p class="m-0 mt-1" style="font-size: 0.9rem; color: #64748b;">{{ resultNote }}</p>
                </div>
              </div>
              <div v-if="savedPredictionId">
                <el-button type="primary" @click="viewDetail" size="medium" class="glow-btn" round>
                  查看详细临床分析 <i class="el-icon-arrow-right"></i>
                </el-button>
              </div>
            </div>
          </el-card>
        </transition>
      </el-col>

      <el-col :span="6">
        <el-card class="box-card border-0 shadow-sm tips-card h-100" body-style="padding: 0;">
          <div class="scanner-container">
            <div class="scanner-line"></div>
            <i class="el-icon-s-platform scanner-icon"></i>
            <div class="scanner-grid"></div>
          </div>
          <div class="p-4 bg-white">
            <h4 class="fw-bold text-primary mb-3"><i class="el-icon-aim"></i> 临床数据接入规范</h4>
            <ul class="tips-list text-muted">
              <li><i class="el-icon-circle-check text-success"></i> 录入前请确保患者处于静息状态</li>
              <li><i class="el-icon-circle-check text-success"></i> 血压需取连续两次测量的平均值</li>
              <li><i class="el-icon-circle-check text-success"></i> 胆固醇与血糖应为空腹抽血生化指标</li>
              <li><i class="el-icon-warning-outline text-warning"></i> 既往病史请严格结合病历本核查</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
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
  name: 'DoctorPrediction',
  setup() {
    const router = useRouter()

    const predictionForm = ref(null)
    const loading = ref(false)
    const predictionResult = ref(null)
    const savedPredictionId = ref(null)
    const patientsList = ref([])
    const selectedPatient = ref(null)

    const formData = reactive({
      patientName: '',
      male: 1,
      age: 50,
      BMI: 25,
      currentSmoker: 0,
      prevalentHyp: 0,
      diabetes: 0,
      totChol: 200,
      sysBP: 120,
      diaBP: 80,
      heartRate: 70,
      glucose: 90
    })

    const rules = {
      patientName: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
      age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
      BMI: [{ required: true, message: '请输入BMI指数', trigger: 'blur' }]
    }

    const fetchPatients = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/patients`)
        patientsList.value = response.data.patients || []
      } catch (error) {
        console.error('获取患者列表失败:', error)
      }
    }

    const handlePatientSelect = async (patientId) => {
      try {
        if (patientId) {
          const patient = patientsList.value.find(p => p.id === patientId)
          if (patient) {
            formData.patientName = patient.name
            formData.age = patient.age
            formData.male = patient.gender === 'male' ? 1 : 0
          }
        }
      } catch (error) {
        console.error('选择患者失败:', error)
      }
    }

    const resultClass = computed(() => {
      if (!predictionResult.value) return ''
      const probability = predictionResult.value.probability
      if (probability >= 0.7) return 'high-risk'
      if (probability >= 0.3) return 'medium-risk'
      return 'low-risk'
    })

    const resultIcon = computed(() => {
      if (!predictionResult.value) return ''
      const probability = predictionResult.value.probability
      if (probability >= 0.7) return 'bi-exclamation-triangle-fill'
      if (probability >= 0.3) return 'bi-exclamation-circle-fill'
      return 'bi-check-circle-fill'
    })

    const resultTitle = computed(() => {
      if (!predictionResult.value) return ''
      return predictionResult.value.risk_level || predictionResult.value.riskLevel || '未知风险'
    })

    const resultNote = computed(() => {
      if (!predictionResult.value) return ''
      const probability = predictionResult.value.probability
      if (probability >= 0.7) {
        return '患者心脏病风险较高，建议尽快安排进一步检查，针对风险因素进行干预治疗。'
      } else if (probability >= 0.3) {
        return '患者心脏病风险中等，建议定期随访监测，适当调整生活方式。'
      } else {
        return '患者心脏病风险较低，建议保持健康的生活习惯，定期体检。'
      }
    })

    const formatProbability = (probability) => {
      if (probability === undefined || probability === null || isNaN(probability)) {
        return '0.00%'
      }
      return `${(parseFloat(probability) * 100).toFixed(2)}%`
    }

    const savePredictionToDatabase = async (result) => {
      try {
        const predictionData = {
          patientName: formData.patientName,
          probability: result.probability,
          riskLevel: result.risk_level || result.riskLevel || resultTitle.value,
          result: result.risk_level || result.riskLevel || resultTitle.value,
          features: { ...formData }
        }

        const token = localStorage.getItem('token')
        const response = await axios.post(`${API_BASE_URL}/predictions`, predictionData, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        savedPredictionId.value = response.data.id || response.data.data?.id
        return savedPredictionId.value
      } catch (error) {
        console.error('保存预测结果失败:', error)
        ElMessage.warning('预测结果已生成，但存入数据库失败(未授权)')
        return null
      }
    }

    const viewDetail = () => {
      if (savedPredictionId.value) {
        router.push(`/doctor/prediction-detail/${savedPredictionId.value}`)
      }
    }

    const submitForm = async () => {
      if (!predictionForm.value) return

      predictionForm.value.validate(async (valid) => {
        if (valid) {
          try {
            loading.value = true
            savedPredictionId.value = null

            const loadingInstance = ElLoading.service({
              lock: true,
              text: '正在进行算法测算...',
              background: 'rgba(0, 0, 0, 0.7)'
            })

            const result = await predictionService.predict(formData)
            predictionResult.value = result

            await savePredictionToDatabase(result)

            loadingInstance.close()
            ElMessage.success('测算完成')

            setTimeout(() => {
              const resultElement = document.querySelector('.prediction-result')
              if (resultElement) {
                resultElement.scrollIntoView({ behavior: 'smooth' })
              }
            }, 100)
          } catch (error) {
            console.error('测算失败:', error)
            ElMessage.error('测算失败')
          } finally {
            loading.value = false
          }
        } else {
          ElMessage.warning('请填写所有必填字段')
          return false
        }
      })
    }

    const resetForm = () => {
      if (predictionForm.value) {
        predictionForm.value.resetFields()
        predictionResult.value = null
        savedPredictionId.value = null
        selectedPatient.value = null
      }
    }

    onMounted(async () => {
      await fetchPatients()
    })

    return {
      predictionForm,
      formData,
      rules,
      loading,
      predictionResult,
      resultClass,
      resultIcon,
      resultTitle,
      resultNote,
      savedPredictionId,
      patientsList,
      selectedPatient,
      submitForm,
      resetForm,
      formatProbability,
      viewDetail,
      handlePatientSelect
    }
  }
}
</script>

<style scoped>
/* 全局美化 */
.modern-ui {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  padding: 10px;
}

/* 动态科幻头部 */
.tech-header {
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  border-radius: 12px;
  padding: 25px 30px;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
  border-left: 6px solid #3b82f6;
}
.pulse-ring {
  width: 60px;
  height: 60px;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 50%;
  position: absolute;
  left: 30px;
  animation: pulse-ring-anim 2s infinite cubic-bezier(0.215, 0.61, 0.355, 1);
}
.pulse-ring::after {
  content: '';
  position: absolute;
  top: 15px; left: 15px; width: 30px; height: 30px;
  background: #3b82f6;
  border-radius: 50%;
}
@keyframes pulse-ring-anim {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(3.5); opacity: 0; }
}
.header-text {
  margin-left: 80px;
  z-index: 1;
}
.title-gradient {
  background: -webkit-linear-gradient(45deg, #1e40af, #7e22ce);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 表单内部分区 */
.form-card { border-radius: 14px; }
.section-container {
  margin-bottom: 25px;
  padding: 25px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}
.section-container:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-color: #cbd5e1;
}
.section-title {
  margin-top: 0;
  margin-bottom: 20px;
  color: #1e293b;
  font-weight: bold;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 12px;
}

/* 现代化 Grid 布局 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}
:deep(.el-form-item) { margin-bottom: 0; }
:deep(.el-form-item__label) { font-weight: 600; color: #475569; padding-bottom: 8px; }

/* 🚀 动态雷达扫描动画 */
.tips-card { border-radius: 14px; overflow: hidden; }
.scanner-container {
  height: 200px;
  background: #0f172a;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.scanner-grid {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-image:
    linear-gradient(rgba(56, 189, 248, 0.2) 1px, transparent 1px),
    linear-gradient(90deg, rgba(56, 189, 248, 0.2) 1px, transparent 1px);
  background-size: 20px 20px;
  z-index: 1;
}
.scanner-icon { font-size: 70px; color: #38bdf8; z-index: 3; text-shadow: 0 0 20px #38bdf8; }
.scanner-line {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 3px;
  background: #38bdf8;
  box-shadow: 0 0 20px 10px rgba(56, 189, 248, 0.4);
  animation: scan-anim 2.5s infinite linear;
  z-index: 2;
}
@keyframes scan-anim {
  0% { top: -10%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 110%; opacity: 0; }
}

.tips-list { padding-left: 0; list-style: none; }
.tips-list li { margin-bottom: 12px; line-height: 1.6; }

/* 预测结果弹层 */
.result-card {
  background: linear-gradient(120deg, #ffffff, #f0f9ff);
  border-left: 6px solid #3b82f6 !important;
  border-radius: 12px;
  padding: 10px;
}
.result-icon-box {
  width: 65px; height: 65px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 35px; color: white;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

/* 按钮发光特效 */
.glow-btn {
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
  transition: all 0.3s ease;
}
.glow-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

/* 出场动画 */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.fade-slide-enter-from { opacity: 0; transform: translateY(40px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-40px); }

.d-flex { display: flex; }
.justify-content-between { justify-content: space-between; }
.align-items-center { align-items: center; }
.mt-4 { margin-top: 1.5rem; }
.mx-2 { margin-left: 0.5rem; margin-right: 0.5rem; }
.mb-1 { margin-bottom: 0.25rem; }
.fw-bold { font-weight: bold; }
</style>