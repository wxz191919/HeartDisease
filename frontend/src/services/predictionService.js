import axios from 'axios';

// 机器学习API的基础URL - Vue CLI用VUE_APP_*前缀
const API_BASE_URL = (process.env && process.env.VUE_APP_API_URL) || 'http://localhost:5002/api';

// 创建一个专用的axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000 // 10秒超时
});

/**
 * 预测服务
 */
export default {
  /**
   * 健康检查
   * @returns {Promise} 健康状态
   */
  async healthCheck() {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('健康检查失败:', error);
      throw error;
    }
  },

  /**
   * 获取特征信息
   * @returns {Promise} 特征信息
   */
  async getFeatures() {
    try {
      const response = await apiClient.get('/features');
      return response.data;
    } catch (error) {
      console.error('获取特征信息失败:', error);
      throw error;
    }
  },

  /**
   * 获取样本输入
   * @returns {Promise} 样本输入
   */
  async getSampleInput() {
    try {
      const response = await apiClient.get('/features');
      return response.data.sample_input;
    } catch (error) {
      console.error('获取样本输入失败:', error);
      throw error;
    }
  },

  /**
   * 进行预测
   * @param {Object} data 预测数据
   * @returns {Promise} 预测结果
   */
  async predict(data) {
    try {
      const response = await apiClient.post('/predict', data);
      return response.data;
    } catch (error) {
      console.error('预测失败:', error);
      throw error;
    }
  },

  /**
   * 批量预测
   * @param {Array} dataList 预测数据列表
   * @returns {Promise} 预测结果列表
   */
  async batchPredict(dataList) {
    try {
      const response = await apiClient.post('/batch_predict', dataList);
      return response.data;
    } catch (error) {
      console.error('批量预测失败:', error);
      throw error;
    }
  }
}; 