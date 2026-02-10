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
              <span v-if="isConnected" class="connection-status connected">● 在线</span>
              <span v-else class="connection-status disconnected">● 离线</span>
            </div>
            <button class="close-btn" @click="closeDialog">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- 消息区域 -->
          <div class="chat-messages" ref="chatMessagesRef">
            <div 
              v-for="message in messages" 
              :key="message.id || message.tempId"
              class="message-container"
              :class="{ 
                'own-message': message.isOwn, 
                'system-message': message.type === 2
              }"
            >
              <!-- 时间戳 -->
              <div class="message-timestamp" v-if="shouldShowTimestamp(message)">
                {{ formatMessageTime(message.createTime) }}
              </div>
              
              <!-- 消息气泡 -->
              <div class="message-bubble">
                <div class="message-content">
                  {{ message.content }}
                </div>
                <div class="message-footer">
                  <span class="message-time">
                    {{ formatTime(message.createTime) }}
                  </span>
                  <span v-if="message.status === 'sending'" class="message-status">
                    <span class="sending-indicator">
                      <span class="dot"></span>
                      <span class="dot"></span>
                      <span class="dot"></span>
                    </span>
                  </span>
                  <span v-else-if="message.status === 'error'" class="message-status error" title="发送失败">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                    </svg>
                  </span>
                  <span v-else-if="message.isOwn" class="message-status sent">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                    </svg>
                  </span>
                </div>
              </div>
            </div>
            <div v-if="messages.length === 0" class="no-messages">
              <div class="empty-icon">💬</div>
              <div class="empty-text">暂无消息，开始沟通吧</div>
            </div>
          </div>
          
          <!-- 输入区域 -->
          <div class="chat-input-area">
            <div class="input-wrapper">
              <textarea 
                v-model="inputText" 
                placeholder="请输入与物品相关的消息..."
                :rows="1"
                maxlength="200"
                @keydown.enter.prevent="sendMessage"
                @input="handleInputChange"
                ref="chatInputRef"
                class="message-input"
              ></textarea>
              <div class="input-actions">
                <span class="char-count">{{ inputText.length }}/200</span>
                <button 
                  class="send-btn" 
                  :disabled="!canSend || isSending"
                  @click="sendMessage"
                >
                  <svg v-if="isSending" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" class="loading-icon">
                    <path d="M12 2v4m0 12v4m8-10h-4M6 12H2m15.3-7.3l-2.8 2.8m-9.8 9.8l-2.8 2.8m15.3-2.8l-2.8-2.8M4.7 7.7L2 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="currentColor" class="send-icon">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useRealtimeMessages, type RealtimeCallback } from '../../utils/realtimeService'

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
const isSending = ref(false)
const currentConversationId = ref<number | null>(props.conversationId || null)
const chatMessagesRef = ref<HTMLElement | null>(null)
const chatInputRef = ref<HTMLTextAreaElement | null>(null)
const isLoading = ref(false)
const itemOwnerInfo = ref<{userId: number, userRole: number} | null>(null)
const isConnected = ref(false)

// ==================== 实时消息服务 ====================
const { subscribe, unsubscribe, triggerUpdate } = useRealtimeMessages()

// 用于追踪已发送的临时消息
const pendingMessages = ref<Set<number>>(new Set())

// 实时消息回调函数
const handleRealtimeUpdate: RealtimeCallback = (update) => {
  if (!update.messages || update.messages.length === 0) return;
  
  const currentUser = getCurrentUser();
  if (!currentUser) return;

  update.messages.forEach((newMessage: any) => {
    // 1. 查找是否存在对应的本地临时消息
    // 匹配条件：(tempId相同) OR (内容、发送者相同 且 状态为发送中)
    const existingIndex = messages.value.findIndex(msg => {
      const isSameTempId = msg.tempId && newMessage.tempId && msg.tempId === newMessage.tempId;
      const isSameContent = msg.status === 'sending' && 
                            msg.content === newMessage.content && 
                            msg.senderId === currentUser.id;
      return isSameTempId || isSameContent;
    });

    if (existingIndex !== -1) {
      // 【替换逻辑】用服务器返回的正式数据替换本地临时数据
      messages.value[existingIndex] = {
        ...newMessage,
        isOwn: true,
        status: 'sent',
        tempId: undefined // 清除临时ID，标识已转正
      };
      // 成功匹配后，从待处理集合中移除
      if (newMessage.tempId) pendingMessages.value.delete(newMessage.tempId);
    } else {
      // 【新增逻辑】检查正式ID防止重复推送
      const isDuplicate = messages.value.some(msg => msg.id === newMessage.id);
      if (!isDuplicate) {
        messages.value.push({
          ...newMessage,
          isOwn: newMessage.senderId === currentUser.id,
          status: 'sent'
        });
      }
    }
  });

  // 按时间重新排序并滚动
  messages.value.sort((a, b) => new Date(a.createTime).getTime() - new Date(b.createTime).getTime());
  scrollToBottom();
}

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

onUnmounted(() => {
  // 清理实时消息订阅
  if (currentConversationId.value) {
    unsubscribe(currentConversationId.value, handleRealtimeUpdate)
  }
  
  // 清空待处理消息
  pendingMessages.value.clear()
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
    // 取消旧的订阅
    if (currentConversationId.value) {
      unsubscribe(currentConversationId.value, handleRealtimeUpdate)
    }
    
    currentConversationId.value = newId
    loadMessages()
    
    // 订阅新的对话
    if (currentConversationId.value) {
      subscribe(currentConversationId.value, handleRealtimeUpdate)
      isConnected.value = true
    }
  }
})

// ==================== 对话框操作 ====================
const closeDialog = () => {
  // 取消实时消息订阅
  if (currentConversationId.value) {
    unsubscribe(currentConversationId.value, handleRealtimeUpdate)
  }
  
  emit('update:visible', false)
  emit('close')
}

const resetDialog = () => {
  messages.value = []
  inputText.value = ''
  isLoading.value = false
  isSending.value = false
  isConnected.value = false
  pendingMessages.value.clear()
}

const initDialog = async () => {
  if (isLoading.value) return
  
  isLoading.value = true
  await nextTick()
  
  // 首先检查物品信息，获取发布者信息
  await checkItemInfo()
  
  // 如果有conversationId，直接加载消息并订阅实时更新
  if (currentConversationId.value) {
    await loadMessages()
    
    // 订阅实时消息更新
    subscribe(currentConversationId.value, handleRealtimeUpdate)
    isConnected.value = true
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
    // 使用可用的 /api/item/detail 接口替代不存在的 /api/item/info
    const res = await axios.get(`/api/item/detail`, {
      params: { itemId: props.itemId }
    })
    
    if (res.data.code === 0 || res.data.code === 200) {
      const itemData = res.data.data
      // 根据后端返回的数据结构调整字段映射
      itemOwnerInfo.value = {
        userId: itemData.userId || itemData.publisherId || itemData.creatorId,
        userRole: itemData.userRole || 0
      }
    }
  } catch (error) {
    console.error('获取物品信息失败:', error)
    // 如果获取失败，设置默认值避免后续逻辑错误
    itemOwnerInfo.value = {
      userId: currentUser.value.id,
      userRole: 0
    }
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
      
      // 订阅实时消息更新
      if (currentConversationId.value) {
        subscribe(currentConversationId.value, handleRealtimeUpdate)
        isConnected.value = true
      }
      
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
      
      // 订阅实时消息更新
      if (currentConversationId.value) {
        subscribe(currentConversationId.value, handleRealtimeUpdate)
        isConnected.value = true
      }
      
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
        // 只加载服务器返回的消息，不包含发送中的临时消息
        const serverMessages = rawMessages.map((msg: any) => ({
          ...msg,
          isOwn: msg.senderId === currentUser.value?.id,
          status: 'sent'
        }))
        
        messages.value = serverMessages.sort((a, b) => 
          new Date(a.createTime).getTime() - new Date(b.createTime).getTime()
        )
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
  const content = inputText.value.trim();
  if (!content || !currentConversationId.value || isSending.value) return;

  const tempId = Date.now();
  
  // 1. 构造临时消息用于 UI 占位
  const tempMessage = {
    id: tempId, 
    tempId: tempId,
    conversationId: currentConversationId.value,
    senderId: currentUser.value!.id,
    content: content,
    createTime: new Date().toISOString(),
    type: 1,
    isOwn: true,
    status: 'sending'
  };

  // 2. 更新状态
  pendingMessages.value.add(tempId);
  messages.value.push(tempMessage);
  inputText.value = '';
  scrollToBottom();

  try {
    // 3. 请求接口（建议带上 tempId，方便后端在实时推送时带回）
    const sendRes = await axios.post('/api/chat/conversation/message/send', { 
      conversationId: currentConversationId.value, 
      content: content,
      tempId: tempId // 哪怕后端不存，传过去也是个好习惯
    });

    if (sendRes.data.code === 0) {
      // 注意：这里不要立即 delete(tempId)，
      // 也不要手动去修改 messages.value 里的 status，
      // 全部交给 handleRealtimeUpdate 处理，这样逻辑最统一。
      
      // 如果你的实时推送很慢，可以保留下面的逻辑作为保底：
      const idx = messages.value.findIndex(m => m.tempId === tempId);
      if (idx !== -1 && !messages.value[idx].id.toString().includes('17')) { // 简单判断是否已由推送更新
         messages.value[idx].status = 'sent';
      }
      
      triggerUpdate(currentConversationId.value);
    } else {
      throw new Error(sendRes.data.msg);
    }
  } catch (e) {
    // 只有失败时才手动处理状态
    const idx = messages.value.findIndex(m => m.tempId === tempId);
    if (idx !== -1) messages.value[idx].status = 'error';
    pendingMessages.value.delete(tempId);
  } finally {
    focusInput();
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
      return '今天'
    }
    const diff = now.getTime() - date.getTime()
    if (diff < 24 * 60 * 60 * 1000) {
      return '昨天'
    }
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch {
    return timeStr
  }
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return timeStr
  }
}

const shouldShowTimestamp = (message: any) => {
  const index = messages.value.indexOf(message)
  if (index === 0) return true
  
  const prevMessage = messages.value[index - 1]
  if (!prevMessage) return true
  
  const currentTime = new Date(message.createTime)
  const prevTime = new Date(prevMessage.createTime)
  const timeDiff = currentTime.getTime() - prevTime.getTime()
  
  // 如果两条消息时间差超过5分钟，显示时间戳
  return timeDiff > 5 * 60 * 1000
}

const handleInputChange = () => {
  validateMessage()
  // 自动调整文本框高度
  nextTick(() => {
    const textarea = chatInputRef.value
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
  })
}

const showErrorMessage = (message: string) => {
  console.error(message)
  alert(message)
}

const getCurrentUser = () => {
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
}
</script>

<style scoped>
.chat-dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.chat-dialog {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  width: 600px;
  max-width: 95vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.chat-header {
  padding: 24px;
  background: linear-gradient(135deg, #f38181 0%, #f77d5f 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(243, 129, 129, 0.3);
}

.chat-title {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.participant-role {
  font-size: 18px;
  font-weight: 700;
  font-family: "Comic Sans MS", "Marker Felt", cursive;
}

.chat-hint {
  font-size: 13px;
  opacity: 0.9;
  font-family: "Comic Sans MS", cursive;
}

.connection-status {
  font-size: 12px;
  margin-top: 4px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.connection-status.connected {
  color: #4ade80;
}

.connection-status.disconnected {
  color: #f87171;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  color: white;
  padding: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.chat-messages {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  max-height: 400px;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.message-container {
  display: flex;
  flex-direction: column;
  padding: 0 20px;
  margin: 8px 0;
}

.message-container.own-message {
  align-items: flex-end;
}

.message-container.system-message {
  align-items: center;
}

.message-timestamp {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  margin: 16px 0 8px;
  padding: 4px 12px;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  display: inline-block;
  align-self: center;
  font-family: "Comic Sans MS", cursive;
}

.message-bubble {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.own-message .message-bubble {
  align-items: flex-end;
}

.system-message .message-bubble {
  align-items: center;
  max-width: 90%;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  word-break: break-word;
  line-height: 1.5;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  animation: messageSlideIn 0.3s ease-out;
}

.message-container:not(.own-message):not(.system-message) .message-content {
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  color: #334155;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 6px;
}

.own-message .message-content {
  background: linear-gradient(135deg, #f38181 0%, #f77d5f 100%);
  color: white;
  border-bottom-right-radius: 6px;
}

.system-message .message-content {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  font-size: 12px;
  border-radius: 12px;
}

.message-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #94a3b8;
  padding: 0 4px;
}

.own-message .message-footer {
  justify-content: flex-end;
}

.message-status {
  display: flex;
  align-items: center;
}

.message-status.sent {
  color: #10b981;
}

.message-status.error {
  color: #ef4444;
}

.sending-indicator {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.sending-indicator .dot {
  width: 4px;
  height: 4px;
  background-color: #94a3b8;
  border-radius: 50%;
  animation: dot-blink 1.4s infinite both;
}

.sending-indicator .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.sending-indicator .dot:nth-child(3) {
  animation-delay: 0.4s;
}

.no-messages {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  font-family: "Comic Sans MS", cursive;
}

.chat-input-area {
  padding: 20px;
  background: #ffffff;
  border-top: 1px solid #f1f5f9;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #f8fafc;
  border-radius: 20px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: #f38181;
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

.message-input {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  outline: none;
  max-height: 120px;
  min-height: 20px;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.char-count {
  font-size: 12px;
  color: #94a3b8;
  min-width: 50px;
  text-align: right;
}

.send-btn {
  background: linear-gradient(135deg, #f38181 0%, #f77d5f 100%);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

.send-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.send-icon, .loading-icon {
  transition: transform 0.3s ease;
}

.send-btn:hover:not(:disabled) .send-icon {
  transform: translateX(2px);
}

.loading-icon {
  animation: spin 1s linear infinite;
}

/* 动画效果 */
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes dot-blink {
  0%, 80%, 100% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-dialog-mask {
    padding: 10px;
  }
  
  .chat-dialog {
    border-radius: 16px;
    max-height: 90vh;
  }
  
  .chat-header {
    padding: 20px;
  }
  
  .participant-role {
    font-size: 16px;
  }
  
  .message-bubble {
    max-width: 85%;
  }
  
  .message-content {
    padding: 10px 14px;
    font-size: 13px;
  }
  
  .chat-input-area {
    padding: 16px;
  }
  
  .input-wrapper {
    padding: 10px;
  }
}

@media (max-width: 480px) {
  .chat-dialog {
    border-radius: 12px;
  }
  
  .chat-header {
    padding: 16px;
  }
  
  .message-container {
    padding: 0 16px;
  }
  
  .message-bubble {
    max-width: 90%;
  }
}
</style>