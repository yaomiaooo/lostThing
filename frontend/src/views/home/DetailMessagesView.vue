<template>
  <teleport to="body">
    <transition name="dialog-fade">
      <div v-if="visible" class="chat-dialog-mask" @click.self="closeDialog">
        <div class="chat-dialog">
          <!-- 对话框头部 -->
          <div class="chat-header">
            <div class="chat-title">
              <span class="participant-role">{{ dialogTitle }}</span>
              <span class="chat-hint">仅可沟通物品相关事宜，违规消息将被禁止发送</span>
            </div>
            <button class="close-btn" @click="closeDialog">×</button>
          </div>
          
          <!-- 消息区域 -->
          <div class="chat-messages" ref="chatMessagesRef">
            <div 
              v-for="message in messages" 
              :key="message.id"
              class="message-item"
              :class="{ 'own-message': message.isOwn, 'system-message': message.type === 2 }"
            >
              <div class="message-content">
                {{ message.content }}
              </div>
              <div class="message-time">
                {{ formatMessageTime(message.createTime) }}
              </div>
            </div>
            <div v-if="messages.length === 0" class="no-messages">
              暂无消息，开始沟通吧
            </div>
          </div>
          
          <!-- 输入区域 -->
          <div class="chat-input-area">
            <textarea 
              v-model="inputText" 
              placeholder="请输入与物品相关的消息..."
              :rows="2"
              maxlength="200"
              @keydown.enter.prevent="sendMessage"
              @input="validateMessage"
              ref="chatInputRef"
            ></textarea>
            <button 
              class="send-btn" 
              :disabled="!canSend"
              @click="sendMessage"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed, onMounted } from 'vue'
import axios from 'axios'

// ==================== Props & Emits ====================
interface Props {
  visible: boolean
  itemId: number
  conversationId?: number
  dialogTitle: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ==================== 状态管理 ====================
const messages = ref<any[]>([])
const inputText = ref('')
const canSend = ref(true)
const currentConversationId = ref<number | null>(props.conversationId || null)
const chatMessagesRef = ref<HTMLElement | null>(null)
const chatInputRef = ref<HTMLTextAreaElement | null>(null)
const isLoading = ref(false)
const itemOwnerInfo = ref<{userId: number, userRole: number} | null>(null)

// ==================== 计算属性 ====================
const currentUser = computed(() => {
  const userId = sessionStorage.getItem('userId')
  const userRole = sessionStorage.getItem('role')
  const realName = sessionStorage.getItem('realName')
  if (!userId || !userRole) return null
  return {
    id: parseInt(userId),
    role: parseInt(userRole),
    realName: realName || '',
    username: userId,
    phone: '',
    status: 1
  }
})

// ==================== 生命周期 ====================
onMounted(() => {
  if (props.visible) {
    initDialog()
  }
})

watch(() => props.visible, async (newVal) => {
  if (newVal) {
    await initDialog()
  } else {
    resetDialog()
  }
})

watch(() => props.conversationId, (newId) => {
  if (newId && props.visible) {
    currentConversationId.value = newId
    loadMessages()
  }
})

// ==================== 对话框操作 ====================
const closeDialog = () => {
  emit('update:visible', false)
  emit('close')
}

const resetDialog = () => {
  messages.value = []
  inputText.value = ''
  isLoading.value = false
}

const initDialog = async () => {
  if (isLoading.value) return
  
  isLoading.value = true
  await nextTick()
  
  // 首先检查物品信息，获取发布者信息
  await checkItemInfo()
  
  // 如果有conversationId，直接加载消息
  if (currentConversationId.value) {
    await loadMessages()
  } 
  // 如果没有conversationId，检查是否可以创建对话
  else if (props.itemId) {
    await checkAndCreateConversation()
  }
  
  focusInput()
  scrollToBottom()
  isLoading.value = false
}

const focusInput = () => {
  nextTick(() => {
    chatInputRef.value?.focus()
  })
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = chatMessagesRef.value
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

// ==================== 物品信息检查 ====================
const checkItemInfo = async () => {
  if (!props.itemId || !currentUser.value) return
  
  try {
    const res = await axios.get(`/api/item/info`, {
      params: { itemId: props.itemId }
    })
    
    if (res.data.code === 0 || res.data.code === 200) {
      const itemData = res.data.data
      itemOwnerInfo.value = {
        userId: itemData.userId || itemData.publisherId,
        userRole: itemData.userRole || 0
      }
      
      console.log('物品信息:', itemData, '当前用户:', currentUser.value.id)
    }
  } catch (error) {
    console.error('获取物品信息失败:', error)
  }
}

// ==================== 对话管理 ====================
const checkAndCreateConversation = async () => {
  if (!props.itemId || !currentUser.value) return
  
  // 首先检查是否已有对话存在
  try {
    const checkRes = await axios.get('/api/chat/conversation/check', {
      params: { 
        itemId: props.itemId,
        userId: currentUser.value.id
      }
    })
    
    if (checkRes.data.code === 0 && checkRes.data.data?.conversationId) {
      // 已有对话，使用现有对话ID
      currentConversationId.value = checkRes.data.data.conversationId
      await loadMessages()
      return
    }
  } catch (error) {
    console.warn('检查对话失败，尝试创建新对话:', error)
  }
  
  // 没有现有对话，检查是否可以创建新对话
  await createNewConversation()
}

const createNewConversation = async () => {
  // 检查是否是自己的物品
  if (itemOwnerInfo.value && currentUser.value) {
    if (itemOwnerInfo.value.userId === currentUser.value.id) {
      // 不能与自己发起对话
      showErrorMessage('不能与自己发起对话')
      closeDialog()
      return
    }
  }
  
  try {
    const enterRes = await axios.post('/api/chat/conversation/enter', { 
      itemId: props.itemId 
    })
    
    if (enterRes.data.code === 0) {
      currentConversationId.value = enterRes.data.data.conversationId
      await loadMessages()
    } else {
      const errorMsg = enterRes.data.message || enterRes.data.msg || '进入对话失败'
      if (errorMsg.includes('自己') || errorMsg.includes('本人')) {
        showErrorMessage('不能与自己发起对话')
        closeDialog()
      } else {
        showErrorMessage(`进入对话失败: ${errorMsg}`)
      }
    }
  } catch (e) {
    showErrorMessage('网络错误，请检查网络连接后重试')
  }
}

const loadMessages = async () => {
  if (!currentConversationId.value) return
  
  try {
    const messagesRes = await axios.get('/api/chat/conversation/messages', { 
      params: { conversationId: currentConversationId.value } 
    })
    
    if (messagesRes.data.code === 0) {
      let rawMessages = messagesRes.data.data
      
      // 处理不同类型的返回数据
      if (!Array.isArray(rawMessages)) {
        if (rawMessages && typeof rawMessages === 'object') {
          rawMessages = rawMessages.messages || rawMessages.list || []
        } else {
          rawMessages = []
        }
      }
      
      if (Array.isArray(rawMessages)) {
        messages.value = rawMessages.map((msg: any) => ({
          ...msg,
          isOwn: msg.senderId === currentUser.value?.id
        }))
      } else {
        console.warn('消息数据格式异常:', rawMessages)
        messages.value = []
      }
      
      scrollToBottom()
    }
  } catch (e) {
    console.error('加载消息失败', e)
  }
}

// ==================== 消息发送 ====================
const sendMessage = async () => {
  if (!inputText.value.trim() || !currentConversationId.value) {
    if (!currentConversationId.value) {
      showErrorMessage('对话未建立，无法发送消息')
    }
    return
  }
  
  try {
    const sendRes = await axios.post('/api/chat/conversation/message/send', { 
      conversationId: currentConversationId.value, 
      content: inputText.value.trim() 
    })
    
    if (sendRes.data.code === 0) {
      inputText.value = ''
      await loadMessages()
      focusInput()
    } else {
      const errorMsg = sendRes.data.message || sendRes.data.msg || '发送失败'
      
      // 如果是权限错误，重新检查对话状态
      if (errorMsg.includes('权限') || errorMsg.includes('不允许') || errorMsg.includes('无效')) {
        showErrorMessage('对话状态异常，请重新打开')
        // 重置对话状态，重新加载
        currentConversationId.value = null
        await initDialog()
      } else {
        showErrorMessage(`消息发送失败: ${errorMsg}`)
      }
    }
  } catch (e) {
    showErrorMessage('网络错误，请检查网络连接后重试')
  }
}

const validateMessage = () => {
  const content = inputText.value.trim()
  const forbiddenKeywords = ['广告', '骚扰', '违法', '垃圾', '诈骗']
  canSend.value = content.length > 0 && 
                  content.length <= 200 && 
                  !forbiddenKeywords.some(k => content.includes(k))
}

// ==================== 工具函数 ====================
const formatMessageTime = (timeStr: string) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    const now = new Date()
    if (date.toDateString() === now.toDateString()) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }
    const diff = now.getTime() - date.getTime()
    if (diff < 24 * 60 * 60 * 1000) {
      return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }
    return date.toLocaleDateString('zh-CN')
  } catch {
    return timeStr
  }
}

const showErrorMessage = (message: string) => {
  // 这里可以使用更友好的提示方式，如Element UI的Message
  console.error(message)
  alert(message)
}
</script>

<style scoped>
.chat-dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.chat-dialog {
  background: white;
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.chat-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.participant-role {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.chat-hint {
  font-size: 12px;
  color: #666;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 400px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}

.message-item.own-message {
  align-self: flex-end;
  align-items: flex-end;
}

.message-item.system-message {
  align-self: center;
  align-items: center;
  max-width: 90%;
}

.message-content {
  background: #f0f0f0;
  padding: 8px 12px;
  border-radius: 12px;
  word-break: break-word;
  line-height: 1.4;
}

.own-message .message-content {
  background: #007bff;
  color: white;
}

.system-message .message-content {
  background: #ffc107;
  color: #333;
  font-size: 12px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

.no-messages {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 40px 0;
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input-area textarea {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
}

.chat-input-area textarea:focus {
  outline: none;
  border-color: #007bff;
}

.send-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  cursor: pointer;
  font-size: 14px;
  min-width: 60px;
}

.send-btn:hover:not(:disabled) {
  background: #0056b3;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 过渡动画 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-active .chat-dialog,
.dialog-fade-leave-active .chat-dialog {
  transition: transform 0.3s ease;
}

.dialog-fade-enter-from .chat-dialog,
.dialog-fade-leave-to .chat-dialog {
  transform: scale(0.9);
}
</style>