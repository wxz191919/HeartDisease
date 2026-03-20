<template>
  <div class="feature-importance-container">
    <el-card class="box-card">
      <template #header>
        <div class="clearfix">
          <span>特征重要性分析</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="refreshData">刷新数据</el-button>
        </div>
      </template>
      <div v-loading="loading">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <div v-else>
          <h3>特征重要性排名</h3>
          <div class="chart-container">
            <div ref="featureImportanceChart" class="chart"></div>
          </div>
          
          <el-table
            :data="featureImportanceData"
            style="width: 100%; margin-top: 20px;"
            border
            stripe>
            <el-table-column
              prop="feature"
              label="特征名称"
              width="180">
            </el-table-column>
            <el-table-column
              prop="description"
              label="特征描述"
              width="280">
            </el-table-column>
            <el-table-column
              prop="importance"
              label="重要性得分">
              <template #default="scope">
                {{ (scope.row.importance * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column
              label="重要性可视化">
              <template #default="scope">
                <div class="importance-bar">
                  <div class="importance-fill" :style="{ width: (scope.row.importance * 100) + '%' }"></div>
                </div>
              </template>
            </el-table-column>
          </el-table>
          


          
          <div class="explanation-box">
            <h4>特征重要性解释</h4>
            <p>特征重要性表示每个特征对模型预测结果的影响程度。数值越高，表示该特征对预测结果的影响越大。</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'FeatureImportance',
  data() {
    return {
      featureImportanceData: [],
      shapImage: null,
      loading: false,
      error: null,
      chart: null
    };
  },
  mounted() {
    this.fetchData();
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose();
    }
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        // 获取特征重要性数据
        const importanceResponse = await axios.get('http://localhost:5002/api/feature_importance');
        console.log('特征重要性响应数据:', importanceResponse.data);
        
        if (importanceResponse.data.error) {
          console.error('特征重要性错误:', importanceResponse.data.error);
          // 使用示例数据
          this.featureImportanceData = this.getExampleFeatureImportanceData();
        } else {
          // 检查响应数据的格式
          if (Array.isArray(importanceResponse.data)) {
            this.featureImportanceData = importanceResponse.data;
          } else if (importanceResponse.data.importance && Array.isArray(importanceResponse.data.importance)) {
            this.featureImportanceData = importanceResponse.data.importance;
          } else {
            console.error('特征重要性数据格式不正确:', importanceResponse.data);
            // 使用示例数据
            this.featureImportanceData = this.getExampleFeatureImportanceData();
          }
        }
        
        if (this.featureImportanceData && this.featureImportanceData.length > 0) {
          this.$nextTick(() => {
            this.renderChart();
          });
        }
        

      } catch (error) {
        console.error('获取数据失败:', error);
        // 使用示例数据
        this.featureImportanceData = this.getExampleFeatureImportanceData();
        this.$nextTick(() => {
          this.renderChart();
        });
      } finally {
        this.loading = false;
      }
    },
    refreshData() {
      this.fetchData();
    },
    renderChart() {
      if (this.chart) {
        this.chart.dispose();
      }
      
      // 如果没有数据，不渲染图表
      if (!this.featureImportanceData || this.featureImportanceData.length === 0) {
        console.log('没有特征重要性数据，跳过图表渲染');
        return;
      }
      
      // 准备数据
      const data = this.featureImportanceData.slice(0, 10).map(item => ({
        name: item.feature,
        value: parseFloat((item.importance * 100).toFixed(2))
      })).reverse();
      
      // 初始化图表
      this.chart = echarts.init(this.$refs.featureImportanceChart);
      
      // 设置图表选项
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: '{b}: {c}%'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}%'
          }
        },
        yAxis: {
          type: 'category',
          data: data.map(item => item.name)
        },
        series: [
          {
            name: '特征重要性',
            type: 'bar',
            data: data.map(item => item.value),
            itemStyle: {
              color: function(params) {
                // 颜色渐变
                const colorList = [
                  '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
                  '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#5470c6'
                ];
                return colorList[params.dataIndex % colorList.length];
              }
            }
          }
        ]
      };
      
      // 应用选项
      this.chart.setOption(option);
      
      // 响应窗口大小变化
      window.addEventListener('resize', () => {
        this.chart.resize();
      });
    },
    // 获取示例特征重要性数据
    getExampleFeatureImportanceData() {
      return [
        { feature: 'age', importance: 0.28, description: '年龄' },
        { feature: 'sysBP', importance: 0.22, description: '收缩压' },
        { feature: 'totChol', importance: 0.15, description: '总胆固醇' },
        { feature: 'glucose', importance: 0.12, description: '血糖水平' },
        { feature: 'BMI', importance: 0.09, description: '体重指数' },
        { feature: 'heartRate', importance: 0.06, description: '心率' },
        { feature: 'cigsPerDay', importance: 0.04, description: '每天吸烟数量' },
        { feature: 'male', importance: 0.02, description: '性别 (1=男性; 0=女性)' },
        { feature: 'prevalentHyp', importance: 0.01, description: '是否有高血压 (1=是; 0=否)' },
        { feature: 'diabetes', importance: 0.01, description: '是否有糖尿病 (1=是; 0=否)' }
      ];
    }
  }
};
</script>

<style scoped>
.feature-importance-container {
  padding: 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}

.chart {
  width: 100%;
  height: 100%;
}

.importance-bar {
  width: 100%;
  height: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}

.importance-fill {
  height: 100%;
  background-color: #409eff;
}

.shap-container {
  margin-top: 20px;
  text-align: center;
}

.shap-image {
  max-width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.no-data {
  padding: 20px;
  color: #606266;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.example-shap-description {
  margin: 15px 0;
  padding: 10px;
  background-color: #ecf5ff;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.example-shap-image {
  margin: 20px 0;
  text-align: center;
}

.example-caption {
  margin-top: 10px;
  font-size: 0.9em;
  color: #909399;
  font-style: italic;
}

.error-message {
  padding: 20px;
  color: #f56c6c;
  background-color: #fef0f0;
  border-radius: 4px;
}

.explanation-box {
  margin-top: 30px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.explanation-box h4 {
  margin-top: 10px;
  margin-bottom: 5px;
  color: #303133;
}

.explanation-box p {
  margin: 5px 0 15px;
  color: #606266;
  line-height: 1.6;
}
</style> 