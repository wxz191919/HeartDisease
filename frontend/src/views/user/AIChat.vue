<template>
  <div class="chat-container d-flex flex-column h-100">
    <div class="chat-header p-3 bg-white shadow-sm d-flex align-items-center justify-content-between rounded-top-3">
      <div class="d-flex align-items-center">
        <div class="avatar bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-3" style="width: 45px; height: 45px;">
          <i class="bi bi-robot fs-4"></i>
        </div>
        <div>
          <h5 class="m-0 fw-bold text-dark">Cardio-AI 智能问诊大模型</h5>
          <small class="text-success"><i class="bi bi-circle-fill me-1" style="font-size: 0.5rem;"></i>在线 · 基于百万级医疗文献训练</small>
        </div>
      </div>
      <button class="btn btn-outline-secondary btn-sm rounded-pill" @click="clearChat">
        <i class="bi bi-trash3 me-1"></i>清空对话
      </button>
    </div>

    <div class="chat-body flex-grow-1 p-4 overflow-auto" ref="chatBody">
      <div v-for="(msg, index) in messageList" :key="index" :class="['message-wrapper mb-4 d-flex', msg.role === 'user' ? 'justify-content-end' : 'justify-content-start']">

        <div v-if="msg.role === 'ai'" class="me-3 mt-1 flex-shrink-0">
          <div class="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center" style="width: 35px; height: 35px;">
            <i class="bi bi-robot"></i>
          </div>
        </div>

        <div :class="['message-bubble p-3 rounded-4 shadow-sm', msg.role === 'user' ? 'bg-primary text-white user-bubble' : 'bg-white text-dark ai-bubble']" style="max-width: 75%;">
          <div style="white-space: pre-wrap; line-height: 1.6;">{{ msg.content }}</div>
        </div>

        <div v-if="msg.role === 'user'" class="ms-3 mt-1 flex-shrink-0">
          <div class="bg-secondary text-white rounded-circle d-flex justify-content-center align-items-center" style="width: 35px; height: 35px;">
            <i class="bi bi-person"></i>
          </div>
        </div>
      </div>

      <div v-if="isTyping" class="message-wrapper mb-4 d-flex justify-content-start">
        <div class="me-3 mt-1 flex-shrink-0">
          <div class="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center" style="width: 35px; height: 35px;">
            <i class="bi bi-robot"></i>
          </div>
        </div>
        <div class="message-bubble p-3 rounded-4 shadow-sm bg-white text-dark ai-bubble d-flex align-items-center">
          <div class="typing-dot me-1"></div>
          <div class="typing-dot me-1"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    </div>

    <div class="chat-footer p-3 bg-white shadow-sm rounded-bottom-3">
      <div class="quick-questions mb-3 d-flex gap-2 overflow-auto pb-1">
        <span class="badge rounded-pill border border-primary text-primary px-3 py-2 cursor-pointer custom-badge" @click="sendQuickMsg('我的收缩压是150，这算高吗？应该怎么缓解？')">
          🩸 血压150算高吗？
        </span>
        <span class="badge rounded-pill border border-primary text-primary px-3 py-2 cursor-pointer custom-badge" @click="sendQuickMsg('如何通过饮食降低总胆固醇？')">
          🥗 如何降低胆固醇？
        </span>
        <span class="badge rounded-pill border border-primary text-primary px-3 py-2 cursor-pointer custom-badge" @click="sendQuickMsg('经常熬夜会增加得心脏病的概率吗？')">
          🌙 熬夜对心脏的危害？
        </span>
      </div>

      <div class="input-group">
        <textarea
          class="form-control rounded-start-4 border-end-0 shadow-none ps-4 py-3"
          rows="1"
          placeholder="向 Cardio-AI 描述您的健康疑惑..."
          v-model="inputText"
          @keydown.enter.prevent="handleSend"
          style="resize: none;"
        ></textarea>
        <button class="btn btn-primary rounded-end-4 px-4 fw-bold" @click="handleSend" :disabled="!inputText.trim() || isTyping">
          <i class="bi bi-send-fill me-1"></i> 发送
        </button>
      </div>
      <div class="text-center mt-2">
        <small class="text-muted" style="font-size: 0.75rem;">AI 生成的医疗建议仅供参考，不能代替专业医生的诊断。</small>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'

export default {
  name: 'AIChat',
  setup() {
    const inputText = ref('')
    const isTyping = ref(false)
    const chatBody = ref(null)

    const messageList = ref([
      { role: 'ai', content: '您好！我是接入了 DeepSeek 大模型的 Cardio-AI 智能健康助手。请问今天有什么我可以帮您的？' }
    ])

    const scrollToBottom = async () => {
      await nextTick()
      if (chatBody.value) {
        chatBody.value.scrollTop = chatBody.value.scrollHeight
      }
    }

    const clearChat = () => {
      messageList.value = [
        { role: 'ai', content: '对话已清空。您可以开始新的健康咨询。' }
      ]
    }

    const sendQuickMsg = (msg) => {
      if (isTyping.value) return
      inputText.value = msg
      handleSend()
    }

    const handleSend = async () => {
      const text = inputText.value.trim()
      if (!text || isTyping.value) return

      // 把用户的话推入界面
      messageList.value.push({ role: 'user', content: text })
      inputText.value = ''
      scrollToBottom()

      // 显示正在思考的动画
      isTyping.value = true
      scrollToBottom()

      // 发起真实的 DeepSeek API 请求
      await fetchDeepSeekResponse()
    }

    // 🚀 核心升级：真实调用 DeepSeek 大模型接口
    const fetchDeepSeekResponse = async () => {
      // ⚠️⚠️⚠️ 请把下面这行换成你申请的真实 API Key ⚠️⚠️⚠️
      const apiKey = 'sk-513768d242da4afdbbdee96ec7a6da59';

      try {
        // 1. 整理历史对话记录给 AI (DeepSeek 需要 system, user, assistant 这三种角色)
        const messagesForAPI = [
          // 先给 AI 设定一个专家人设
          { role: 'system', content: '你是一个专业的心血管疾病AI医生助手，回答要专业、严谨、易懂，带有人文关怀。尽量分点作答。' }
        ];

        // 把页面上的历史聊天记录转换成 API 能听懂的格式
        messageList.value.forEach(msg => {
          if (msg.content) {
            messagesForAPI.push({
              role: msg.role === 'ai' ? 'assistant' : 'user',
              content: msg.content
            })
          }
        });

        // 2. 发送网络请求给 DeepSeek 服务器
        const response = await fetch('https://api.deepseek.com/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            model: 'deepseek-chat', // 使用 deepseek V3 核心模型
            messages: messagesForAPI,
            temperature: 0.7 // 创造力参数，0.7 比较适合医疗咨询的严谨性
          })
        });

        if (!response.ok) {
          throw new Error('API 请求失败');
        }

        const data = await response.json();
        // 获取 AI 真实的回复内容
        const realAiAnswer = data.choices[0].message.content;

        // 3. 把真实的回复用打字机特效显示出来
        playTypewriterEffect(realAiAnswer);

      } catch (error) {
        console.error('AI接口报错:', error);
        playTypewriterEffect('抱歉，网络连接异常或 API 密钥未配置正确，请检查您的网络或 API Key 设置。');
      }
    }

    // 打字机特效函数 (让字一个一个蹦出来)
    const playTypewriterEffect = (fullResponse) => {
      isTyping.value = false

      messageList.value.push({ role: 'ai', content: '' })
      const currentMsg = messageList.value[messageList.value.length - 1]

      let i = 0
      const typingInterval = setInterval(() => {
        if (i < fullResponse.length) {
          currentMsg.content += fullResponse.charAt(i)
          i++
          scrollToBottom()
        } else {
          clearInterval(typingInterval)
        }
      }, 20) // 打字速度，数字越小越快
    }

    return {
      inputText,
      messageList,
      isTyping,
      chatBody,
      handleSend,
      sendQuickMsg,
      clearChat
    }
  }
}
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 120px) !important;
  max-width: 1200px;
  margin: 0 auto;
}

.chat-header {
  border-bottom: 1px solid #e2e8f0;
}

.chat-body {
  background-color: #f8fafc;
}

.user-bubble {
  border-bottom-right-radius: 4px !important;
}

.ai-bubble {
  border-bottom-left-radius: 4px !important;
  border: 1px solid #e2e8f0;
}

.custom-badge {
  background-color: transparent;
  transition: all 0.2s;
}
.custom-badge:hover {
  background-color: #3b82f6;
  color: white !important;
}
.cursor-pointer {
  cursor: pointer;
}

/* 正在输入的三个跳动小圆点 */
.typing-dot {
  width: 8px;
  height: 8px;
  background-color: #94a3b8;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 夜间模式适配 */
[data-theme="dark"] .bg-white { background-color: #1e293b !important; }
[data-theme="dark"] .chat-body { background-color: transparent !important; }
[data-theme="dark"] .ai-bubble { background-color: #334155 !important; border-color: #475569 !important; color: #f1f5f9 !important; }
[data-theme="dark"] .chat-header { border-bottom-color: #334155 !important; }
[data-theme="dark"] .text-dark { color: #f1f5f9 !important; }
[data-theme="dark"] .form-control { background-color: #0f172a !important; color: #f1f5f9 !important; border-color: #475569 !important; }
</style>