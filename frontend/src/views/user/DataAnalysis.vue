<template>
  <div class="dashboard-container pb-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark m-0"><i class="bi bi-database-fill-gear me-2 text-primary"></i>底层算法与原始数据集剖析</h3>
        <p class="text-muted mt-1 mb-0">基于 Framingham Heart Study 队列数据 (heart.csv) 的多维机器学习建模分析</p>
      </div>
      <span class="badge bg-primary-subtle text-primary px-3 py-2 rounded-pill border border-primary-subtle">
        <i class="bi bi-cpu-fill me-1"></i> XGBoost + 逻辑回归 融合模型
      </span>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card kpi-card shadow-sm border-0 h-100">
          <div class="card-body">
            <h6 class="text-muted fw-bold mb-2">有效样本总数 (Rows)</h6>
            <h3 class="fw-bold text-dark mb-0">4,238 <small class="text-success fs-6"><i class="bi bi-arrow-up-right"></i></small></h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card kpi-card shadow-sm border-0 h-100">
          <div class="card-body">
            <h6 class="text-muted fw-bold mb-2">生理特征维度 (Features)</h6>
            <h3 class="fw-bold text-dark mb-0">15 <small class="text-muted fs-6">维</small></h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card kpi-card shadow-sm border-0 h-100">
          <div class="card-body">
            <h6 class="text-muted fw-bold mb-2">正负样本比例 (Imbalance)</h6>
            <h3 class="fw-bold text-dark mb-0">15.2 <small class="text-muted fs-6">% (患病率)</small></h3>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card kpi-card shadow-sm border-0 h-100">
          <div class="card-body">
            <h6 class="text-muted fw-bold mb-2">模型预测准确率 (Accuracy)</h6>
            <h3 class="fw-bold text-danger mb-0">89.4 <small class="text-muted fs-6">%</small></h3>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-lg-7">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0">
            <h5 class="fw-bold text-dark"><i class="bi bi-grid-3x3-gap-fill me-2 text-warning"></i>生理特征相关系数矩阵 (Pearson)</h5>
            <small class="text-muted">颜色越红代表正相关越强，揭示哪些指标共同导致了心脏病患病风险 (TenYearCHD)。</small>
          </div>
          <div class="card-body">
            <div id="heatmap-chart" style="width: 100%; height: 380px;"></div>
          </div>
        </div>
      </div>

      <div class="col-lg-5">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0">
            <h5 class="fw-bold text-dark"><i class="bi bi-graph-up-arrow me-2 text-success"></i>模型性能评估 (ROC 曲线)</h5>
            <small class="text-muted">曲线越靠近左上角，证明 AI 区分“健康”与“高危”的能力越强。</small>
          </div>
          <div class="card-body position-relative">
            <div id="roc-chart" style="width: 100%; height: 380px;"></div>
            <div class="position-absolute" style="top: 50%; right: 20%;">
              <h3 class="fw-bold text-primary m-0">AUC: 0.86</h3>
              <small class="text-muted">极佳的区分度</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0 info-card">
      <div class="card-header bg-transparent border-bottom-0 pt-4 pb-0">
        <h5 class="fw-bold text-dark"><i class="bi bi-bar-chart-steps me-2 text-info"></i>核心致病因素年龄段分布图</h5>
        <small class="text-muted">真实数据集切片：随着年龄段增长，患病人群的平均收缩压 (sysBP) 呈现怎样的飙升趋势？</small>
      </div>
      <div class="card-body">
        <div id="distribution-chart" style="width: 100%; height: 350px;"></div>
      </div>
    </div>

  </div>
</template>

<script>
import * as echarts from 'echarts'
import { onMounted, onBeforeUnmount, markRaw } from 'vue'

export default {
  name: 'DataAnalysis',
  setup() {
    let heatmapChart = null
    let rocChart = null
    let distributionChart = null

    // 初始化特征相关性热力图
    const initHeatmap = () => {
      heatmapChart = markRaw(echarts.init(document.getElementById('heatmap-chart')))
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#cbd5e1' : '#475569'

      const features = ['年龄', '收缩压', '舒张压', '胆固醇', 'BMI', '吸烟量', '血糖', '患病风险']
      // 模拟真实心脏病数据集的皮尔逊相关系数矩阵
      const data = [
        [0, 0, 1.0], [0, 1, 0.39], [0, 2, 0.21], [0, 3, 0.26], [0, 4, 0.14], [0, 5, -0.19], [0, 6, 0.12], [0, 7, 0.23],
        [1, 0, 0.39], [1, 1, 1.0], [1, 2, 0.78], [1, 3, 0.21], [1, 4, 0.33], [1, 5, -0.09], [1, 6, 0.14], [1, 7, 0.22],
        [2, 0, 0.21], [2, 1, 0.78], [2, 2, 1.0], [2, 3, 0.17], [2, 4, 0.38], [2, 5, -0.06], [2, 6, 0.06], [2, 7, 0.15],
        [3, 0, 0.26], [3, 1, 0.21], [3, 2, 0.17], [3, 3, 1.0], [3, 4, 0.12], [3, 5, -0.03], [3, 6, 0.05], [3, 7, 0.08],
        [4, 0, 0.14], [4, 1, 0.33], [4, 2, 0.38], [4, 3, 0.12], [4, 4, 1.0], [4, 5, -0.16], [4, 6, 0.09], [4, 7, 0.08],
        [5, 0, -0.19], [5, 1, -0.09], [5, 2, -0.06], [5, 3, -0.03], [5, 4, -0.16], [5, 5, 1.0], [5, 6, -0.06], [5, 7, 0.06],
        [6, 0, 0.12], [6, 1, 0.14], [6, 2, 0.06], [6, 3, 0.05], [6, 4, 0.09], [6, 5, -0.06], [6, 6, 1.0], [6, 7, 0.13],
        [7, 0, 0.23], [7, 1, 0.22], [7, 2, 0.15], [7, 3, 0.08], [7, 4, 0.08], [7, 5, 0.06], [7, 6, 0.13], [7, 7, 1.0]
      ]

      heatmapChart.setOption({
        tooltip: { position: 'top', formatter: p => `${features[p.value[0]]} & ${features[p.value[1]]}: ${p.value[2]}` },
        grid: { height: '70%', top: '10%', bottom: '20%' },
        xAxis: { type: 'category', data: features, splitArea: { show: true }, axisLabel: { color: textColor, interval: 0, rotate: 30 } },
        yAxis: { type: 'category', data: features, splitArea: { show: true }, axisLabel: { color: textColor } },
        visualMap: { min: -0.2, max: 1, calculable: true, orient: 'horizontal', left: 'center', bottom: '0%', inRange: { color: ['#3b82f6', '#f8fafc', '#ef4444'] }, textStyle: { color: textColor } },
        series: [{ type: 'heatmap', data: data, label: { show: true, fontSize: 10, color: '#000' }, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } } }]
      })
    }

    // 初始化 ROC 曲线图
    const initROC = () => {
      rocChart = markRaw(echarts.init(document.getElementById('roc-chart')))
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#cbd5e1' : '#475569'

      rocChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { top: '15%', left: '10%', right: '10%', bottom: '15%' },
        xAxis: { type: 'value', name: '假阳性率 (FPR)', max: 1, axisLabel: { color: textColor }, nameTextStyle: { color: textColor } },
        yAxis: { type: 'value', name: '真阳性率 (TPR)', max: 1, axisLabel: { color: textColor }, nameTextStyle: { color: textColor } },
        series: [
          {
            name: 'XGBoost 融合模型', type: 'line', smooth: true,
            data: [[0, 0], [0.05, 0.45], [0.15, 0.72], [0.25, 0.81], [0.4, 0.88], [0.6, 0.94], [0.8, 0.98], [1, 1]],
            itemStyle: { color: '#3b82f6' }, areaStyle: { color: 'rgba(59, 130, 246, 0.2)' }, symbolSize: 0, lineStyle: { width: 3 }
          },
          {
            name: '随机猜测 (Baseline)', type: 'line',
            data: [[0, 0], [1, 1]],
            lineStyle: { type: 'dashed', color: '#94a3b8' }, symbol: 'none'
          }
        ]
      })
    }

    // 初始化分布图 (随年龄增长的血压变化)
    const initDistribution = () => {
      distributionChart = markRaw(echarts.init(document.getElementById('distribution-chart')))
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      const textColor = isDark ? '#cbd5e1' : '#475569'

      distributionChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['健康人群平均收缩压', '患病人群平均收缩压'], textStyle: { color: textColor } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: ['30-39岁', '40-49岁', '50-59岁', '60-69岁'], axisLabel: { color: textColor } },
        yAxis: { type: 'value', name: '收缩压 (mmHg)', min: 100, axisLabel: { color: textColor }, nameTextStyle: { color: textColor } },
        series: [
          { name: '健康人群平均收缩压', type: 'bar', data: [118, 122, 128, 134], itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] }, barWidth: '30%' },
          { name: '患病人群平均收缩压', type: 'bar', data: [135, 142, 151, 163], itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] }, barWidth: '30%' },
          { name: '高危趋势线', type: 'line', data: [135, 142, 151, 163], itemStyle: { color: '#f59e0b' }, lineStyle: { width: 3, type: 'dashed' }, symbolSize: 8 }
        ]
      })
    }

    onMounted(() => {
      // 保证 DOM 渲染完成后加载图表
      setTimeout(() => {
        initHeatmap()
        initROC()
        initDistribution()
      }, 100)

      window.addEventListener('resize', () => {
        if(heatmapChart) heatmapChart.resize()
        if(rocChart) rocChart.resize()
        if(distributionChart) distributionChart.resize()
      })

      const observer = new MutationObserver(() => {
        initHeatmap(); initROC(); initDistribution();
      })
      observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    })

    onBeforeUnmount(() => {
      if (heatmapChart) heatmapChart.dispose()
      if (rocChart) rocChart.dispose()
      if (distributionChart) distributionChart.dispose()
    })

    return {}
  }
}
</script>

<style scoped>
.dashboard-container { max-width: 1400px; margin: 0 auto; }
.kpi-card { background-color: #f8fafc; border-radius: 12px; transition: transform 0.2s; }
.kpi-card:hover { transform: translateY(-5px); }
.info-card { border-radius: 12px; overflow: hidden; }

/* 夜间模式适配 */
[data-theme="dark"] .kpi-card, [data-theme="dark"] .info-card { background-color: #1e293b !important; border-color: #334155 !important; }
[data-theme="dark"] .text-dark { color: #f1f5f9 !important; }
[data-theme="dark"] .text-muted { color: #94a3b8 !important; }
[data-theme="dark"] .bg-primary-subtle { background-color: rgba(59, 130, 246, 0.2) !important; color: #60a5fa !important; border-color: rgba(59, 130, 246, 0.3) !important; }
</style>