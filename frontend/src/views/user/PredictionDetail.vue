<template>
  <div class="doctor-prediction-detail" v-loading="pageLoading">

    <el-card class="mb-4 shadow-sm" v-if="prediction.patientName">
      <template #header>
        <div class="card-header d-flex justify-content-between align-items-center">
          <h3 class="m-0"><i class="el-icon-user-solid text-primary"></i> 患者：{{ prediction.patientName }} 的评估报告</h3>
          <el-tag :type="riskLevelTagType" effect="dark" size="medium">{{ prediction.riskLevel }}</el-tag>
        </div>
      </template>
      <div class="real-data-row text-center">
        <div class="data-item">
          <h5 class="text-muted">患病概率</h5>
          <h1 :class="riskLevelTagType === 'danger' ? 'text-danger' : 'text-primary'">
            {{ prediction.probability }}%
          </h1>
        </div>
        <div class="data-item">
          <h5 class="text-muted">预测时间</h5>
          <h4>{{ prediction.predictionTime }}</h4>
        </div>
        <div class="data-item">
          <h5 class="text-muted">评估系统</h5>
          <h4>Cardio-AI V2.0</h4>
        </div>
      </div>
    </el-card>

    <el-card class="mb-4 shadow-sm ai-card" v-if="prediction.patientName">
      <template #header>
        <div class="card-header d-flex justify-content-between align-items-center">
          <h3 class="m-0 ai-title">
            <i class="el-icon-cpu"></i> DeepSeek 智能靶向诊断专家
          </h3>
          <el-button type="primary" size="small" icon="el-icon-refresh" @click="fetchDeepSeekAnalysis" :loading="dsLoading" round>
            重新生成深度分析
          </el-button>
        </div>
      </template>

      <div class="ai-report-container" v-loading="dsLoading" element-loading-text="DeepSeek 正在结合患者指标进行特异化深度思考中..." element-loading-spinner="el-icon-loading">
        <div v-if="dsReport" class="ai-report-content" v-html="formattedDsReport"></div>
        <div v-else-if="!dsLoading" class="text-center text-muted py-4">
          等待 AI 引擎响应...
        </div>
      </div>
    </el-card>

    <div class="notice-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3><i class="el-icon-warning"></i> 心脏病通用注意事项</h3>
          </div>
        </template>
        <div class="notice-content">
          <el-alert title="紧急情况处理" type="error" show-icon>
            <ul>
              <li>如出现<strong>持续胸痛、呼吸困难、晕厥</strong>等症状，请立即拨打急救电话</li>
              <li>随身携带硝酸甘油等急救药物</li>
              <li>告知家人您的病情和药物存放位置</li>
            </ul>
          </el-alert>

          <el-collapse v-model="activeNotices" class="mt-3">
            <el-collapse-item title="日常注意事项" name="daily">
              <ul class="notice-list">
                <li>定期监测血压、血糖和血脂水平</li>
                <li>遵医嘱按时服药，不可擅自停药</li>
                <li>保持适度运动，避免剧烈活动</li>
                <li>戒烟限酒，避免二手烟</li>
                <li>控制情绪，避免过度激动</li>
                <li>保证充足睡眠，避免熬夜</li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="复诊提醒" name="checkup">
              <ul class="notice-list">
                <li>每3个月复查心电图和心肌酶谱</li>
                <li>每半年进行一次全面的心血管系统检查</li>
                <li>如有不适，随时就诊</li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="饮食建议" name="diet">
              <div class="diet-advice">
                <p>1. 采用<strong>地中海饮食</strong>模式，多蔬菜水果和全谷物</p>
                <p>2. 每日盐摄入量控制在<strong>5g以下</strong></p>
                <p>3. 少量多餐，避免暴饮暴食</p>
                <p>4. 烹饪方式以蒸、煮、炖为主，避免煎炸</p>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import API_BASE_URL from '../../config.js'

export default {
  name: 'DoctorPredictionDetail',
  data() {
    return {
      activeNotices: ['daily', 'checkup'],
      pageLoading: true,
      prediction: {
        patientName: '',
        riskLevel: '未知',
        probability: 0,
        predictionTime: ''
      },
      // 新增存储患者具体生理指标的对象
      features: {},
      // DeepSeek 专属状态
      dsLoading: false,
      dsReport: ''
    }
  },
  computed: {
    riskLevelTagType() {
      const map = {
        '低风险': 'success',
        '中风险': 'warning',
        '高风险': 'danger'
      }
      return map[this.prediction.riskLevel] || 'info'
    },
    // 将 AI 返回的换行符转为 HTML 换行，并高亮部分医学警示词
    formattedDsReport() {
      if (!this.dsReport) return ''
      let text = this.dsReport.replace(/\n/g, '<br/>')
      // 用正则给危险词汇飘红加粗
      text = text.replace(/(异常|高风险|罪魁祸首|高危|立刻|必须|严禁|超标)/g, '<strong style="color: #F56C6C;">$1</strong>')
      // 给建议性词汇加蓝加粗
      text = text.replace(/(建议|控制在|饮食|干预处方|指标深度剖析)/g, '<strong style="color: #409EFF;">$1</strong>')
      return text
    }
  },
  async mounted() {
    // 1. 抓取刚刚跳转过来时，URL上带的真实数据库ID
    const predictionId = this.$route.params.id
    if (!predictionId) {
      this.pageLoading = false
      return
    }

    try {
      // 2. 带着Token去敲后端的门，要真实的预测数据
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/predictions/${predictionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      const data = response.data

      // 3. 把从MySQL拿到的真数据，塞给页面显示
      this.prediction = {
        patientName: data.patientName || data.patient_name || '未知患者',
        riskLevel: data.riskLevel || data.risk_level || '未知',
        probability: data.probability < 1 ? (data.probability * 100).toFixed(1) : parseFloat(data.probability).toFixed(1),
        predictionTime: data.predictionTime ? data.predictionTime.replace('T', ' ').substring(0, 16) : new Date().toLocaleString()
      }

      // 🚀 4. 提取打包在 features 里的血压、胆固醇等具体生理数据
      if (typeof data.features === 'string') {
        try {
          this.features = JSON.parse(data.features)
        } catch(e) {
          this.features = {}
        }
      } else {
        this.features = data.features || {}
      }

      // 🚀 5. 基础数据加载完毕后，立刻召唤 DeepSeek！
      this.fetchDeepSeekAnalysis()

    } catch (error) {
      console.error('获取真实预测详情失败:', error)
      this.$message && this.$message.error('读取数据库详情失败')
    } finally {
      this.pageLoading = false
    }
  },
  methods: {
    // 🚀 核心：纯前端直连 DeepSeek，执行严苛的特异化分析！
    async fetchDeepSeekAnalysis() {
      this.dsLoading = true
      this.dsReport = ''

      try {
        // 第一步：把患者的所有特征字典，翻译成能让大模型看懂的中文病历
        const metricsMap = {
          age: '年龄', sysBP: '收缩压', diaBP: '舒张压', totChol: '总胆固醇',
          glucose: '空腹血糖', bmi: 'BMI指数', BMI: 'BMI指数', heartRate: '静息心率',
          cigsPerDay: '日吸烟量', male: '性别(1男0女)', diabetes: '糖尿病史(1有0无)'
        }

        let metricsText = ''
        for (const [key, val] of Object.entries(this.features)) {
          const cnName = metricsMap[key] || key
          metricsText += `- ${cnName}: ${val}\n`
        }

        // 第二步：编写极度严苛的专家级 Prompt，逼迫 DeepSeek 进行特异化分析
        const prompt = `你现在是一位资深心血管内科专家。请根据以下患者的全面体征数据，进行【一对一特异化】的深度分析报告，绝不能使用通用套话！

患者姓名：${this.prediction.patientName}
AI预测心血管患病风险率：${this.prediction.probability}% (${this.prediction.riskLevel})

【患者具体生理指标】：
${metricsText}

请严格按照以下3个部分输出报告（直接输出正文，不要有任何多余问候语）：
### 1. 异常指标深度剖析
（必须逐一分析上述指标中偏离正常范围的项，说明其对该患者心血管的单独及协同危害。正常的指标一笔带过，异常的指标必须重点点名！）

### 2. 核心风险归因
（结合高达/低至 ${this.prediction.probability}% 的风险率，指出导致该患者风险的最主要1-2个“罪魁祸首”）

### 3. 特异化干预处方
（必须针对上述的具体异常指标，给出数值化的建议。例如不能只说“注意血压”，必须说“鉴于收缩压高达XXX，需将其控制在130以下”。对吸烟、高胆固醇等提供精准干预方案）`

        // 第三步：直接调用官方 API (复用你已有的 key)
        const apiKey = 'sk-513768d242da4afdbbdee96ec7a6da59'

        const response = await fetch('https://api.deepseek.com/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            model: 'deepseek-chat',
            messages: [
              { role: 'system', content: '你是一个专业、严谨的心血管AI专家诊断系统。' },
              { role: 'user', content: prompt }
            ],
            temperature: 0.7
          })
        })

        if (!response.ok) {
          throw new Error('网络请求异常，状态码: ' + response.status)
        }

        const data = await response.json()

        // 渲染 DeepSeek 呕心沥血写出来的特异化报告
        this.dsReport = data.choices[0].message.content

      } catch (error) {
        console.error('DeepSeek 请求失败:', error)
        // 报错绝对不手软，直接显示错误原因！
        this.dsReport = `<div style="background-color: #fef0f0; border: 1px solid #fde2e2; color: #f56c6c; padding: 15px; border-radius: 4px;">
          <strong><i class="el-icon-error"></i> AI 诊断生成失败</strong><br/><br/>
          未能成功连接到 DeepSeek 官方接口。请检查网络状态或 API 余额。<br/>
          详细报错：${error.message}
        </div>`
      } finally {
        this.dsLoading = false
      }
    }
  }
}
</script>

<style scoped>
.doctor-prediction-detail {
  padding: 20px;
}
.card-header {
  margin-bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mb-4 {
  margin-bottom: 20px;
}
.mt-3 {
  margin-top: 15px;
}
.real-data-row {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}
.data-item h1, .data-item h4 {
  margin-top: 10px;
  font-weight: bold;
}
.notice-list li {
  line-height: 2;
  color: #555;
}
.diet-advice p {
  margin-bottom: 8px;
  color: #555;
}

/* AI 卡片专属样式 */
.ai-card {
  border: 1px solid #c6e2ff;
}
.ai-title {
  color: #409EFF;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ai-report-container {
  min-height: 200px;
  padding: 10px;
}
.ai-report-content {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
}
.text-danger {
  color: #F56C6C;
}
.text-primary {
  color: #409EFF;
}
</style>