<template>
  <div class="dashboard">
    <h2 class="mb-4">仪表盘</h2>
    
    <div class="row">
      <!-- 统计卡片 -->

      
      <div class="col-md-3 mb-4">
        <div class="card bg-info text-white h-100">
          <div class="card-body d-flex flex-column align-items-start">
            <div class="d-flex align-items-center w-100 mb-2">
              <i class="bi bi-graph-up me-2 fs-4"></i>
              <h5 class="card-title mb-0">预测次数</h5>
            </div>
            <h2 class="card-text mt-2">{{ stats.predictions || 0 }}</h2>
            <small class="mt-auto">已完成的风险预测总数</small>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-4">
        <div class="card bg-warning text-white h-100">
          <div class="card-body d-flex flex-column align-items-start">
            <div class="d-flex align-items-center w-100 mb-2">
              <i class="bi bi-exclamation-triangle-fill me-2 fs-4"></i>
              <h5 class="card-title mb-0">高风险病例</h5>
            </div>
            <h2 class="card-text mt-2">{{ stats.highRisk || 0 }}</h2>
            <small class="mt-auto">被判定为高风险的病例数</small>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="card">
      <div class="card-header bg-light">
        <div class="d-flex align-items-center">
          <i class="bi bi-activity me-2"></i>
          <h5 class="card-title mb-0">最近活动</h5>
        </div>
      </div>
      <div class="card-body">
        <div class="list-group">
          <a v-for="activity in recentActivities" 
             :key="activity.id" 
             href="#" 
             class="list-group-item list-group-item-action">
            <div class="d-flex w-100 justify-content-between">
              <h6 class="mb-1">
                <i v-if="activity.id.startsWith('file_')" class="bi bi-file-earmark-text me-2"></i>
                <i v-else-if="activity.id.startsWith('pred_')" class="bi bi-clipboard-data me-2"></i>
                {{ activity.title }}
              </h6>
              <small class="text-muted">{{ formatDate(activity.time) }}</small>
            </div>
            <p class="mb-1">{{ activity.description }}</p>
          </a>
          <div v-if="recentActivities.length === 0" class="text-center py-4">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <p class="mt-2 text-muted">暂无活动记录</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 刷新按钮 -->
    <div class="text-center mt-4">
      <button class="btn btn-outline-primary" @click="fetchDashboardData">
        <i class="bi bi-arrow-clockwise me-2"></i>刷新数据
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'Dashboard',
  setup() {
    const stats = ref({})
    const recentActivities = ref([])
    const loading = ref(false)

    const fetchDashboardData = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/dashboard')
        stats.value = response.data.stats
        recentActivities.value = response.data.activities
      } catch (error) {
        console.error('获取仪表盘数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleString()
    }

    onMounted(() => {
      fetchDashboardData()
    })

    return {
      stats,
      recentActivities,
      loading,
      fetchDashboardData,
      formatDate
    }
  }
}
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: transform 0.3s, box-shadow 0.3s;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.card-title {
  font-size: 1.1rem;
}

.list-group-item {
  transition: background-color 0.2s;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.btn-outline-primary {
  transition: all 0.3s;
}

.btn-outline-primary:hover {
  transform: scale(1.05);
}
</style> 