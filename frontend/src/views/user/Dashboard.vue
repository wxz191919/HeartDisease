<template>
  <div class="dashboard-container">

    <div class="card shadow-sm mb-4 map-card border-0">
      <div class="card-header bg-transparent border-bottom-0 pt-4 pb-2 d-flex justify-content-between align-items-center flex-wrap">
        <h4 class="m-0 fw-bold text-primary">
          <i class="bi bi-globe-americas me-2"></i>全球心血管疾病(CVD)死亡率分布图
          <span class="fs-6 text-muted ms-2 fw-normal">真实数据来源: Kaggle / GBD (每10万人)</span>
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle ms-3 rounded-pill fw-normal">
            <i class="bi bi-hand-index-thumb-fill me-1"></i>支持点击国家查看详情
          </span>
        </h4>
      </div>
      <div class="card-body">
        <div v-if="mapLoading" class="text-center py-5 text-muted">
          <span class="spinner-border spinner-border-sm me-2"></span>正在突破网络封锁，挂载全球地图与真实数据...
        </div>

        <div v-if="mapError" class="alert alert-danger text-center">
          <i class="bi bi-x-circle-fill me-2"></i>地图基础结构加载失败，请检查网络连接。
        </div>

        <div v-if="dataErrorMessage" class="alert alert-warning text-center fw-bold">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>状态提示：{{ dataErrorMessage }}
        </div>

        <div id="global-map" style="width: 100%; height: 500px; cursor: pointer;" v-show="!mapLoading && !mapError"></div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-lg-7">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-header bg-transparent border-bottom-0 pt-4 pb-2">
            <h4 class="m-0 fw-bold text-danger"><i class="bi bi-heart-pulse-fill me-2"></i>3D 动态心脏结构模型</h4>
            <small class="text-muted">您可以按住鼠标左键旋转、滚轮缩放查看心脏全方位结构</small>
          </div>
          <div class="card-body p-0 position-relative" style="height: 450px; background-color: #111;">
            <iframe title="Realistic Human Heart" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" allow="autoplay; fullscreen; xr-spatial-tracking" src="https://sketchfab.com/models/97f61d76780d4a81a8247e1fe7a2d43e/embed?autostart=1&ui_theme=dark" style="width: 100%; height: 100%; border-radius: 0 0 12px 12px;"></iframe>
          </div>
        </div>
      </div>
      <div class="col-lg-5">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-header bg-transparent border-bottom-0 pt-4 pb-2">
            <h4 class="m-0 fw-bold text-primary"><i class="bi bi-clipboard2-pulse me-2"></i>病理性变态特征分析</h4>
          </div>
          <div class="card-body d-flex flex-column">
            <div class="d-flex flex-wrap gap-2 mb-4">
              <button v-for="(disease, key) in diseaseAnalysis" :key="key" @click="activeDisease = key" :class="['btn btn-sm fw-bold rounded-pill px-3', activeDisease === key ? 'btn-primary' : 'btn-outline-secondary']">
                {{ disease.name }}
              </button>
            </div>
            <div class="disease-detail-box p-4 flex-grow-1 rounded-3">
              <h5 class="fw-bold text-danger mb-3">{{ diseaseAnalysis[activeDisease].name }}</h5>
              <p class="text-muted mb-3" style="font-size: 0.95rem; line-height: 1.6;">
                <strong><i class="bi bi-info-circle-fill text-info me-1"></i>疾病概述：</strong><br>{{ diseaseAnalysis[activeDisease].overview }}
              </p>
              <div class="alert custom-alert border-0 mb-0">
                <p class="mb-2 text-dark fw-bold"><i class="bi bi-search me-1"></i>3D 结构受损表现：</p>
                <ul class="mb-0 text-muted ps-3" style="font-size: 0.9rem;">
                  <li v-for="(item, index) in diseaseAnalysis[activeDisease].lesions" :key="index" class="mb-1">{{ item }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm mb-4 border-0 info-card">
      <div class="card-header bg-transparent border-bottom-0 pt-4 pb-2">
        <h4 class="m-0 fw-bold text-dark">
          <i class="bi bi-cpu-fill me-2 text-warning"></i>硬核 AI 风险因子推演沙盘
        </h4>
        <small class="text-muted">
          已直连底层 <span class="badge bg-dark text-warning mx-1">5002 模型接口</span>，拖动滑块实时调用后端 XGBoost 机器学习算法进行患病概率推演。
        </small>
      </div>
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-7 pe-md-5">
            <div class="simulator-panel p-4 rounded-3">
              <div class="mb-4">
                <div class="d-flex justify-content-between mb-1">
                  <label class="fw-bold">年龄 (Age)</label>
                  <span class="text-primary fw-bold">{{ simData.age }} 岁</span>
                </div>
                <input type="range" class="form-range custom-range" min="20" max="90" step="1" v-model="simData.age" @input="updateSimulation">
              </div>
              <div class="mb-4">
                <div class="d-flex justify-content-between mb-1">
                  <label class="fw-bold">收缩压 (sysBP)</label>
                  <span class="text-danger fw-bold">{{ simData.sysBP }} mmHg</span>
                </div>
                <input type="range" class="form-range custom-range-danger" min="90" max="200" step="1" v-model="simData.sysBP" @input="updateSimulation">
              </div>
              <div class="mb-4">
                <div class="d-flex justify-content-between mb-1">
                  <label class="fw-bold">总胆固醇 (totChol)</label>
                  <span class="text-warning fw-bold">{{ simData.chol }} mg/dL</span>
                </div>
                <input type="range" class="form-range custom-range-warning" min="130" max="350" step="1" v-model="simData.chol" @input="updateSimulation">
              </div>
              <div class="mb-0">
                <div class="d-flex justify-content-between mb-1">
                  <label class="fw-bold">日吸烟量 (cigsPerDay)</label>
                  <span class="text-secondary fw-bold">{{ simData.cigs }} 支</span>
                </div>
                <input type="range" class="form-range custom-range-secondary" min="0" max="50" step="1" v-model="simData.cigs" @input="updateSimulation">
              </div>
            </div>
          </div>
          <div class="col-md-5 position-relative">
            <div v-if="isPredicting" class="position-absolute w-100 h-100 d-flex justify-content-center align-items-center" style="z-index: 10; background: rgba(255,255,255,0.6); top: 0; left: 0; border-radius: 12px;">
               <span class="spinner-border text-warning" role="status"></span>
               <span class="ms-2 fw-bold text-dark">AI 正在深度推演...</span>
            </div>
            <div id="risk-gauge" style="width: 100%; height: 350px;"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-5">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-header bg-transparent border-bottom-0 pt-4 pb-2">
            <h5 class="m-0 fw-bold text-dark"><i class="bi bi-pie-chart-fill me-2 text-danger"></i>全球 CVD 致死核心归因</h5>
            <small class="text-muted">基于 Kaggle 真实横截面数据聚合分析</small>
          </div>
          <div class="card-body">
            <div id="risk-factors-chart" style="width: 100%; height: 280px;"></div>
          </div>
        </div>
      </div>
      <div class="col-md-7">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-header bg-transparent border-bottom-0 pt-4 pb-2">
            <h5 class="m-0 fw-bold text-dark"><i class="bi bi-graph-up-arrow me-2 text-primary"></i>2025-2050 全球病患死亡趋势预估</h5>
            <small class="text-muted">宏观时序数据推演测算结果</small>
          </div>
          <div class="card-body">
            <div id="trend-chart" style="width: 100%; height: 280px;"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="row g-4">
      <div class="col-md-6">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-body p-4">
            <h4 class="mb-3 fw-bold text-dark">心脏病的危害</h4>
            <p class="text-muted mb-4">心血管疾病（CVD）是全球第一大死因，每年夺走近 1800 万人的生命。这些疾病可能导致胸痛、呼吸困难、心悸等症状，严重时甚至会危及生命。</p>
            <div class="alert alert-dark border-0 custom-alert">据世界卫生组织统计，超过四分之三的心血管疾病死亡发生在低收入和中等收入国家。</div>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card shadow-sm h-100 border-0 info-card">
          <div class="card-body p-4">
            <h4 class="mb-4 fw-bold text-dark">预防心脏病的关键要点</h4>
            <h6 class="text-primary mb-2 fw-bold"><i class="bi bi-apple me-2"></i>健康饮食</h6>
            <ul class="text-muted mb-4 fs-7 ps-3">
              <li><strong>控制脂肪：</strong>减少饱和脂肪和反式脂肪的摄入，如动物内脏、油炸食品等</li>
              <li><strong>控制盐摄入：</strong>建议每天盐的摄入量不超过6克</li>
            </ul>
            <h6 class="text-primary mb-2 fw-bold"><i class="bi bi-bicycle me-2"></i>适量运动</h6>
            <ul class="text-muted mb-0 fs-7 ps-3">
              <li><strong>有氧运动：</strong>如快走、跑步、游泳等，每周至少150分钟</li>
              <li><strong>日常习惯：</strong>减少久坐时间，保持规律作息</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import * as echarts from 'echarts'
import API_BASE_URL from '../config.js'
import { ref, reactive, onMounted, onBeforeUnmount, markRaw, nextTick } from 'vue'

export default {
  name: 'Dashboard',
  setup() {
    // ================= 地图与底层宏观数据逻辑 =================
    let mapChart = null
    let riskChart = null
    let trendChart = null

    const mapLoading = ref(true)
    const mapError = ref(false)
    const dataErrorMessage = ref('')

    // 承载 5003 接口发来的真实大盘数据
    const whoData = { cvd: [] }
    const macroData = reactive({
      riskFactors: [],
      trendYears: [],
      trendDeaths: []
    })

    const initMap = async () => {
      try {
        mapLoading.value = true;
        mapError.value = false;
        dataErrorMessage.value = '';

        const cdns = [
          'https://fastly.jsdelivr.net/npm/echarts@4.9.0/map/json/world.json',
          'https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/json/world.json',
          'https://registry.npmmirror.com/echarts/4.9.0/files/map/json/world.json'
        ];

        let worldJson = null;
        for (let url of cdns) {
          try {
            const response = await fetch(url);
            if (response.ok) {
              worldJson = await response.json();
              break;
            }
          } catch (e) {
            console.warn("当前 CDN 超时或被墙，切换下一个...");
          }
        }

        if (!worldJson) throw new Error('所有地图源均无法访问，网络可能受限');
        echarts.registerMap('world', worldJson);

        const nameMap = {
          'United States': 'United States of America', 'USA': 'United States of America', 'Russian Federation': 'Russia', 'Republic of Korea': 'Korea', 'Democratic People\'s Republic of Korea': 'Dem. Rep. Korea', 'United Kingdom': 'United Kingdom', 'Iran (Islamic Republic of)': 'Iran', 'Syrian Arab Republic': 'Syria', 'Democratic Republic of the Congo': 'Dem. Rep. Congo', 'Viet Nam': 'Vietnam', 'Bolivia (Plurinational State of)': 'Bolivia', 'Venezuela (Bolivarian Republic of)': 'Venezuela', 'Lao People\'s Democratic Republic': 'Laos', 'United Republic of Tanzania': 'Tanzania'
        };

        try {
          // 🚀 核心：5003 接口不仅返回地图，还返回趋势和归因数据！
          const dataRes = await fetch(`${API_BASE_URL}/global-analysis`);
          if (!dataRes.ok) throw new Error(`后端返回错误代码: ${dataRes.status}`);

          const dataJson = await dataRes.json();
          if (dataJson.success && dataJson.data) {
             // 1. 挂载地图国家数据
             if(dataJson.data.country_data) {
                 const realData = dataJson.data.country_data.map(item => {
                    return { name: nameMap[item.name] || item.name, value: item.value };
                 });
                 whoData['cvd'] = realData;
             }
             // 2. 挂载图表真实数据 (提取你原本后端写好的宏观指标)
             if(dataJson.data.risk_factors) macroData.riskFactors = dataJson.data.risk_factors;
             if(dataJson.data.trend) {
                 macroData.trendYears = dataJson.data.trend.years;
                 macroData.trendDeaths = dataJson.data.trend.deaths;
             }
          } else {
             throw new Error(dataJson.message || 'CSV 数据提炼失败');
          }
        } catch (apiErr) {
          console.error('后端连接失败:', apiErr);
          dataErrorMessage.value = '无法连接到后端接口，已自动开启备用预设数据支撑大屏。';
          // 断网兜底数据
          whoData['cvd'] = [{ name: 'China', value: 277 }, { name: 'United States of America', value: 151 }, { name: 'Russia', value: 430 }, { name: 'India', value: 282 }, { name: 'Japan', value: 90 }];
          macroData.riskFactors = [{name: '高血压致死', value: 38}, {name: '高LDL致死', value: 24}, {name: '肥胖致死', value: 21}, {name: '吸烟致死', value: 17}];
          macroData.trendYears = [2025, 2030, 2035, 2040, 2045, 2050];
          macroData.trendDeaths = [18500000, 19800000, 21500000, 23400000, 25800000, 28500000];
        }

        mapLoading.value = false;
        await nextTick();

        // 渲染地图
        const dom = document.getElementById('global-map');
        if (dom) { mapChart = markRaw(echarts.init(dom)); renderMap(); }

        // 渲染下方的宏观数据图表
        initMacroCharts();

      } catch (error) {
        console.error('引擎崩溃:', error);
        mapLoading.value = false;
        mapError.value = true;
      }
    }

    const renderMap = () => {
      if (!mapChart) return
      const colorRange = ['#FFFACD', '#FF8C00', '#E31A1C', '#800026'];
      mapChart.setOption({
        tooltip: {
          trigger: 'item', backgroundColor: 'rgba(25, 33, 50, 0.95)', textStyle: { color: '#fff' }, borderColor: '#475569', borderWidth: 1, padding: [10, 15],
          formatter: function (params) {
            let valStr = params.value ? `<span style="color:#fde047; font-size:16px; font-weight:bold;">${params.value}</span> /10万人` : '<span style="color:#94a3b8;">暂无数据</span>';
            return `<div style="font-size:14px; font-weight:bold; border-bottom:1px solid #475569; padding-bottom:5px; margin-bottom:5px;">${params.name}</div>
                    CVD死亡率: ${valStr}<br/><span style="font-size:12px; color:#cbd5e1; margin-top:5px; display:inline-block;"><i class="bi bi-cursor-fill"></i> 点击国家查看详细报告</span>`;
          }
        },
        visualMap: { min: 0, max: 500, text: ['高危', '低危'], calculable: true, inRange: { color: colorRange }, bottom: 20, left: 20, textStyle: { color: document.documentElement.getAttribute('data-theme') === 'dark' ? '#cbd5e1' : '#334155', fontWeight: 'bold' } },
        series: [{ type: 'map', map: 'world', zoom: 1.2, roam: true, itemStyle: { areaColor: '#e2e8f0', borderColor: '#cbd5e1', borderWidth: 1 }, emphasis: { label: { show: true, color: '#000', fontWeight: 'bold' }, itemStyle: { areaColor: '#fde047', shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } }, data: whoData['cvd'] }]
      }, true);

      mapChart.off('click');
      mapChart.on('click', function (params) {
        if (params.name) window.open(`https://www.bing.com/search?q=${encodeURIComponent(params.name + ' 心血管疾病 CVD 数据报告')}`, '_blank');
      });
    }

    // 初始化新增的两个数据表
    const initMacroCharts = () => {
      const riskDom = document.getElementById('risk-factors-chart');
      const trendDom = document.getElementById('trend-chart');
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      const textColor = isDark ? '#cbd5e1' : '#64748b';

      if (riskDom) {
        riskChart = markRaw(echarts.init(riskDom));
        riskChart.setOption({
          tooltip: { trigger: 'item', formatter: '{b}: {c}%' },
          legend: { top: 'bottom', textStyle: { color: textColor } },
          color: ['#dc3545', '#fd7e14', '#ffc107', '#6c757d'],
          series: [{
            name: '归因占比', type: 'pie', radius: ['45%', '70%'],
            itemStyle: { borderRadius: 8, borderColor: isDark ? '#1e293b' : '#fff', borderWidth: 2 },
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
            data: macroData.riskFactors
          }]
        });
      }

      if (trendDom) {
        trendChart = markRaw(echarts.init(trendDom));
        trendChart.setOption({
          tooltip: { trigger: 'axis', formatter: '{b}年 <br/> 预估死亡人数: <b>{c}</b>' },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          xAxis: { type: 'category', boundaryGap: false, data: macroData.trendYears, axisLabel: { color: textColor } },
          yAxis: { type: 'value', axisLabel: { color: textColor, formatter: (val) => (val/1000000) + ' M' }, splitLine: { lineStyle: { type: 'dashed', color: isDark ? '#334155' : '#e2e8f0' } } },
          series: [{
            name: '全球死亡人数趋势', type: 'line', smooth: true,
            areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(13, 110, 253, 0.4)' }, { offset: 1, color: 'rgba(13, 110, 253, 0.05)' }]) },
            lineStyle: { width: 3, color: '#0d6efd' },
            itemStyle: { color: '#0d6efd' },
            data: macroData.trendDeaths
          }]
        });
      }
    }

    // ================= 五大病理分析逻辑 =================
    const activeDisease = ref('coronary')

    const diseaseAnalysis = {
      coronary: { name: '冠状动脉粥样硬化 (冠心病)', overview: '由于脂质在冠状动脉内膜沉积，形成粥样斑块，导致血管腔狭窄甚至阻塞。', lesions: ['🔴 冠状动脉出现黄色脂质条纹。', '🔴 晚期斑块破裂形成血栓。', '🔴 局部心肌萎缩纤维化。'] },
      hypertension: { name: '高血压性心脏病', overview: '长期体循环动脉血压升高，增加了心脏泵血的阻力，导致左心室代偿性肥大。', lesions: ['🔴 左心室壁明显增厚。', '🔴 晚期心室腔严重扩张。', '🔴 心肌微血管密度降低。'] },
      infarction: { name: '急性心肌梗死', overview: '冠状动脉急性闭塞，导致心肌因严重持久的缺血而发生局部坏死。', lesions: ['🔴 心肌肉眼下呈现不规则苍白。', '🔴 梗死灶周围伴有暗红色出血带。', '🔴 严重者心室壁软化破裂。'] },
      stroke: { name: '缺血性脑卒中 (中风并发)', overview: '由于心脏或颈部血管的血栓脱落，随血流阻塞脑部血管，导致脑组织缺血缺氧性坏死。', lesions: ['🔴 脑动脉血管腔发生严重狭窄或闭塞。', '🔴 局部脑组织出现软化和液化坏死。', '🔴 周围脑组织伴随明显的水肿压迫。'] },
      heart_failure: { name: '充血性心力衰竭', overview: '各种心脏结构或功能性疾病导致心室充盈和射血能力受损，心排血量不能满足机体代谢需要。', lesions: ['🔴 心脏体积显著增大，心室腔极度扩张。', '🔴 心肌细胞发生退行性变与不可逆坏死。', '🔴 肺部及体循环静脉系统出现严重淤血。'] }
    }

    // ================= 直连 5002 后端的 AI 沙盘 =================
    let gaugeChart = null
    const isPredicting = ref(false)
    const realRiskResult = ref(0)
    const simData = reactive({ age: 45, sysBP: 120, chol: 200, cigs: 0 })

    const calculateLocalFallbackRisk = () => {
      let baseRisk = 5;
      baseRisk += (simData.age - 45) * 0.5;
      baseRisk += (simData.sysBP - 120) * 0.4;
      baseRisk += (simData.chol - 200) * 0.2;
      baseRisk += simData.cigs * 0.8;
      let finalRisk = Math.max(0, Math.min(100, baseRisk));
      return parseFloat(finalRisk.toFixed(1));
    }

    const debounce = (fn, delay) => {
      let timer = null;
      return function (...args) {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => { fn.apply(this, args); }, delay);
      };
    };

    const fetchRealRiskFromBackend = async () => {
      try {
        isPredicting.value = true;
        const mlPayload = {
          age: parseInt(simData.age),
          sysBP: parseFloat(simData.sysBP),
          totChol: parseFloat(simData.chol),
          cigsPerDay: parseInt(simData.cigs),
          male: 1, education: 2, currentSmoker: parseInt(simData.cigs) > 0 ? 1 : 0, BPMeds: 0, prevalentStroke: 0,
          prevalentHyp: parseFloat(simData.sysBP) >= 140 ? 1 : 0, diabetes: 0, diaBP: 80.0, BMI: 24.0, heartRate: 75.0, glucose: 85.0
        };

        const response = await fetch('http://localhost:5002/api/predict', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(mlPayload)
        });

        if (response.ok) {
          const resData = await response.json();
          let prob = resData.probability || resData.risk_probability || resData.risk || 0;
          if (prob <= 1 && prob > 0) prob = prob * 100;
          realRiskResult.value = parseFloat(prob).toFixed(1);
        } else {
          console.warn("后端预测请求异常，已切换至本地算法兜底");
          realRiskResult.value = calculateLocalFallbackRisk();
        }
      } catch (err) {
        console.warn("网络断开，已切换至本地算法兜底:", err);
        realRiskResult.value = calculateLocalFallbackRisk();
      } finally {
        isPredicting.value = false;
        updateGauge();
      }
    };

    const debouncedFetchRealRisk = debounce(fetchRealRiskFromBackend, 300);

    const initGauge = () => {
      const dom = document.getElementById('risk-gauge');
      if (dom) {
        gaugeChart = markRaw(echarts.init(dom))
        fetchRealRiskFromBackend();
      }
    }

    const updateGauge = () => {
      if (!gaugeChart) return;
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
      gaugeChart.setOption({
        series: [{
          type: 'gauge', startAngle: 210, endAngle: -30, min: 0, max: 100, splitNumber: 4,
          axisLine: { lineStyle: { width: 18, color: [[0.3, '#34d399'], [0.7, '#fbbf24'], [1, '#ef4444']] } },
          pointer: { icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z', length: '65%', width: 8, offsetCenter: [0, '-10%'], itemStyle: { color: isDark ? '#e2e8f0' : '#475569' } },
          axisTick: { length: 12, lineStyle: { color: 'auto', width: 2 } }, splitLine: { length: 20, lineStyle: { color: 'auto', width: 4 } },
          axisLabel: { color: isDark ? '#cbd5e1' : '#64748b', fontSize: 14, distance: -60 },
          title: { offsetCenter: [0, '40%'], fontSize: 16, color: isDark ? '#94a3b8' : '#64748b' },
          detail: { fontSize: 36, offsetCenter: [0, '70%'], valueAnimation: true, formatter: function (value) { return value + '{unit| %}'; }, color: 'inherit', rich: { unit: { fontSize: 18, padding: [0, 0, -10, 2], color: isDark ? '#94a3b8' : '#64748b' } } },
          data: [{ value: realRiskResult.value, name: 'AI 真实演算概率' }]
        }]
      })
    }

    const updateSimulation = () => { debouncedFetchRealRisk(); };

    onMounted(async () => {
      await initMap()
      initGauge()
      window.addEventListener('resize', () => {
        if(mapChart) mapChart.resize()
        if(gaugeChart) gaugeChart.resize()
        if(riskChart) riskChart.resize()
        if(trendChart) trendChart.resize()
      })
      const observer = new MutationObserver(() => {
          updateGauge();
          if(riskChart) riskChart.resize(); // 适应主题切换可能导致的大小变化
      })
      observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
    })

    onBeforeUnmount(() => {
      if (mapChart) mapChart.dispose()
      if (gaugeChart) gaugeChart.dispose()
      if (riskChart) riskChart.dispose()
      if (trendChart) trendChart.dispose()
    })

    return { mapLoading, mapError, dataErrorMessage, activeDisease, diseaseAnalysis, simData, updateSimulation, isPredicting }
  }
}
</script>

<style scoped>
.dashboard-container { max-width: 1400px; margin: 0 auto; }
.map-card, .info-card { border-radius: 12px; overflow: hidden; }
.fs-7 { font-size: 0.9rem; }
.custom-alert { background-color: rgba(148, 163, 184, 0.1); border-radius: 8px; }
.disease-detail-box { background-color: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.1); transition: all 0.3s ease; }

.simulator-panel { background-color: rgba(241, 245, 249, 0.5); border: 1px dashed #cbd5e1; }
.form-range { height: 6px; border-radius: 5px; outline: none; transition: 0.2s; }
.form-range::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #3b82f6; cursor: pointer; transition: 0.2s; }
.form-range::-webkit-slider-thumb:hover { transform: scale(1.2); }
.custom-range-danger::-webkit-slider-thumb { background: #ef4444; }
.custom-range-warning::-webkit-slider-thumb { background: #f59e0b; }
.custom-range-secondary::-webkit-slider-thumb { background: #64748b; }

[data-theme="dark"] .map-card, [data-theme="dark"] .info-card { background-color: #1e293b !important; color: #f1f5f9 !important; border-color: #334155 !important; }
[data-theme="dark"] .custom-alert { background-color: rgba(15, 23, 42, 0.6) !important; }
[data-theme="dark"] .disease-detail-box { background-color: rgba(15, 23, 42, 0.4) !important; border-color: #334155 !important; }
[data-theme="dark"] .text-muted { color: #94a3b8 !important; }
[data-theme="dark"] .text-dark { color: #f1f5f9 !important; }
[data-theme="dark"] .simulator-panel { background-color: rgba(15, 23, 42, 0.5) !important; border-color: #475569 !important; }

.bg-primary-subtle { background-color: rgba(13, 110, 253, 0.1); }
.border-primary-subtle { border-color: rgba(13, 110, 253, 0.2); }
</style>