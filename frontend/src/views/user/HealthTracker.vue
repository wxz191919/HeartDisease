<template>
  <div class="dashboard-container pb-4" id="report-content">

    <div class="d-flex justify-content-between align-items-end mb-4 print-header">
      <div>
        <h3 class="fw-bold text-dark m-0">
          <i class="bi bi-activity me-2 text-danger"></i>个人健康趋势与干预报告
        </h3>
        <p class="text-muted mt-1 mb-0">当前查看患者: <span class="text-primary fw-bold fs-5">{{ targetPatient }}</span> | 记录周期: 近期预测趋势动态分析</p>
      </div>

      <div class="d-flex align-items-center no-print">
        <div class="input-group me-3 shadow-sm" style="width: 260px;">
          <input type="text" class="form-control border-primary" placeholder="输入患者姓名查询..." v-model="searchQuery" @keyup.enter="handleSearch">
          <button class="btn btn-primary" type="button" @click="handleSearch">
            <i class="bi bi-search"></i> 查询
          </button>
        </div>

        <button class="btn btn-outline-primary fw-bold px-3 py-2 shadow-sm" @click="exportPDF" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-file-earmark-pdf-fill me-1"></i>导出
        </button>
      </div>
    </div>

    <div class="print-only mb-4 text-center border-bottom pb-3">
      <h2>Cardio-AI 心脏病风险动态评估报告</h2>
      <p class="text-muted">生成时间: {{ currentDate }} | 报告归属: {{ targetPatient }}</p>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="text-muted mt-2">正在从数据库抓取患者【{{ targetPatient }}】的记录...</p>
    </div>

    <div v-else-if="!hasData" class="alert alert-warning text-center py-5 border-0 shadow-sm">
      <i class="bi bi-search fs-1 text-warning mb-2 d-block"></i>
      <h5 class="fw-bold text-dark">暂无患者【{{ targetPatient }}】的趋势数据</h5>
      <p class="text-muted mb-0">数据库中未找到该姓名的预测记录。请检查姓名是否拼写正确，或先去进行预测。</p>
      <router-link to="/user/diagnose" class="btn btn-primary mt-4 rounded-pill px-4">去为 {{ targetPatient }} 进行预测</router-link>
    </div>

    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-md-3 col-6">
          <div class="card stat-card shadow-sm border-0 h-100 bg-primary-subtle">
            <div class="card-body">
              <h6 class="text-primary fw-bold mb-2"><i class="bi bi-droplet-half me-1"></i>最新收缩压</h6>
              <h3 class="fw-bold text-dark mb-0">{{ latestData.sysBP }} <small class="text-muted fs-6">mmHg</small></h3>
              <span :class="['badge mt-2', latestData.sysBP > 140 ? 'bg-danger' : 'bg-success']">
                {{ latestData.sysBP > 140 ? '偏高警戒' : '血压正常' }}
              </span>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="card stat-card shadow-sm border-0 h-100 bg-success-subtle">
            <div class="card-body">
              <h6 class="text-success fw-bold mb-2"><i class="bi bi-heart-pulse me-1"></i>最新总胆固醇</h6>
              <h3 class="fw-bold text-dark mb-0">{{ latestData.totChol }} <small class="text-muted fs-6">mg/dL</small></h3>
              <span :class="['badge mt-2', latestData.totChol > 240 ? 'bg-danger text-white' : 'bg-success']">
                {{ latestData.totChol > 240 ? '偏高警戒' : '指标正常' }}
              </span>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="card stat-card shadow-sm border-0 h-100 bg-warning-subtle">
            <div class="card-body">
              <h6 class="text-warning-emphasis fw-bold mb-2"><i class="bi bi-person-standing me-1"></i>最新 BMI</h6>
              <h3 class="fw-bold text-dark mb-0">{{ latestData.bmi }} <small class="text-muted fs-6"></small></h3>
              <span :class="['badge mt-2', latestData.bmi > 25 ? 'bg-warning text-dark' : 'bg-success']">
                {{ latestData.bmi > 25 ? '超重需减脂' : '体态健康' }}
              </span>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="card stat-card shadow-sm border-0 h-100 bg-danger-subtle">
            <div class="card-body">
              <h6 class="text-danger fw-bold mb-2"><i class="bi bi-exclamation-triangle-fill me-1"></i>综合发病风险</h6>
              <h3 class="fw-bold text-dark mb-0">{{ latestData.risk }} <small class="text-muted fs-6">%</small></h3>
              <span :class="['badge mt-2', latestData.risk > 20 ? 'bg-danger' : 'bg-success']">
                {{ latestData.risk > 20 ? '高危预警' : '风险可控' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="card shadow-sm mb-4 border-0 info-card chart-container">
        <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0">
          <h5 class="fw-bold text-dark"><i class="bi bi-graph-up text-danger me-2"></i>历史血压监控动态曲线 (sysBP / diaBP)</h5>
        </div>
        <div class="card-body">
          <div id="bp-chart" style="width: 100%; height: 320px;"></div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="card shadow-sm h-100 border-0 info-card chart-container">
            <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0">
              <h5 class="fw-bold text-dark"><i class="bi bi-egg-fried text-warning me-2"></i>总胆固醇演变趋势 (totChol)</h5>
            </div>
            <div class="card-body">
              <div id="chol-chart" style="width: 100%; height: 280px;"></div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card shadow-sm h-100 border-0 info-card chart-container">
            <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0">
              <h5 class="fw-bold text-dark"><i class="bi bi-shield-check text-success me-2"></i>AI 风险评估指数演变</h5>
            </div>
            <div class="card-body">
              <div id="risk-chart" style="width: 100%; height: 280px;"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card shadow-sm border-0 info-card mt-2">
        <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0">
          <h5 class="fw-bold text-dark"><i class="bi bi-clipboard2-check-fill text-primary me-2"></i>AI 智能干预总结</h5>
        </div>
        <div class="card-body">
          <ul class="text-muted fs-6" style="line-height: 1.8;">
            <li><strong>最新指标总评：</strong> 患者 {{ targetPatient }} 最近一次的预测心血管风险率为 <strong>{{ latestData.risk }}%</strong>。{{ latestData.risk > 20 ? '风险处于较高水平，必须引起重视。' : '目前风险处于安全范围内，请继续保持良好的生活习惯。' }}</li>
            <li><strong>核心异常追踪：</strong> 最新收缩压为 {{ latestData.sysBP }} mmHg，胆固醇为 {{ latestData.totChol }} mg/dL。{{ latestData.sysBP > 140 ? '血压超出正常水平，请减少钠盐摄入并关注血压变化。' : '' }}</li>
            <li><strong>系统提示：</strong> 本报告数据仅供临床参考。</li>
          </ul>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import * as echarts from 'echarts'
import { onMounted, onBeforeUnmount, markRaw, ref, nextTick } from 'vue'
import axios from 'axios'
import API_BASE_URL from '../../config.js'

export default {
  name: 'HealthTracker',
  setup() {
    const loading = ref(true)
    const hasData = ref(false)
    const targetPatient = ref('') // 当前正在查看的患者姓名
    const searchQuery = ref('')   // 搜索框里输入的内容
    const currentDate = ref(new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }))

    const chartData = ref({ dates: [], sysBP: [], diaBP: [], chol: [], risk: [] })
    const latestData = ref({ sysBP: 0, diaBP: 0, totChol: 0, bmi: 0, risk: 0 })

    let bpChart = null; let cholChart = null; let riskChart = null;

    // 🚀 核心逻辑：传入你要查的患者姓名
    const fetchRealHistoryData = async (patientName) => {
      try {
        loading.value = true
        hasData.value = false

        // 从后端拉取数据
        const response = await axios.get(`${API_BASE_URL}/predictions?per_page=100`)
        let allRecords = response.data.items || response.data || []

        // 🚀 重点：只留下【填写的患者姓名】完全匹配的数据！
        let records = allRecords.filter(item => item.patientName === patientName)

        if (!records || records.length === 0) {
          loading.value = false
          return
        }

        // 按时间排序
        records = records.sort((a, b) => new Date(a.predictionTime) - new Date(b.predictionTime))
        const recentRecords = records.slice(-10)

        // 🚀 每次查询前，清空旧数据，防止张三的数据和李四的混在一起
        chartData.value = { dates: [], sysBP: [], diaBP: [], chol: [], risk: [] }

        // 解析并填充图表数据
        recentRecords.forEach(item => {
          const d = new Date(item.predictionTime)
          chartData.value.dates.push(`${d.getMonth() + 1}月${d.getDate()}日 ${d.getHours()}:${d.getMinutes()}`)

          const features = item.features || {}
          chartData.value.sysBP.push(features.sysBP || 120)
          chartData.value.diaBP.push(features.diaBP || 80)
          chartData.value.chol.push(features.totChol || 180)

          let riskVal = item.probability || 0
          if (riskVal < 1) riskVal = (riskVal * 100).toFixed(1)
          chartData.value.risk.push(parseFloat(riskVal))
        })

        const last = recentRecords[recentRecords.length - 1]
        const lastFeatures = last.features || {}

        latestData.value = {
          sysBP: lastFeatures.sysBP || 0,
          diaBP: lastFeatures.diaBP || 0,
          totChol: lastFeatures.totChol || 0,
          bmi: lastFeatures.BMI || lastFeatures.bmi || 0,
          risk: chartData.value.risk[chartData.value.risk.length - 1] || 0
        }

        hasData.value = true
        loading.value = false

        await nextTick()
        renderAllCharts()

      } catch (error) {
        console.error('请求真实历史数据失败:', error)
        hasData.value = false
        loading.value = false
      }
    }

    // 🚀 搜索按钮的点击事件
    const handleSearch = () => {
      const name = searchQuery.value.trim()
      if (name) {
        targetPatient.value = name
        fetchRealHistoryData(name)
      }
    }

    const renderAllCharts = () => {
      // 重绘画图前，必须把老图表销毁掉
      if (bpChart) { bpChart.dispose() }
      if (cholChart) { cholChart.dispose() }
      if (riskChart) { riskChart.dispose() }

      initBPChart()
      initCholChart()
      initRiskChart()
    }

    const initBPChart = () => {
      if(!document.getElementById('bp-chart')) return;
      bpChart = markRaw(echarts.init(document.getElementById('bp-chart')))
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#cbd5e1' : '#475569'

      bpChart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['收缩压 (高压)', '舒张压 (低压)'], textStyle: { color: textColor } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: chartData.value.dates, axisLabel: { color: textColor } },
        yAxis: { type: 'value', min: 'dataMin', axisLabel: { color: textColor } },
        series: [
          {
            name: '收缩压 (高压)', type: 'line', smooth: true, data: chartData.value.sysBP,
            itemStyle: { color: '#ef4444' }, lineStyle: { width: 3 },
            markArea: { itemStyle: { color: 'rgba(239, 68, 68, 0.1)' }, data: [[{ name: '高血压警戒线', yAxis: 140 }, { yAxis: 200 }]] }
          },
          { name: '舒张压 (低压)', type: 'line', smooth: true, data: chartData.value.diaBP, itemStyle: { color: '#3b82f6' }, lineStyle: { width: 3 } }
        ]
      })
    }

    const initCholChart = () => {
      if(!document.getElementById('chol-chart')) return;
      cholChart = markRaw(echarts.init(document.getElementById('chol-chart')))
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#cbd5e1' : '#475569'

      cholChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: chartData.value.dates, axisLabel: { color: textColor } },
        yAxis: { type: 'value', min: 'dataMin', axisLabel: { color: textColor } },
        series: [
          {
            name: '总胆固醇', type: 'line', smooth: true, data: chartData.value.chol,
            itemStyle: { color: '#f59e0b' }, areaStyle: { color: 'rgba(245, 158, 11, 0.2)' }, lineStyle: { width: 3 },
            markLine: { data: [{ name: '安全标准线', yAxis: 200, lineStyle: { color: '#10b981', type: 'dashed' } }] }
          }
        ]
      })
    }

    const initRiskChart = () => {
      if(!document.getElementById('risk-chart')) return;
      riskChart = markRaw(echarts.init(document.getElementById('risk-chart')))
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#cbd5e1' : '#475569'

      riskChart.setOption({
        tooltip: { trigger: 'axis', formatter: '{b} <br/> 综合发病风险: {c}%' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: chartData.value.dates, axisLabel: { color: textColor } },
        yAxis: { type: 'value', min: 0, max: 100, axisLabel: { color: textColor } },
        series: [
          {
            type: 'bar', data: chartData.value.risk,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#ec4899' }, { offset: 1, color: '#8b5cf6' }]),
              borderRadius: [4, 4, 0, 0]
            }, barWidth: '40%'
          }
        ]
      })
    }

    const exportPDF = () => {
      window.print()
    }

    onMounted(() => {
      // 页面刚加载时，默认取当前登录的账号名作为初始查询
      const user = JSON.parse(localStorage.getItem('user')) || {}
      targetPatient.value = user.username || '当前用户'
      searchQuery.value = targetPatient.value

      // 触发第一次查询
      fetchRealHistoryData(targetPatient.value)

      window.addEventListener('resize', () => {
        if(bpChart) bpChart.resize()
        if(cholChart) cholChart.resize()
        if(riskChart) riskChart.resize()
      })

      const observer = new MutationObserver(() => {
        if(hasData.value) renderAllCharts();
      })
      observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    })

    onBeforeUnmount(() => {
      if (bpChart) bpChart.dispose()
      if (cholChart) cholChart.dispose()
      if (riskChart) riskChart.dispose()
    })

    return { loading, hasData, targetPatient, searchQuery, handleSearch, exportPDF, currentDate, latestData }
  }
}
</script>

<style scoped>
.dashboard-container { max-width: 1200px; margin: 0 auto; }
.stat-card { border-radius: 12px; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-5px); }
.info-card { border-radius: 12px; overflow: hidden; }
.print-only { display: none; }

/* 搜索框美化 */
.input-group .form-control:focus { box-shadow: none; border-color: #0d6efd; }
.input-group .btn { z-index: 0; }

[data-theme="dark"] .stat-card, [data-theme="dark"] .info-card { background-color: #1e293b !important; border-color: #334155 !important; }
[data-theme="dark"] .text-dark { color: #f1f5f9 !important; }
[data-theme="dark"] .text-muted { color: #94a3b8 !important; }
[data-theme="dark"] .bg-primary-subtle { background-color: rgba(59, 130, 246, 0.2) !important; color: #60a5fa !important; }
[data-theme="dark"] .bg-success-subtle { background-color: rgba(34, 197, 94, 0.2) !important; color: #4ade80 !important; }
[data-theme="dark"] .bg-warning-subtle { background-color: rgba(245, 158, 11, 0.2) !important; color: #fbbf24 !important; }
[data-theme="dark"] .bg-danger-subtle { background-color: rgba(239, 68, 68, 0.2) !important; color: #f87171 !important; }

@media print {
  .no-print, .top-navbar, .sidebar, .theme-btn { display: none !important; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  .print-only { display: block !important; }
  .dashboard-container { max-width: 100% !important; margin: 0 !important; padding: 0 !important; }
  .shadow-sm { box-shadow: none !important; border: 1px solid #e2e8f0 !important; }
  .chart-container { page-break-inside: avoid; }
}
</style>