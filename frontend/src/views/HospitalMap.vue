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

        <div v-if="loading" class="loading-tip">
          <i class="bi bi-hourglass-split"></i> 正在努力搜索中...
        </div>

        <div v-else-if="errorMsg" class="error-tip text-danger">
          <i class="bi bi-exclamation-triangle"></i> {{ errorMsg }}
        </div>

        <ul v-else class="hospital-list">
          <li v-for="(hospital, index) in hospitalList" :key="index" @click="focusHospital(hospital)">
            <div class="hospital-name">{{ index + 1 }}. {{ hospital.title }}</div>
            <div class="hospital-address">{{ hospital.address || '地址未知' }}</div>
          </li>
          <li v-if="hospitalList.length === 0" class="empty-tip">
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
// 1. 核心修复：引入 markRaw 和 nextTick
import { ref, onMounted, onBeforeUnmount, markRaw, nextTick } from 'vue'

export default {
  name: 'HospitalMap',
  setup() {
    const selectedProvince = ref('北京')
    const hospitalList = ref([])
    const loading = ref(true)
    const errorMsg = ref('')
    let map = null
    let localSearch = null
    let timeoutId = null

    const provinces = [
      '北京', '上海', '天津', '重庆', '广东', '浙江', '江苏', '山东', '四川',
      '湖北', '湖南', '福建', '安徽', '河南', '河北', '辽宁', '陕西', '江西'
    ]

    const loadBaiduMap = () => {
      return new Promise((resolve, reject) => {
        if (typeof window.BMap !== 'undefined') {
          resolve(window.BMap)
          return
        }

        window.initBaiduMap = () => {
          resolve(window.BMap)
        }

        const script = document.createElement('script')
        // 2. 核心修复：加上了 &callback=initBaiduMap ，否则地图根本不会初始化！
        script.src = 'https://api.map.baidu.com/api?v=3.0&ak=GCNkhnTYj6ghDhzGyq8SDczDAtRi1Nl0&callback=initBaiduMap'
        script.onerror = () => reject(new Error('百度地图脚本加载失败'))
        document.head.appendChild(script)
      })
    }

    const initMap = async () => {
      loading.value = true
      errorMsg.value = ''
      try {
        const BMap = await loadBaiduMap()
        await nextTick() // 确保网页右侧的地图框已经完全渲染

        // 3. 核心修复：用 markRaw 保护地图实例，防止 Vue3 劫持导致卡死
        const mapInstance = new BMap.Map("hospital-map")
        map = markRaw(mapInstance)

        map.centerAndZoom(selectedProvince.value, 11)
        map.enableScrollWheelZoom(true)

        // 同样保护搜索实例
        const searchInstance = new BMap.LocalSearch(map, {
          onSearchComplete: (results) => {
            clearTimeout(timeoutId) // 成功拿到数据就取消超时报错
            loading.value = false

            if (searchInstance.getStatus() === window.BMAP_STATUS_SUCCESS) {
              const arr = []
              for (let i = 0; i < results.getCurrentNumPois(); i++) {
                arr.push(results.getPoi(i))
              }
              hospitalList.value = arr
            } else {
              hospitalList.value = []
              if(searchInstance.getStatus() !== 0) {
                 errorMsg.value = '搜索接口请求失败，可能受限于百度API配额'
              }
            }
          }
        })
        localSearch = markRaw(searchInstance)

        // 延迟半秒再搜索，给引擎缓冲时间
        setTimeout(() => {
          searchHospitals()
        }, 500)

      } catch (error) {
        loading.value = false
        errorMsg.value = '地图加载失败，请检查网络或控制台报错。'
        console.error(error)
      }
    }

    const searchHospitals = () => {
      if (!map || !localSearch) return
      loading.value = true
      errorMsg.value = ''
      hospitalList.value = []

      map.clearOverlays()
      map.setCenter(selectedProvince.value)

      timeoutId = setTimeout(() => {
        if(loading.value) {
          loading.value = false
          errorMsg.value = '搜索超时，可能是网络问题或API受限'
        }
      }, 8000)

      localSearch.setLocation(selectedProvince.value)
      localSearch.search("心血管病医院")
    }

    const handleProvinceChange = () => {
      searchHospitals()
    }

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

    onBeforeUnmount(() => {
       clearTimeout(timeoutId)
    })

    return {
      selectedProvince,
      provinces,
      hospitalList,
      loading,
      errorMsg,
      handleProvinceChange,
      focusHospital
    }
  }
}
</script>

<style scoped>
.hospital-map-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  padding: 20px;
}

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
  background-color: #fff;
  color: #000;
}

.map-body {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden;
}

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
  color: #3b82f6;
}

.hospital-address {
  font-size: 0.8rem;
  opacity: 0.8;
}

.loading-tip, .empty-tip, .error-tip {
  text-align: center;
  padding: 20px;
  opacity: 0.8;
  font-weight: bold;
}

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
  min-height: 500px;
  background-color: #f3f0e8 !important;
}

:deep(#hospital-map *) {
  background-color: initial !important;
  color: #000 !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(#hospital-map img) {
  max-width: none !important;
  background-color: transparent !important;
}
</style>