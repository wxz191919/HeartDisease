<template>
  <div class="layout-container">
    <nav class="sidebar custom-sidebar">
      <div class="sidebar-sticky d-flex flex-column h-100">

        <div class="sidebar-header py-4 text-center">
          <h3 class="fw-bold text-white mb-0 d-flex align-items-center justify-content-center">
            <i class="bi bi-heart-pulse-fill text-danger me-2 fs-2"></i>
            <span style="letter-spacing: 1px;">智能问诊后台</span>
          </h3>
          <p class="text-secondary mt-1 mb-0 fs-7">Heart Disease AI System</p>
        </div>

        <ul class="nav flex-column mt-3 px-2 custom-nav-list flex-grow-1">
          <li class="nav-item">
            <router-link to="/doctor/dashboard" class="nav-link custom-nav-link">
              <i class="bi bi-speedometer2 me-3 fs-5"></i><span>仪表盘</span>
            </router-link>
          </li>

          <li class="nav-item">
            <router-link to="/doctor/patients" class="nav-link custom-nav-link">
              <i class="bi bi-people me-3 fs-5"></i><span>病人管理</span>
            </router-link>
          </li>

          <li class="nav-item dropdown">
            <a class="nav-link custom-nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="collapse" data-bs-target="#predictionSubmenu">
              <i class="bi bi-graph-up-arrow me-3 fs-5"></i><span>风险预测</span>
            </a>
            <ul class="collapse nav flex-column custom-submenu" id="predictionSubmenu">
              <li class="nav-item">
                <router-link to="/doctor/prediction" class="nav-link custom-sub-link">
                  <i class="bi bi-plus-circle me-2"></i>新建预测
                </router-link>
              </li>
              <li class="nav-item">
                <router-link to="/doctor/prediction-history" class="nav-link custom-sub-link">
                  <i class="bi bi-clock-history me-2"></i>历史记录
                </router-link>
              </li>
            </ul>
          </li>

          <li class="nav-item mt-3 mb-1 px-3">
            <small class="text-secondary fw-bold" style="font-size: 0.75rem; letter-spacing: 1px;">AI & 数据分析</small>
          </li>

          <li class="nav-item">
            <router-link to="/doctor/feature-importance" class="nav-link custom-nav-link">
              <i class="bi bi-bar-chart-steps me-3 fs-5 text-info"></i><span>重要性分析</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/doctor/map" class="nav-link custom-nav-link">
              <i class="bi bi-geo-alt me-3 fs-5 text-success"></i><span>医院地图</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/doctor/chat" class="nav-link custom-nav-link">
              <i class="bi bi-robot me-3 fs-5 text-warning"></i><span>AI 专家问诊</span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/doctor/data-analysis" class="nav-link custom-nav-link">
              <i class="bi bi-display me-3 fs-5 text-primary"></i><span>全球数据大屏</span>
            </router-link>
          </li>
        </ul>

        <div class="sidebar-footer p-3 mt-auto">
          <div class="user-card p-3 rounded-4 mb-3 d-flex align-items-center">
            <div class="avatar bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-3" style="width: 40px; height: 40px; font-weight: bold;">
              {{ username.charAt(0).toUpperCase() }}
            </div>
            <div class="user-info overflow-hidden">
              <div class="text-white fw-bold text-truncate">{{ username }}</div>
              <div class="text-secondary fs-7">主治医师</div>
            </div>
          </div>

          <button class="btn btn-logout w-100 d-flex align-items-center justify-content-center fw-bold" @click="handleLogout">
            <i class="bi bi-box-arrow-right me-2 fs-5"></i> 安全退出系统
          </button>
        </div>

      </div>
    </nav>
    <main class="main-content"><router-view></router-view></main>
  </div>
</template>

<script>
import { useStore } from 'vuex'; import { useRouter } from 'vue-router'; import { computed, onMounted } from 'vue'; import { Dropdown } from 'bootstrap'

export default {
  name: 'Layout',
  setup() {
    const store = useStore(); const router = useRouter()
    const username = computed(() => store.getters.currentUser?.username || '未登录')
    const handleLogout = () => { store.dispatch('logout'); router.push('/login') }

    onMounted(() => {
      document.querySelectorAll('.dropdown-toggle').forEach(el => new Dropdown(el))
      const userDropdown = document.getElementById('userDropdown')
      if (userDropdown) new Dropdown(userDropdown)
    })

    return { username, handleLogout }
  }
}
</script>

<style scoped>
/* ================== 全局与布局结构 ================== */
/* 🚀 核心修复：背景强制透明，让全局粒子网格透上来 */
.layout-container { display: flex; min-height: 100vh; background: transparent; }
.main-content { margin-left: 260px; padding: 2rem; width: calc(100% - 260px); min-height: 100vh; background: transparent; }
.fs-7 { font-size: 0.85rem; }

/* ================== 侧边栏高级样式 ================== */
.custom-sidebar {
  width: 260px;
  position: fixed;
  height: 100vh;
  /* 高级深邃蓝渐变背景 */
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  box-shadow: 4px 0 20px rgba(0,0,0,0.05);
  z-index: 1000;
}

.sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

/* ================== 菜单项极致美化 ================== */
.custom-nav-link {
  color: #94a3b8 !important; /* 默认未选中颜色 */
  padding: 0.85rem 1.2rem;
  margin-bottom: 0.4rem;
  border-radius: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

/* 悬停状态 (丝滑右移效果) */
.custom-nav-link:hover {
  background-color: rgba(241, 245, 249, 0.05);
  color: #f8fafc !important;
  transform: translateX(5px);
}

/* 激活状态 (科幻发光感) */
.custom-nav-link.router-link-active {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%);
  color: #60a5fa !important;
  font-weight: 600;
  border-left: 4px solid #3b82f6;
  border-radius: 0 12px 12px 0;
}
.custom-nav-link.router-link-active i {
  color: #3b82f6 !important;
}

/* ================== 折叠子菜单 ================== */
.custom-submenu {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  margin: 0.2rem 1rem 0.5rem 1rem;
  padding: 0.5rem 0;
}
.custom-sub-link {
  color: #64748b !important;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  border-radius: 8px;
  margin: 0.1rem 0.5rem;
}
.custom-sub-link:hover {
  color: #e2e8f0 !important;
  background-color: rgba(255, 255, 255, 0.05);
}
.custom-sub-link.router-link-active {
  color: #38bdf8 !important;
  font-weight: bold;
}

/* ================== 底部用户卡片与按钮 ================== */
.sidebar-footer { border-top: 1px solid rgba(255, 255, 255, 0.05); }
.user-card { background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); }

.btn-logout {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 12px;
  padding: 0.75rem;
  transition: all 0.3s ease;
}
.btn-logout:hover {
  background-color: #ef4444;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* 修改自带的下拉箭头对齐 */
.dropdown-toggle::after {
  margin-left: auto;
  vertical-align: middle;
}
</style>