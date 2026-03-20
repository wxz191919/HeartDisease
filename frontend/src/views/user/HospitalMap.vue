<template>
  <div class="hospital-map-container card">
    <div class="map-header">
      <h2>🗺️ 全国心血管专科医院分布与定位</h2>
      <div class="control-panel">
        <label for="province-select">选择省份/直辖市：</label>
        <select id="province-select" v-model="selectedProvince" @change="handleProvinceChange">
          <option v-for="prov in provinces" :key="prov" :value="prov">
            {{ prov }}
          </option>
        </select>
      </div>
    </div>

    <div class="map-body">
      <div class="hospital-sidebar box">
        <h3>📍 {{ selectedProvince }} 医院列表</h3>
        <div v-if="loading" class="loading-tip">正在搜索中...</div>
        <ul v-else class="hospital-list">
          <li v-for="(hospital, index) in hospitalList" :key="index" @click="focusHospital(hospital)">
            <div class="hospital-name">{{ index + 1 }}. {{ hospital.title }}</div>
            <div class="hospital-address">{{ hospital.address }}</div>
          </li>
          <li v-if="hospitalList.length === 0 && !loading" class="empty-tip">
            该区域暂无搜索结果
          </li>
        </ul>
      </div>

      <div class="map-view-wrapper">
        <div id="hospital-map"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'HospitalMap',
  setup() {
    const selectedProvince = ref('北京')
    const hospitalList = ref([])
    const loading = ref(false)
    let map = null
    let localSearch = null

    // 中国主要省份/直辖市列表
    const provinces = [
      '北京', '上海', '天津', '重庆', '广东', '浙江', '江苏', '山东', '四川', 
      '湖北', '湖南', '福建', '安徽', '河南', '河北', '辽宁', '陕西', '江西'
    ]

    // 1. 动态加载百度地图 API
    const loadBaiduMap = () => {
      return new Promise((resolve, reject) => {
        if (window.BMap) {
          resolve(window.BMap)
          return
        }
        window.initBaiduMap = () => {
          resolve(window.BMap)
        }
        const script = document.createElement('script')
        // 注意：这里用了一个公共测试用的 AK（密钥）。
        // 如果后期上线或提示配额不足，请去百度地图开放平台(lbsyun.baidu.com)免费申请一个你自己的 AK
        script.src = 'https://api.map.baidu.com/api?v=3.0&ak=YWdGplhYjUGQ3GtpKNeuTM2LNTCg41fr&callback=initBaiduMap'
        script.onerror = reject
        document.head.appendChild(script)
      })
    }

    // 2. 初始化地图与搜索服务
    const initMap = async () => {
      try {
        const BMap = await loadBaiduMap()
        
        // 创建地图实例
        map = new BMap.Map("hospital-map")
        map.centerAndZoom(selectedProvince.value, 11) // 初始化中心点和缩放级别
        map.enableScrollWheelZoom(true) // 开启鼠标滚轮缩放

        // 配置本地搜索服务
        localSearch = new BMap.LocalSearch(map, {
          onSearchComplete: (results) => {
            loading.value = false
            if (localSearch.getStatus() === window.BMAP_STATUS_SUCCESS) {
              const arr = []
              for (let i = 0; i < results.getCurrentNumPois(); i++) {
                arr.push(results.getPoi(i))
              }
              hospitalList.value = arr
            } else {
              hospitalList.value = []
            }
          }
        })

        // 首次加载触发搜索
        searchHospitals()
      } catch (error) {
        console.error("百度地图加载失败", error)
      }
    }

    // 3. 执行搜索：只搜心血管病医院
    const searchHospitals = () => {
      if (!map || !localSearch) return
      loading.value = true
      map.clearOverlays() // 清除之前的标记
      map.setCenter(selectedProvince.value) // 移动地图到所选省份
      
      // 在当前省份范围内搜索关键词
      localSearch.setLocation(selectedProvince.value)
      localSearch.search("心血管病医院")
    }

    // 4. 切换省份事件
    const handleProvinceChange = () => {
      searchHospitals()
    }

    // 5. 点击左侧列表，地图聚焦到该医院并弹出信息
    const focusHospital = (hospital) => {
      if (!map) return
      map.centerAndZoom(hospital.point, 15)
      
      const BMap = window.BMap
      const infoWindow = new BMap.InfoWindow(`地址：${hospital.address}`, {
        width: 200,
        height: 80,
        title: `<strong style="color:#e11d48">${hospital.title}</strong>`
      })
      map.openInfoWindow(infoWindow, hospital.point)
    }

    onMounted(() => {
      initMap()
    })

    return {
      selectedProvince,
      provinces,
      hospitalList,
      loading,
      handleProvinceChange,
      focusHospital
    }
  }
}
</script>

<style scoped>
/* 组件整体布局 */
.hospital-map-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px); /* 适应右侧区域高度 */
  padding: 20px;
}

/* 顶部操作栏 */
.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid rgba(148, 163, 184, 0.2);
  padding-bottom: 10px;
}

.map-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.control-panel select {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  outline: none;
}

/* 核心主体：左列表 + 右地图 */
.map-body {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden;
}

/* 左侧医院列表 */
.hospital-sidebar {
  width: 320px;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  padding: 15px;
}

.hospital-sidebar h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.1rem;
  border-bottom: 1px dashed rgba(148, 163, 184, 0.4);
  padding-bottom: 10px;
}

.hospital-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex: 1;
}

.hospital-list li {
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 6px;
  background-color: rgba(148, 163, 184, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.hospital-list li:hover {
  background-color: rgba(59, 130, 246, 0.2);
  transform: translateX(5px);
}

.hospital-name {
  font-weight: bold;
  font-size: 0.95rem;
  margin-bottom: 5px;
  color: #2563eb;
}

.hospital-address {
  font-size: 0.8rem;
  opacity: 0.8;
}

.loading-tip, .empty-tip {
  text-align: center;
  padding: 20px;
  opacity: 0.6;
}

/* 右侧地图视图 */
.map-view-wrapper {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

#hospital-map {
  width: 100%;
  height: 100%;
}

/* ★★★ 重点防护罩 ★★★ 
  为了防止我们 App.vue 里霸道的夜间模式 CSS 破坏百度地图内部的贴图和按钮，
  必须用 :deep() 强制重置地图内部的样式！
*/
:deep(#hospital-map *) {
  color: #000 !important;
  background-color: initial !important;
  border-color: initial !important;
}
</style>