<template>
  <div class="layout-container-top">
    <nav class="top-navbar shadow">
      <div class="navbar-brand">
        <i class="bi bi-heart-pulse-fill text-white me-2" style="font-size: 1.5rem;"></i>
        <h3 class="m-0 text-white">
          心脏病预测系统 <small class="ms-2 badge bg-light text-primary">用户版</small>
        </h3>
      </div>

      <ul class="nav-links">
        <li class="nav-item">
          <router-link to="/user/dashboard" class="nav-link">
            <i class="bi bi-house-door me-1"></i> 首页
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/user/patients" class="nav-link">
            <i class="bi bi-clipboard2-pulse me-1"></i> 风险预测
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/user/feature-importance" class="nav-link">
            <i class="bi bi-bar-chart me-1"></i> 致病因素
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/user/map" class="nav-link">
            <i class="bi bi-map me-1"></i> 医院地图
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/user/chat" class="nav-link">
            <i class="bi bi-robot me-1 text-warning"></i> AI 问诊
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/user/data-analysis" class="nav-link">
            <i class="bi bi-database-fill-gear me-1 text-info"></i> 数据大屏
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/user/tracker" class="nav-link">
            <i class="bi bi-file-earmark-medical me-1 text-success"></i> 趋势报告
          </router-link>
        </li>
      </ul>

      <div class="user-actions d-flex align-items-center">
        <button class="btn btn-outline-light me-3 d-flex align-items-center theme-btn" @click="toggleTheme">
          <span v-if="theme === 'light'"><i class="bi bi-moon-fill me-1"></i>夜间</span>
          <span v-else><i class="bi bi-sun-fill me-1"></i>日间</span>
        </button>

        <div class="user-dropdown-container position-relative">
          <button class="btn btn-outline-light user-btn d-flex align-items-center" type="button" @click="toggleUserMenu">
            <i class="bi bi-person-circle me-1"></i>
            {{ username }}
            <i class="bi bi-caret-down-fill ms-2" style="font-size: 0.7rem;"></i>
          </button>

          <transition name="dropdown-fade">
            <ul v-show="isUserMenuOpen" class="custom-dropdown-menu shadow-lg">
              <li>
                <a class="dropdown-item py-2" href="#" @click.prevent="goToAccountManage">
                  <i class="bi bi-person-gear me-2 text-primary"></i>账号管理
                </a>
              </li>
              <li>
                <a class="dropdown-item py-2" href="#" @click.prevent="goToChangePassword">
                  <i class="bi bi-shield-lock me-2 text-warning"></i>修改密码
                </a>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <a class="dropdown-item py-2 text-danger fw-bold" href="#" @click.prevent="handleLogout">
                  <i class="bi bi-box-arrow-right me-2"></i>退出登录
                </a>
              </li>
            </ul>
          </transition>
        </div>
      </div>
    </nav>

    <main class="main-content-top">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { computed, ref, onMounted, onBeforeUnmount, inject } from 'vue'

export default {
  name: 'DoctorLayout',
  setup() {
    const store = useStore()
    const router = useRouter()

    const theme = inject('globalTheme', ref(localStorage.getItem('theme') || 'light'))
    const injectedToggle = inject('toggleTheme', null)

    const toggleTheme = () => {
      if (injectedToggle) {
        injectedToggle()
      } else {
        theme.value = theme.value === 'light' ? 'dark' : 'light'
        localStorage.setItem('theme', theme.value)
        document.documentElement.setAttribute('data-theme', theme.value)
      }
    }

    const username = computed(() => {
      try {
        const user = store.getters.currentUser || JSON.parse(localStorage.getItem('user'))
        return user ? user.username : '普通用户'
      } catch (error) {
        return '普通用户'
      }
    })

    const isUserMenuOpen = ref(false)

    const toggleUserMenu = (e) => {
      if(e) e.stopPropagation()
      isUserMenuOpen.value = !isUserMenuOpen.value
    }

    const closeUserMenu = (e) => {
      if (!e.target.closest('.user-dropdown-container')) {
        isUserMenuOpen.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', closeUserMenu)
    })

    onBeforeUnmount(() => {
      document.removeEventListener('click', closeUserMenu)
    })

    const goToAccountManage = () => {
      isUserMenuOpen.value = false
      router.push('/user/profile')
    }

    const goToChangePassword = () => {
      isUserMenuOpen.value = false
      router.push('/user/profile')
    }

    const handleLogout = () => {
      isUserMenuOpen.value = false
      try {
        store.dispatch('logout')
      } catch (e) {
        console.warn('清理系统状态...', e)
      }
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }

    return {
      username,
      theme,
      toggleTheme,
      isUserMenuOpen,
      toggleUserMenu,
      goToAccountManage,
      goToChangePassword,
      handleLogout
    }
  }
}
</script>

<style scoped>
.layout-container-top {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 动态流动渐变导航栏 */
.top-navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 70px;
  background: linear-gradient(-45deg, #3b82f6, #8b5cf6, #ec4899, #06b6d4, #3b82f6);
  background-size: 400% 400%;
  animation: gradientFlow 12s ease infinite;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  z-index: 99999 !important;
  pointer-events: auto !important;
}

@keyframes gradientFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.navbar-brand {
  display: flex;
  align-items: center;
}
.navbar-brand h3 {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 1px;
}
.navbar-brand small {
  font-size: 0.75rem;
  vertical-align: middle;
}

.nav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 1.5rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9) !important;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  font-size: 1.05rem;
}

.nav-link:hover, .nav-link.router-link-active {
  color: #ffffff !important;
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.theme-btn, .user-btn {
  border-radius: 20px;
  padding: 0.4rem 1.2rem;
  font-weight: 600;
  border-width: 2px;
  transition: all 0.3s;
}

.theme-btn:hover, .user-btn:hover {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

/* 自定义下拉菜单样式 */
.custom-dropdown-menu {
  position: absolute;
  top: 130%;
  right: 0;
  background-color: #ffffff;
  border-radius: 8px;
  min-width: 170px;
  padding: 0.5rem 0;
  list-style: none;
  margin: 0;
  z-index: 999999 !important;
  border: 1px solid #e2e8f0;
}

.custom-dropdown-menu .dropdown-item {
  color: #334155;
  text-decoration: none;
  display: block;
  font-size: 0.95rem;
  transition: background-color 0.2s;
}

.custom-dropdown-menu .dropdown-item:hover {
  background-color: #f1f5f9;
}

.dropdown-divider {
  border-top: 1px solid #e2e8f0;
  margin: 0.4rem 0;
}

.dropdown-fade-enter-active, .dropdown-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.dropdown-fade-enter-from, .dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.main-content-top {
  margin-top: 70px;
  padding: 2rem;
  flex: 1;
  width: 100%;
  box-sizing: border-box;
}

/* 夜间模式绝对防御网 */
[data-theme="dark"] .top-navbar {
  background: linear-gradient(-45deg, #0f172a, #1e293b, #334155, #1e293b) !important;
  border-bottom: 1px solid #334155;
}
[data-theme="dark"] .custom-dropdown-menu {
  background-color: #1e293b !important;
  border: 1px solid #334155 !important;
}
[data-theme="dark"] .custom-dropdown-menu .dropdown-item {
  color: #f1f5f9 !important;
}
[data-theme="dark"] .custom-dropdown-menu .dropdown-item:hover {
  background-color: #334155 !important;
}
[data-theme="dark"] .dropdown-divider {
  border-top-color: #334155 !important;
}
</style>