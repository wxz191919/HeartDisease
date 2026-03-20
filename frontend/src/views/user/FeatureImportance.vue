<template>
  <div class="feature-importance-container pb-4">
    <div class="d-flex justify-content-between align-items-end mb-4 header-area">
      <div>
        <h3 class="fw-bold text-dark m-0">
          <i class="el-icon-cpu text-primary mr-2"></i>模型特征重要性分析 (SHAP Values)
        </h3>
        <p class="text-muted mt-2 mb-0">
          基于机器学习算法的全局可解释性分析，展示影响心脏病发病风险的核心驱动因素。
        </p>
      </div>
      <el-button type="primary" icon="el-icon-refresh" @click="refreshData" :loading="loading" round>
        重新运行特征评估
      </el-button>
    </div>

    <el-row :gutter="20" class="mb-4">
      <el-col :span="16">
        <el-card class="box-card shadow-sm border-0 h-100" body-style="padding: 20px;">
          <template #header>
            <div class="card-header d-flex justify-content-between align-items-center">
              <span class="fw-bold"><i class="el-icon-data-analysis text-warning mr-2"></i>全局特征重要性排名 (Top 10)</span>
              <el-tag size="small" type="success" effect="plain">XGBoost 模型</el-tag>
            </div>
          </template>
          <div v-loading="loading" class="chart-wrapper">
            <div ref="featureImportanceChart" class="chart"></div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="box-card shadow-sm border-0 h-100 insight-card">
          <template #header>
            <div class="card-header">
              <span class="fw-bold"><i class="el-icon-magic-stick text-purple mr-2"></i>AI 智能洞察</span>
            </div>
          </template>
          <div class="insight-content">
            <div class="insight-item mb-4">
              <h5 class="text-danger fw-bold">1. 最关键风险因子</h5>
              <p class="text-muted fs-6">
                模型表明，<strong>年龄 (Age)</strong> 和 <strong>收缩压 (sysBP)</strong> 是预测心脏病风险最具决定性的两个因素。对于这两项指标异常的患者，应优先进行干预。
              </p>
            </div>
            <div class="insight-item mb-4">
              <h5 class="text-warning fw-bold">2. 生活习惯的影响</h5>
              <p class="text-muted fs-6">
                <strong>每日吸烟量 (cigsPerDay)</strong> 作为可控的生活习惯因素，其重要性排名第三。这为医生提供了明确的临床干预方向：强烈建议患者戒烟。
              </p>
            </div>
            <div class="insight-item">
              <h5 class="text-primary fw-bold">3. 血糖与胆固醇的协同</h5>
              <p class="text-muted fs-6">
                虽然单一的空腹血糖 (glucose) 排名居中，但当它与高总胆固醇 (totChol) 并存时，模型给出的风险权重会呈指数级上升。
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="box-card shadow-sm border-0">
      <template #header>
        <div class="card-header">
          <span class="fw-bold"><i class="el-icon-document text-success mr-2"></i>特征数据字典与权重明细</span>
        </div>
      </template>
      <el-table
        v-loading="loading"
        :data="featureImportanceData"
        style="width: 100%"
        :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight:'bold'}"
        border
        stripe
        hover
      >
        <el-table-column type="index" label="排名" width="80" align="center">
          <template #default="scope">
            <span :class="{'top-rank': scope.$index < 3}" class="rank-badge">{{ scope.$index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="feature" label="特征字段 (Feature)" width="150" align="center">
          <template #default="scope">
            <code class="feature-code">{{ scope.row.feature }}</code>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="数据分类" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getCategoryTag(scope.row.category)" effect="light" size="medium">
              {{ scope.row.category }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="医学描述 (Description)" min-width="250"></el-table-column>

        <el-table-column prop="importance" label="相对重要性贡献 (SHAP Score)" width="350">
          <template #default="scope">
            <div class="d-flex align-items-center">
              <span class="mr-3 fw-bold" style="width: 40px;">{{ (scope.row.importance * 100).toFixed(1) }}%</span>
              <el-progress
                :percentage="scope.row.importance * 100"
                :color="getProgressColor(scope.row.importance)"
                :show-text="false"
                :stroke-width="12"
                style="flex: 1;"
              ></el-progress>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { markRaw } from 'vue';
import axios from 'axios'; // 🚀 引入 axios 用于请求后端接口
import API_BASE_URL from '../../config.js'

export default {
  name: 'FeatureImportance',
  data() {
    return {
      featureImportanceData: [],
      loading: false,
      error: null,
      chartInstance: null
    };
  },
  mounted() {
    this.fetchData();
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    if (this.chartInstance) {
      this.chartInstance.dispose();
    }
  },
  methods: {
    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    },
    async fetchData() {
      this.loading = true;
      this.error = null;

      // 🚀 给冰冷的模型英文特征，穿上好看的中文外套
      const featureMeta = {
        'age': { description: '患者年龄 (岁)', category: '基础信息' },
        'sysBP': { description: '收缩压/高压 (mmHg)', category: '生理指标' },
        'cigsPerDay': { description: '每日吸烟量 (支)', category: '生活习惯' },
        'diaBP': { description: '舒张压/低压 (mmHg)', category: '生理指标' },
        'totChol': { description: '总胆固醇水平 (mg/dL)', category: '生化指标' },
        'glucose': { description: '空腹血糖水平 (mg/dL)', category: '生化指标' },
        'BMI': { description: '身体质量指数', category: '基础信息' },
        'heartRate': { description: '静息心率 (次/分)', category: '生理指标' },
        'male': { description: '性别 (1=男; 0=女)', category: '基础信息' },
        'diabetes': { description: '是否有糖尿病病史 (1=是; 0=否)', category: '疾病史' }
      };

      try {
        const token = localStorage.getItem('token');

        // 🚀 调用真实的后端接口获取特征重要性
        const response = await axios.get(`${API_BASE_URL}/predictions/importance`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        const rawData = response.data.data || [];

        if (rawData.length === 0) {
          throw new Error('模型未返回有效特征数据');
        }

        // 把后端的真实分数和前端的中文翻译完美结合
        this.featureImportanceData = rawData.map(item => {
          const meta = featureMeta[item.feature] || { description: '未知特征', category: '其他' };
          return {
            feature: item.feature,
            importance: item.importance,
            description: meta.description,
            category: meta.category
          };
        });

        this.$nextTick(() => {
          this.initChart();
        });

      } catch (err) {
        console.error('获取特征重要性数据失败:', err);
        this.error = '无法连接到 AI 模型接口，或模型尚未就绪。';
        this.$message && this.$message.error(this.error);
      } finally {
        this.loading = false;
      }
    },
    refreshData() {
      if (this.chartInstance) {
        this.chartInstance.clear();
      }
      this.fetchData();
    },
    initChart() {
      const chartDom = this.$refs.featureImportanceChart;
      if (!chartDom) return;

      this.chartInstance = markRaw(echarts.init(chartDom));

      const sortedData = [...this.featureImportanceData].sort((a, b) => a.importance - b.importance);
      const yAxisData = sortedData.map(item => item.feature);
      const seriesData = sortedData.map(item => item.importance * 100);

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: function (params) {
            let data = params[0];
            return `<div style="padding: 5px;">
                      <div style="font-weight:bold;margin-bottom:5px;">${data.name}</div>
                      重要性贡献: <span style="color:#0d6efd;font-weight:bold;">${data.value.toFixed(2)}%</span>
                    </div>`;
          }
        },
        grid: {
          left: '3%',
          right: '8%',
          bottom: '3%',
          top: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '重要性 (%)',
          splitLine: { lineStyle: { type: 'dashed', color: '#e2e8f0' } },
          axisLabel: { color: '#64748b' }
        },
        yAxis: {
          type: 'category',
          data: yAxisData,
          axisLabel: { fontWeight: 'bold', color: '#334155' },
          axisTick: { show: false },
          axisLine: { lineStyle: { color: '#cbd5e1' } }
        },
        series: [
          {
            name: '重要性',
            type: 'bar',
            data: seriesData,
            barWidth: '50%',
            showBackground: true,
            backgroundStyle: { color: 'rgba(180, 180, 180, 0.05)', borderRadius: [0, 4, 4, 0] },
            itemStyle: {
              borderRadius: [0, 4, 4, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#3b82f6' },
                { offset: 1, color: '#8b5cf6' }
              ])
            },
            label: {
              show: true,
              position: 'right',
              formatter: '{c}%',
              color: '#64748b',
              fontWeight: 'bold'
            }
          }
        ]
      };

      this.chartInstance.setOption(option);
    },
    getProgressColor(importance) {
      if (importance >= 0.20) return '#ef4444';
      if (importance >= 0.10) return '#f59e0b';
      if (importance >= 0.05) return '#3b82f6';
      return '#94a3b8';
    },
    getCategoryTag(category) {
      const map = {
        '基础信息': 'info',
        '生理指标': 'danger',
        '生化指标': 'warning',
        '生活习惯': 'success',
        '疾病史': 'primary'
      };
      return map[category] || 'info';
    }
  }
};
</script>

<style scoped>
.feature-importance-container {
  padding: 24px;
  background-color: #f8fafc;
  min-height: calc(100vh - 60px);
}

.header-area {
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 16px;
}

.text-purple {
  color: #8b5cf6;
}

.box-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.box-card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
}

.chart-wrapper {
  width: 100%;
  height: 420px;
}

.chart {
  width: 100%;
  height: 100%;
}

.insight-card .insight-content {
  padding: 10px 5px;
}
.insight-item h5 {
  margin-bottom: 8px;
  font-size: 1.05rem;
}
.insight-item p {
  line-height: 1.6;
}

.rank-badge {
  display: inline-block;
  width: 24px;
  height: 24px;
  line-height: 24px;
  background-color: #e2e8f0;
  color: #475569;
  border-radius: 50%;
  font-weight: bold;
}
.rank-badge.top-rank {
  background-color: #fee2e2;
  color: #ef4444;
}

.feature-code {
  background-color: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
  color: #0f172a;
  font-weight: 600;
  font-family: 'Courier New', Courier, monospace;
}

.d-flex { display: flex; }
.justify-content-between { justify-content: space-between; }
.align-items-center { align-items: center; }
.align-items-end { align-items: flex-end; }
.mb-4 { margin-bottom: 1.5rem; }
.mt-2 { margin-top: 0.5rem; }
.m-0 { margin: 0; }
.mr-2 { margin-right: 0.5rem; }
.mr-3 { margin-right: 1rem; }
.fw-bold { font-weight: 700; }
.text-muted { color: #6c757d; }
.text-primary { color: #0d6efd; }
.text-danger { color: #dc3545; }
.text-warning { color: #ffc107; }
.text-success { color: #198754; }
.fs-6 { font-size: 1rem; }
.shadow-sm { box-shadow: 0 .125rem .25rem rgba(0,0,0,.075) !important; }
.border-0 { border: 0 !important; }
.h-100 { height: 100% !important; }
</style>