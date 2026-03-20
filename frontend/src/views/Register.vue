<template>
  <div class="register-container">
    <div class="register-box">
      <h2 class="text-center mb-4">注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="username" class="form-label">用户名</label>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="username"
            required
          />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">密码</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="password"
            required
          />
        </div>
        <div class="mb-3">
          <label for="confirmPassword" class="form-label">确认密码</label>
          <input
            type="password"
            class="form-control"
            id="confirmPassword"
            v-model="confirmPassword"
            required
          />
        </div>
        <div class="mb-3 row">
          <div class="col-md-7">
            <label for="captcha" class="form-label">验证码</label>
            <input
              type="text"
              class="form-control"
              id="captcha"
              v-model="captchaInput"
              required
              placeholder="请输入验证码"
            />
          </div>
          <div class="col-md-5 d-flex align-items-center justify-content-start">
            <span @click="refreshCaptcha" class="captcha-text" title="点击刷新">
              {{ captchaText }}
            </span>
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label">用户角色</label>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="roleUser"
              value="user"
              v-model="role"
              checked
            />
            <label class="form-check-label" for="roleUser">
              普通用户
            </label>
          </div>
          <div class="form-check">
            <input
              class="form-check-input"
              type="radio"
              id="roleDoctor"
              value="doctor"
              v-model="role"
            />
            <label class="form-check-label" for="roleDoctor">
              医生
            </label>
          </div>
        </div>
        <div class="alert alert-danger" v-if="error">
          {{ error }}
        </div>
        <button type="submit" class="btn btn-primary w-100">注册</button>
        <div class="text-center mt-3">
          <router-link to="/login">已有账号？立即登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import API_BASE_URL from '../config.js'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      role: 'user',
      captchaInput: '',
      captchaText: '',
      correctCaptcha: '',
      error: null
    }
  },
  methods: {
    generateCaptchaText(length = 4) {
      const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
      let result = ''
      for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length))
      }
      return result
    },
    refreshCaptcha() {
      const newCaptcha = this.generateCaptchaText()
      this.captchaText = newCaptcha
      this.correctCaptcha = newCaptcha
      this.captchaInput = ''
    },
    async handleRegister() {
      this.error = null
      if (this.password !== this.confirmPassword) {
        this.error = '两次输入的密码不一致'
        this.refreshCaptcha()
        return
      }

      if (this.captchaInput.toLowerCase() !== this.correctCaptcha.toLowerCase()) {
        this.error = '验证码输入错误'
        this.refreshCaptcha()
        return
      }

      try {
        await axios.post(`${API_BASE_URL}/register`, {
          username: this.username,
          password: this.password,
          role: this.role
        })

        this.$router.push('/login')
      } catch (err) {
        this.error =
          (err.response && err.response.data && err.response.data.message) ||
          '注册失败，请重试'
        this.refreshCaptcha()
      }
    }
  },
  mounted() {
    this.refreshCaptcha()
  }
}
</script>

<style scoped>
.captcha-text {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  font-size: 1.2rem;
  font-weight: bold;
  background-color: #e9ecef;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  cursor: pointer;
  user-select: none;
  font-family: 'Courier New', Courier, monospace;
  margin-left: 0.5rem;
  line-height: 1.5;
}

.register-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.register-box {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.form-check {
  margin-bottom: 0.5rem;
}

.form-check-input {
  margin-right: 0.5rem;
}
</style>