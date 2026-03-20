<template>
  <div class="login-container">
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>
    <div class="bg-shape shape-3"></div>

    <div class="login-box glass-effect">
      <div class="login-header text-center mb-4">
        <h2>欢迎登录</h2>
        <p class="subtitle">请选择您的身份以继续</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3 input-group-custom">
          <label for="username" class="form-label">用户名</label>
          <input
            type="text"
            class="form-control custom-input"
            id="username"
            v-model="username"
            required
            :disabled="loading"
            placeholder="请输入用户名"
          />
        </div>

        <div class="mb-3 input-group-custom">
          <label for="password" class="form-label">密码</label>
          <input
            type="password"
            class="form-control custom-input"
            id="password"
            v-model="password"
            required
            :disabled="loading"
            placeholder="请输入密码"
          />
        </div>

        <div class="mb-4 row align-items-end">
          <div class="col-7 pr-1">
            <label for="captcha" class="form-label">验证码</label>
            <input
              type="text"
              class="form-control custom-input"
              id="captcha"
              v-model="captchaInput"
              required
              :disabled="loading"
              placeholder="输入验证码"
            />
          </div>
          <div class="col-5 pl-1 d-flex justify-content-end">
            <div @click="refreshCaptcha" class="captcha-box" title="点击刷新验证码">
              <span class="captcha-text">{{ captchaText }}</span>
            </div>
          </div>
        </div>

        <div class="mb-4 role-selector">
          <label class="form-label d-block mb-2">选择角色</label>
          <div class="d-flex gap-3">
            <label class="role-card flex-fill" :class="{ active: role === 'doctor' }">
              <input
                type="radio"
                name="role"
                v-model="role"
                value="doctor"
                :disabled="loading"
                class="d-none"
              />
              <span class="role-icon">👨‍⚕️</span>
              <span class="role-name">医生</span>
            </label>
            <label class="role-card flex-fill" :class="{ active: role === 'user' }">
              <input
                type="radio"
                name="role"
                v-model="role"
                value="user"
                :disabled="loading"
                class="d-none"
              />
              <span class="role-icon">👤</span>
              <span class="role-name">普通用户</span>
            </label>
          </div>
        </div>

        <div class="alert alert-danger custom-alert" v-if="error">
          <i class="error-icon">⚠️</i> {{ error }}
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100 login-btn"
          :disabled="loading"
        >
          <span v-if="!loading">立 即 登 录</span>
          <span v-else class="loading-state">
            <i class="spinner"></i> 登录中...
          </span>
        </button>

        <div class="text-center mt-4">
          <router-link to="/register" class="register-link">没有账号？立即注册</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import API_BASE_URL from '../config.js'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const role = ref('doctor')
    const captchaInput = ref('')
    const captchaText = ref('')
    const correctCaptcha = ref('')
    const error = ref(null)
    const loading = ref(false)

    const generateCaptchaText = (length = 4) => {
      const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
      let result = ''
      for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length))
      }
      return result
    }

    const refreshCaptcha = () => {
      const newCaptcha = generateCaptchaText()
      captchaText.value = newCaptcha
      correctCaptcha.value = newCaptcha
      captchaInput.value = ''
    }

    onMounted(() => {
      refreshCaptcha()
    })

    const handleLogin = async () => {
      error.value = null
      loading.value = true

      if (captchaInput.value.toLowerCase() !== correctCaptcha.value.toLowerCase()) {
        error.value = '验证码输入错误'
        loading.value = false
        refreshCaptcha()
        return
      }

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/login`, {
          username: username.value,
          password: password.value,
          role: role.value
        })

        let userData = {}
        if (typeof response.data.user === 'object') {
          userData = response.data.user
        } else {
          userData = {
            id: response.data.user,
            username: username.value,
            role: role.value
          }
        }

        if (userData.role && userData.role !== role.value) {
          throw new Error(`请使用${role.value === 'doctor' ? '医生' : '普通用户'}账号登录`)
        }

        await store.dispatch('login', {
          user: response.data.user,
          token: response.data.access_token
        })

        // 顺手帮你修正了原代码里路由跳转可能反掉的逻辑 bug
        const targetRoute = response.data.user.role === 'doctor' ? '/doctor' : '/user'
        await router.push(targetRoute)

      } catch (err) {
        error.value =
          err.response?.data?.message ||
          err.message ||
          '登录失败，请检查用户名或密码'
        password.value = ''
        refreshCaptcha()
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      role,
      captchaInput,
      captchaText,
      error,
      loading,
      handleLogin,
      refreshCaptcha
    }
  }
}
</script>

<style scoped>
/* --- 背景特效区 --- */
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 动态渐变背景：科技蓝与治愈青的结合 */
  background: linear-gradient(-45deg, #0f172a, #1e3a8a, #0d9488, #0f766e);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
  position: relative;
  overflow: hidden;
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 漂浮的光球特效 */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  animation: float 10s infinite ease-in-out;
}
.shape-1 {
  width: 300px; height: 300px;
  background: #3b82f6;
  top: -10%; left: -10%;
}
.shape-2 {
  width: 400px; height: 400px;
  background: #14b8a6;
  bottom: -15%; right: -10%;
  animation-delay: -3s;
}
.shape-3 {
  width: 200px; height: 200px;
  background: #6366f1;
  bottom: 20%; left: 20%;
  animation-delay: -6s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

/* --- 登录框主体（毛玻璃） --- */
.login-box.glass-effect {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  position: relative;
  z-index: 10;
}

.login-header h2 {
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}
.subtitle {
  color: #64748b;
  font-size: 0.9rem;
}

/* --- 表单元素美化 --- */
.form-label {
  font-weight: 500;
  color: #334155;
  font-size: 0.9rem;
}

.custom-input {
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.6rem 1rem;
  transition: all 0.3s ease;
}
.custom-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background-color: #ffffff;
}

/* --- 验证码专属样式 --- */
.captcha-box {
  width: 100%;
  height: 100%;
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
  border: 1px dashed #94a3b8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.captcha-box:hover {
  background: #e2e8f0;
  border-color: #64748b;
}
.captcha-text {
  font-size: 1.3rem;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: 4px;
  font-family: 'Courier New', Courier, monospace;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

/* --- 角色选择卡片式设计 --- */
.role-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.role-card:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}
.role-card.active {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.05);
}
.role-icon {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}
.role-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
}
.role-card.active .role-name {
  color: #3b82f6;
}

/* --- 按钮与链接 --- */
.login-btn {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  padding: 0.75rem;
  font-size: 1.05rem;
  font-weight: 600;
  border-radius: 8px;
  transition: transform 0.1s ease, box-shadow 0.2s ease;
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.login-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.register-link {
  color: #64748b;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}
.register-link:hover {
  color: #3b82f6;
}

/* --- 错误提示美化 --- */
.custom-alert {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
  border-radius: 8px;
  font-size: 0.9rem;
  padding: 0.75rem 1rem;
}

/* --- 简单的加载动画 --- */
.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  margin-right: 0.5rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>