// API 配置（Vue CLI：Vercel 环境变量填 VUE_APP_API_URL）
const API_BASE_URL = (process.env && process.env.VUE_APP_API_URL) || 'http://localhost:5003/api';

export default API_BASE_URL;
