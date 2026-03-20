<template>
  <div id="app">
    <canvas ref="canvasRef" class="particle-canvas"></canvas>

    <div class="app-router-view">
      <router-view />
    </div>
  </div>
</template>

<script>
// 引入 provide，把夜间模式共享给导航栏
import { ref, onMounted, onBeforeUnmount, provide } from 'vue'

export default {
  name: 'App',
  setup() {
    const canvasRef = ref(null)
    let animationFrameId = null
    const theme = ref(localStorage.getItem('theme') || 'light')

    const applyTheme = (currentTheme) => {
      document.documentElement.setAttribute('data-theme', currentTheme)
    }

    const toggleTheme = () => {
      theme.value = theme.value === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme', theme.value)
      applyTheme(theme.value)
    }

    // +++ 核心：通过 provide 将主题状态提供给子页面的导航栏 +++
    provide('globalTheme', theme)
    provide('toggleTheme', toggleTheme)
    // +++++++++++++++++++++++++++++++++++++++++++++++++++++++

    onMounted(() => {
      applyTheme(theme.value)
      const canvas = canvasRef.value
      const ctx = canvas.getContext('2d')

      const resizeCanvas = () => {
        canvas.width = window.innerWidth
        canvas.height = Math.max(window.innerHeight, document.documentElement.scrollHeight)
      }
      resizeCanvas()

      const particles = []
      const particleCount = 80
      const connectionDistance = 120

      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 1.2,
          vy: (Math.random() - 0.5) * 1.2,
          radius: Math.random() * 1.5 + 1
        })
      }

      const draw = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        const isDark = theme.value === 'dark'
        ctx.fillStyle = isDark ? 'rgba(59, 130, 246, 0.8)' : 'rgba(148, 163, 184, 0.6)'

        for (let i = 0; i < particles.length; i++) {
          let p = particles[i]
          p.x += p.vx
          p.y += p.vy
          if (p.x < 0 || p.x > canvas.width) p.vx *= -1
          if (p.y < 0 || p.y > canvas.height) p.vy *= -1

          ctx.beginPath()
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
          ctx.fill()

          for (let j = i + 1; j < particles.length; j++) {
            let p2 = particles[j]
            let dx = p.x - p2.x
            let dy = p.y - p2.y
            let dist = Math.sqrt(dx * dx + dy * dy)

            if (dist < connectionDistance) {
              ctx.beginPath()
              const opacity = 1 - (dist / connectionDistance)
              ctx.strokeStyle = isDark
                ? `rgba(59, 130, 246, ${opacity * 0.5})`
                : `rgba(148, 163, 184, ${opacity * 0.4})`
              ctx.lineWidth = 0.8
              ctx.moveTo(p.x, p.y)
              ctx.lineTo(p2.x, p2.y)
              ctx.stroke()
            }
          }
        }
        animationFrameId = requestAnimationFrame(draw)
      }
      draw()
      window.addEventListener('resize', resizeCanvas)

      onBeforeUnmount(() => {
        cancelAnimationFrame(animationFrameId)
        window.removeEventListener('resize', resizeCanvas)
      })
    })

    return { canvasRef }
  }
}
</script>

<style>
/* 基础环境配置 */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  background-color: #f1f5f9;
  color: #334155;
}

.app-router-view {
  position: relative;
  z-index: 10;
  min-height: 100vh;
}

.particle-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* 夜间模式纯颜色切换 */
[data-theme="dark"] body,
[data-theme="dark"] html {
  background-color: #0f172a !important;
}

[data-theme="dark"] * {
  color: #f1f5f9 !important;
  border-color: #334155 !important;
}

/* 保护下拉菜单不被变成透明 */
[data-theme="dark"] #app,
[data-theme="dark"] .app-router-view,
[data-theme="dark"] div:not(.custom-dropdown-menu),
[data-theme="dark"] main,
[data-theme="dark"] section,
[data-theme="dark"] nav,
[data-theme="dark"] article {
  background-color: transparent !important;
}

[data-theme="dark"] [class*="card"],
[data-theme="dark"] [class*="box"],
[data-theme="dark"] [class*="container"],
[data-theme="dark"] [class*="wrap"],
[data-theme="dark"] [class*="sidebar"],
[data-theme="dark"] [class*="menu"],
[data-theme="dark"] [class*="content"],
[data-theme="dark"] aside,
[data-theme="dark"] table,
[data-theme="dark"] th,
[data-theme="dark"] td {
  background-color: #1e293b !important;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5) !important;
}

/* 保护顶部导航栏按钮不瞎眼 */
[data-theme="dark"] button:not(.theme-btn):not(.user-btn):not(.dropdown-item) {
  background-color: #3b82f6 !important;
  color: #ffffff !important;
  border: none !important;
}

[data-theme="dark"] input,
[data-theme="dark"] select,
[data-theme="dark"] textarea {
  background-color: #0f172a !important;
  color: #ffffff !important;
  border: 1px solid #475569 !important;
}

/* 镇压 Bootstrap 自带的白色背景 */
[data-theme="dark"] .bg-white,
[data-theme="dark"] .bg-light,
[data-theme="dark"] .card,
[data-theme="dark"] .list-group-item {
  background-color: #1e293b !important;
  color: #f1f5f9 !important;
  border-color: #334155 !important;
}

[data-theme="dark"] .text-dark,
[data-theme="dark"] .text-muted {
  color: #cbd5e1 !important;
}
</style>