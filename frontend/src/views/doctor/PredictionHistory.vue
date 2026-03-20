<template>
  <div class="prediction-history-container pb-4">
    <div class="d-flex justify-content-between align-items-end mb-4 border-bottom pb-3">
      <div>
        <h3 class="fw-bold text-dark m-0">
          <i class="el-icon-time text-primary mr-2"></i>历史预测档案库
        </h3>
        <p class="text-muted mt-2 mb-0">追踪与管理所有患者的心血管风险临床评估记录</p>
      </div>
      <el-button type="primary" icon="el-icon-refresh" @click="refreshData" :loading="loading" round>
        同步最新数据
      </el-button>
    </div>

    <el-card class="box-card shadow-sm border-0" body-style="padding: 20px;">
      <div v-if="error" class="alert alert-danger">
        <i class="el-icon-error mr-2"></i>{{ error }}
      </div>

      <el-table
        v-loading="loading"
        :data="predictionHistory"
        style="width: 100%"
        :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight:'bold'}"
        border
        stripe
        hover>

        <el-table-column prop="id" label="档案编号" width="100" align="center">
          <template #default="scope">
            <span class="fw-bold text-muted">#{{ scope.row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="patientName" label="患者姓名" width="150" align="center">
          <template #default="scope">
            <div class="d-flex align-items-center justify-content-center">
              <el-avatar size="small" style="background:#3b82f6; margin-right:8px;">
                {{ scope.row.patientName ? scope.row.patientName.charAt(0) : '?' }}
              </el-avatar>
              <span class="fw-bold">{{ scope.row.patientName }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="predictionTime" label="评估生成时间" width="200" align="center">
          <template #default="scope">
            <i class="el-icon-time text-muted mr-1"></i>
            {{ formatDate(scope.row.predictionTime) }}
          </template>
        </el-table-column>

        <el-table-column prop="probability" label="系统测算高危概率" width="180" align="center">
          <template #default="scope">
            <span class="fw-bold fs-6" :class="getProbabilityColor(scope.row.probability)">
              {{ formatProbability(scope.row.probability) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="riskLevel" label="系统定级" width="150" align="center">
          <template #default="scope">
            <el-tag :type="getRiskLevelTag(scope.row.riskLevel)" effect="dark" size="medium">
              {{ scope.row.riskLevel || '未知风险' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="临床操作" min-width="200" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" icon="el-icon-document" @click="viewDetail(scope.row.id)" plain>
              调阅分析报告
            </el-button>
            <el-popconfirm title="危险操作：确定要彻底销毁此条患者档案吗？" @confirm="deleteRecord(scope.row.id)">
              <template #reference>
                <el-button size="small" type="danger" icon="el-icon-delete" plain>销毁</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container mt-4 d-flex justify-content-end">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalRecords"
          background>
        </el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import API_BASE_URL from '../../config.js';

export default {
  name: 'PredictionHistory',
  data() {
    return {
      predictionHistory: [],
      loading: false,
      error: null,
      currentPage: 1,
      pageSize: 10,
      totalRecords: 0
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;

      try {
        const token = localStorage.getItem('token');
        // 带着 Token 去数据库拉取真实的列表
        const response = await axios.get(`${API_BASE_URL}/predictions?page=${this.currentPage}&per_page=${this.pageSize}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = response.data;
        this.predictionHistory = data.items || data.data || [];
        this.totalRecords = data.total || this.predictionHistory.length;

      } catch (error) {
        console.error('获取预测历史失败:', error);
        this.error = '无法连接到数据库获取历史记录，请检查网络或重新登录。';
      } finally {
        this.loading = false;
      }
    },

    refreshData() {
      this.currentPage = 1;
      this.fetchData();
    },

    // 🚀 核心修复：跳转地址修正为 prediction-detail
    viewDetail(id) {
      this.$router.push(`/doctor/prediction-detail/${id}`);
    },

    async deleteRecord(id) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API_BASE_URL}/predictions/${id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        this.$message({
          type: 'success',
          message: '档案销毁成功'
        });
        this.fetchData(); // 删完刷新列表

      } catch (error) {
        console.error('删除预测记录失败:', error);
        this.$message({
          type: 'error',
          message: '删除失败，权限不足或网络异常'
        });
      }
    },

    handleSizeChange(val) {
      this.pageSize = val;
      this.fetchData();
    },

    handleCurrentChange(val) {
      this.currentPage = val;
      this.fetchData();
    },

    formatDate(dateString) {
      if (!dateString) return '未知时间';
      const date = new Date(dateString);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    },

    formatProbability(prob) {
      if (prob === null || prob === undefined) return '--';
      return prob < 1 ? (prob * 100).toFixed(1) + '%' : parseFloat(prob).toFixed(1) + '%';
    },

    getProbabilityColor(prob) {
      const value = prob < 1 ? prob * 100 : prob;
      if (value >= 70) return 'text-danger';
      if (value >= 30) return 'text-warning';
      return 'text-success';
    },

    getRiskLevelTag(level) {
      const map = {
        '高风险': 'danger',
        '中风险': 'warning',
        '低风险': 'success'
      };
      return map[level] || 'info';
    }
  }
};
</script>

<style scoped>
.prediction-history-container {
  padding: 20px;
}
.box-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}
.text-danger { color: #ef4444 !important; }
.text-warning { color: #f59e0b !important; }
.text-success { color: #10b981 !important; }
.text-muted { color: #64748b !important; }
.fw-bold { font-weight: 700 !important; }
.fs-6 { font-size: 1rem !important; }
.mr-1 { margin-right: 0.25rem !important; }
.mr-2 { margin-right: 0.5rem !important; }
.mb-0 { margin-bottom: 0 !important; }
.mt-2 { margin-top: 0.5rem !important; }
.mt-4 { margin-top: 1.5rem !important; }
.pb-3 { padding-bottom: 1rem !important; }
.pb-4 { padding-bottom: 1.5rem !important; }
.d-flex { display: flex !important; }
.align-items-center { align-items: center !important; }
.align-items-end { align-items: flex-end !important; }
.justify-content-between { justify-content: space-between !important; }
.justify-content-center { justify-content: center !important; }
.justify-content-end { justify-content: flex-end !important; }
.border-bottom { border-bottom: 1px solid #e2e8f0 !important; }
</style>