import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Layout from '../components/Layout.vue'
import DoctorLayout from '../components/DoctorLayout.vue'

import Dashboard from '../views/doctor/Dashboard.vue'
import PatientManagement from '../views/doctor/PatientManagement.vue'
import Prediction from '../views/doctor/Prediction.vue'
import FeatureImportance from '../views/doctor/FeatureImportance.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login, meta: { public: true } },
  { path: '/register', name: 'Register', component: Register, meta: { public: true } },

  // ================= 医生路由 =================
  {
    path: '/doctor',
    component: Layout,
    meta: { requiresAuth: true, allowedRoles: ['doctor'] },
    children: [
      { path: '', redirect: '/doctor/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'patients', name: 'PatientManagement', component: PatientManagement },
      { path: 'prediction', name: 'Prediction-doctor', component: Prediction },
      { path: 'prediction-history', name: 'PredictionHistory', component: () => import('../views/doctor/PredictionHistory.vue') },
      { path: 'prediction-detail/:id', name: 'PredictionDetail', component: () => import('../views/doctor/PredictionDetail.vue'), props: true },
      { path: 'feature-importance', name: 'FeatureImportance', component: FeatureImportance },
      { path: 'map', name: 'DoctorMap', component: () => import('../views/HospitalMap.vue') },
      { path: 'chat', name: 'DoctorAIChat', component: () => import('../views/user/AIChat.vue') },
      { path: 'data-analysis', name: 'DoctorDataAnalysis', component: () => import('../views/user/DataAnalysis.vue') },
      { path: 'tracker', name: 'DoctorHealthTracker', component: () => import('../views/user/HealthTracker.vue') }
    ]
  },

  // ================= 用户路由 =================
  {
    path: '/user',
    component: DoctorLayout,
    meta: { requiresAuth: true, allowedRoles: ['user'] },
    children: [
      { path: '', redirect: '/user/patients' },
      { path: 'dashboard', name: 'UserDashboard', component: () => import('../views/user/Dashboard.vue') },
      { path: 'patients', name: 'UserPatientManagement', component: () => import('../views/user/PatientManagement.vue') },
      { path: 'prediction', name: 'UserPrediction', component: () => import('../views/user/Prediction.vue') },
      { path: 'prediction-history', name: 'UserPredictionHistory', component: () => import('../views/user/PredictionHistory.vue') },

      // 🚨 你的 DeepSeek 详细报告页就在这里被精准匹配！
      { path: 'prediction-detail/:id', name: 'UserPredictionDetail', component: () => import('../views/user/PredictionDetail.vue'), props: true },

      { path: 'feature-importance', name: 'UserFeatureImportance', component: () => import('../views/user/FeatureImportance.vue') },
      { path: 'map', name: 'UserMap', component: () => import('../views/HospitalMap.vue') },
      { path: 'profile', name: 'UserProfile', component: () => import('../views/Profile.vue') },
      { path: 'chat', name: 'AIChat', component: () => import('../views/user/AIChat.vue') },
      { path: 'data-analysis', name: 'DataAnalysis', component: () => import('../views/user/DataAnalysis.vue') },
      { path: 'tracker', name: 'HealthTracker', component: () => import('../views/user/HealthTracker.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const isAuthenticated = !!token && !!user

  if (to.meta.public) {
    if (isAuthenticated) {
      return next(user.role === 'doctor' ? '/doctor/dashboard' : '/user/dashboard')
    }
    return next()
  }

  if (to.meta.requiresAuth && !isAuthenticated) return next('/login')

  if (to.meta.allowedRoles) {
    const hasPermission = to.meta.allowedRoles.includes(user?.role)
    if (!hasPermission) {
      // 🚀🚀🚀 核心黑科技修复：自动拦截并纠正路由跨界问题！
      // 如果当前是普通用户，却被按钮误导向了医生的详情页，强制把它掰回用户的详情页！
      if (user?.role === 'user' && to.path.startsWith('/doctor/')) {
        const correctPath = to.path.replace('/doctor/', '/user/')
        return next(correctPath)
      }

      // 反之亦然，保护医生不被误导
      if (user?.role === 'doctor' && to.path.startsWith('/user/')) {
        const correctPath = to.path.replace('/user/', '/doctor/')
        return next(correctPath)
      }

      return next(user?.role === 'doctor' ? '/doctor/dashboard' : '/user/dashboard')
    }
  }

  next()
})

export default router