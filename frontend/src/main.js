import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import axios from 'axios'

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:5003'
axios.defaults.headers.common['Content-Type'] = 'application/json'
axios.defaults.headers.common['Accept'] = 'application/json'
axios.defaults.withCredentials = false

// 请求拦截器
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  console.error('请求错误:', error)
  return Promise.reject(error)
})

// 响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    console.error('响应错误:', error)
    if (error.response && error.response.status === 401) {
      // 清除无效的登录状态
      store.dispatch('logout')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)




const app = createApp(App)
app.use(router)
app.use(store)
app.use(ElementPlus)
app.mount('#app') 