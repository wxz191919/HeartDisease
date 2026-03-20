<template>
  <div class="doctor-prediction-detail" v-loading="pageLoading">

    <el-card class="mb-4 shadow-sm" v-if="prediction.patientName">
      <template #header>
        <div class="card-header d-flex justify-content-between align-items-center">
          <h3 class="m-0"><i class="el-icon-user-solid text-primary"></i> 患者：{{ prediction.patientName }} 临床风险评估</h3>
          <div>
            <el-tag :type="riskLevelTagType" effect="dark" size="medium" class="mr-2">{{ prediction.riskLevel }}</el-tag>
            <el-button size="small" icon="el-icon-back" @click="$router.back()" plain>返回列表</el-button>
          </div>
        </div>
      </template>
      <div class="real-data-row text-center">
        <div class="data-item">
          <h5 class="text-muted">模型推演高危概率</h5>
          <h1 :class="riskLevelTagType === 'danger' ? 'text-danger' : 'text-primary'">
            {{ prediction.probability }}%
          </h1>
        </div>
        <div class="data-item">
          <h5 class="text-muted">评估生成时间</h5>
          <h4>{{ prediction.predictionTime }}</h4>
        </div>
        <div class="data-item">
          <h5 class="text-muted">驱动引擎</h5>
          <h4>Cardio-AI v2.0 & DeepSeek V3</h4>
        </div>
      </div>
    </el-card>

    <el-card class="mb-4 shadow-sm ai-card" v-if="prediction.patientName">
      <template #header>
        <div class="card-header d-flex justify-content-between align-items-center">
          <h3 class="m-0 ai-title">
            <i class="el-icon-cpu"></i> DeepSeek 临床辅助诊断报告
          </h3>
          <el-button type="primary" size="small" icon="el-icon-refresh" @click="fetchDeepSeekAnalysis" :loading="dsLoading" round>
            重新生成靶向分析
          </el-button>
        </div>
      </template>

      <div class="ai-report-container" v-loading="dsLoading" element-loading-text="DeepSeek 正在结合患者指标进行特异化深度思考中..." element-loading-spinner="el-icon-loading">
        <div v-if="dsReport" class="ai-report-content" v-html="formattedDsReport"></div>
        <div v-else-if="!dsLoading" class="text-center text-muted py-5">
          等待 AI 引擎响应...
        </div>
      </div>
    </el-card>

    <div class="notice-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <h3><i class="el-icon-warning"></i> 临床常规干预指南</h3>
          </div>
        </template>
        <div class="notice-content">
          <el-alert title="高危紧急情况处理" type="error" show-icon>
            <ul>
              <li>如出现<strong>持续胸痛、呼吸困难、晕厥</strong>等症状，请立即启动院内急救预案。</li>
              <li>开具硝酸甘油等急救药物处方。</li>
            </ul>
          </el-alert>

          <el-collapse v-model="activeNotices" class="mt-3">
            <el-collapse-item title="日常医嘱建议" name="daily">
              <ul class="notice-list">
                <li>叮嘱患者定期监测血压、血糖和血脂水平</li>
                <li>处方药物需按时服用，强调不可擅自停药的风险</li>
                <li>建议适度运动，但严禁近期进行剧烈活动</li>
                <li>强制要求戒烟限酒，远离二手烟</li>
              </ul>
            </el-collapse-item>
            <el-collapse-item title="复诊排期提醒" name="checkup">
              <ul class="notice-list">
                <li>每 3 个月复查心电图和心肌酶谱</li>
                <li>每半年进行一次全面的心血管系统影像学检查</li>
              </ul>
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
      // 存储患者具体生理指标
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
      text = text.replace(/(异常|高风险|罪魁祸首|高危|立刻|必须|严禁|超标|恶化)/g, '<strong style="color: #F56C6C;">$1</strong>')
      // 给建议性词汇加蓝加粗
      text = text.replace(/(建议|控制在|医嘱|处方|靶向|临床剖析)/g, '<strong style="color: #409EFF;">$1</strong>')
      return text
    }
  },
  async mounted() {
    // 1. 抓取URL上的真实数据库ID
    const predictionId = this.$route.params.id
    if (!predictionId) {
      this.pageLoading = false
      return
    }

    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${API_BASE_URL}/predictions/${predictionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      const data = response.data

      this.prediction = {
        patientName: data.patientName || data.patient_name || '未知患者',
        riskLevel: data.riskLevel || data.risk_level || '未知',
        probability: data.probability < 1 ? (data.probability * 100).toFixed(1) : parseFloat(data.probability).toFixed(1),
        predictionTime: data.predictionTime ? data.predictionTime.replace('T', ' ').substring(0, 16) : new Date().toLocaleString()
      }

      // 提取特征
      if (typeof data.features === 'string') {
        try { this.features = JSON.parse(data.features) } catch(e) { this.features = {} }
      } else {
        this.features = data.features || {}
      }

      // 基础数据加载完毕后，立刻召唤 DeepSeek！
      this.fetchDeepSeekAnalysis()

    } catch (error) {
      console.error('获取真实预测详情失败:', error)
      this.$message && this.$message.error('读取数据库详情失败')
    } finally {
      this.pageLoading = false
    }
  },
  methods: {
    // 🚀 核心：纯前端直连 DeepSeek，专为医生定制的特异化分析
    async fetchDeepSeekAnalysis() {
      this.dsLoading = true
      this.dsReport = ''

      try {
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

        // 🚀 医生版专属强化 Prompt
        const prompt = `作为心血管临床AI辅助诊断系统，请为主治医生生成针对该患者的【特异化临床分析报告】。绝不能使用通用套话！

患者姓名：${this.prediction.patientName}
AI预测高危概率：${this.prediction.probability}% (${this.prediction.riskLevel})

【患者临床体征数据】：
${metricsText}

请按以下3个维度输出临床报告（Markdown排版）：
### 1. 异常指标临床剖析
（逐一精读偏离正常值的指标，向医生提示其单独及协同致病风险。正常指标忽略，异常指标重点预警）

### 2. 核心病理归因
（结合高达/低至 ${this.prediction.probability}% 的风险率，指出引发高危的最核心因素）

### 3. 靶向医疗干预处方
（为医生提供明确的数值化医疗干预建议，例如降压靶标、用药建议方向、生活干预细则）`

        // 🚀 复用你的真实 Key，直接敲门
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

        // 渲染 DeepSeek 给医生的报告
        this.dsReport = data.choices[0].message.content

      } catch (error) {
        console.error('DeepSeek 请求失败:', error)
        this.dsReport = `<div style="background-color: #fef0f0; border: 1px solid #fde2e2; color: #f56c6c; padding: 15px; border-radius: 4px;">
          <strong><i class="el-icon-error"></i> AI 临床诊断生成失败</strong><br/><br/>
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
  padding: 10px 15px;
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
.mr-2 {
  margin-right: 10px;
}
</style>