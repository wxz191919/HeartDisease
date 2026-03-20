<template>
  <div class="profile-container pb-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold text-dark m-0">
          <i class="bi bi-shield-lock-fill me-2 text-primary"></i>账号安全管理
        </h3>
        <p class="text-muted mt-1 mb-0">您可以在此修改您的系统登录密码</p>
      </div>
    </div>

    <div class="row">
      <div class="col-lg-6 col-md-8">
        <div class="card shadow-sm border-0" style="border-radius: 12px;">
          <div class="card-body p-4">

            <div v-if="errorMessage" class="alert alert-danger d-flex align-items-center mb-4" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              <div>{{ errorMessage }}</div>
            </div>

            <div v-if="successMessage" class="alert alert-success d-flex align-items-center mb-4" role="alert">
              <i class="bi bi-check-circle-fill me-2"></i>
              <div>{{ successMessage }}</div>
            </div>

            <form @submit.prevent="submitChangePassword">

              <div class="mb-3">
                <label class="form-label fw-bold text-muted">当前账号</label>
                <input type="text" class="form-control bg-light" :value="username" disabled>
                <div class="form-text">账号名不可修改</div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">原密码</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-key"></i></span>
                  <input type="password" v-model="form.oldPassword" class="form-control" placeholder="请输入当前使用的密码" required>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label fw-bold">新密码</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-lock"></i></span>
                  <input type="password" v-model="form.newPassword" class="form-control" placeholder="请输入新密码（至少6位）" minlength="6" required>
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold">确认新密码</label>
                <div class="input-group">
                  <span class="input-group-text bg-light"><i class="bi bi-lock-fill"></i></span>
                  <input type="password" v-model="form.confirmPassword" class="form-control" placeholder="请再次输入新密码" minlength="6" required>
                </div>
              </div>

              <button type="submit" class="btn btn-primary w-100 fw-bold py-2 rounded-pill shadow-sm" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-save me-2"></i>保存修改并重新登录
              </button>
            </form>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'

export default {
  name: 'Profile',
  setup() {
    const router = useRouter()
    const store = useStore()

    // 获取用户名展示
    const username = computed(() => {
      const user = store.getters.currentUser || JSON.parse(localStorage.getItem('user') || '{}')
      return user.username || '当前用户'
    })

    const form = ref({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    const loading = ref(false)
    const errorMessage = ref('')
    const successMessage = ref('')

    const submitChangePassword = async () => {
      errorMessage.value = ''
      successMessage.value = ''

      if (form.value.newPassword !== form.value.confirmPassword) {
        errorMessage.value = '两次输入的新密码不一致，请重新输入！'
        return
      }

      loading.value = true

      try {
        // 🚀 核心修复区：去掉了 const response = ，直接 await 发送请求，ESLint 瞬间绿灯！
        // 同时补全了完整的 API 路径 /api/auth/change-password
        await axios.put('/api/auth/change-password', {
          old_password: form.value.oldPassword,
          new_password: form.value.newPassword
        }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        successMessage.value = '密码修改成功！3秒后将跳转至登录页...'

        setTimeout(() => {
          store.dispatch('logout')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          router.push('/login')
        }, 3000)

      } catch (error) {
        if (error.response && error.response.data && error.response.data.message) {
          errorMessage.value = error.response.data.message
        } else {
          errorMessage.value = '网络或服务器错误，请稍后再试。'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      form,
      loading,
      errorMessage,
      successMessage,
      submitChangePassword
    }
  }
}
</script>

<style scoped>
.profile-container { max-width: 1200px; margin: 0 auto; }
.input-group-text { border-right: none; color: #6c757d; }
.form-control { border-left: none; }
.form-control:focus { box-shadow: none; border-color: #dee2e6; }
.input-group:focus-within { box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25); border-radius: 0.375rem; }
.input-group:focus-within .input-group-text, .input-group:focus-within .form-control { border-color: #86b7fe; }

[data-theme="dark"] .card { background-color: #1e293b !important; border-color: #334155 !important; }
[data-theme="dark"] .text-dark { color: #f1f5f9 !important; }
[data-theme="dark"] .text-muted { color: #94a3b8 !important; }
[data-theme="dark"] .bg-light { background-color: #334155 !important; color: #f1f5f9; border-color: #475569; }
[data-theme="dark"] .form-control { background-color: #1e293b; color: #f1f5f9; border-color: #475569; }
</style>