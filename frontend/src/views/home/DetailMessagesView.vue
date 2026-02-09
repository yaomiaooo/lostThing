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
              <div class="connection-status" :class="{ connected: isConnected }">
                {{ isConnected ? '✓ 实时连接' : '↻ 轮询中...' }}
              </div>
            </div>
            <button class="close-btn" @click="closeDialog">×</button>
          </div>
          
          <!-- 消息区域 -->
          <div class="chat-messages" ref="chatMessagesRef">
            <div 
              v-for="message in messages" 
              :key="message.id || message.tempId"
              class="message-item"
              :class="{ 
                'own-message': message.isOwn, 
                'system-message': message.type === 2
              }"
            >
              <div class="message-content">
                {{ message.content }}
              </div>
              <div class="message-time">
                {{ formatMessageTime(message.createTime) }}
                <span v-if="message.status === 'sending'" class="sending-indicator">
                  <span class="dot"></span>
                  <span class="dot"></span>
                  <span class="dot"></span>
                </span>
                <span v-else-if="message.status === 'error'" class="error-indicator" title="发送失败">
                  ❌
                </span>
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
              :disabled="!canSend || isSending"
              @click="sendMessage"
            >
              <span v-if="isSending">发送中...</span>
              <span v-else>发送</span>
            </button>
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
    const res = await axios.get(`/api/item/info`, {
      params: { itemId: props.itemId }
    })
    
    if (res.data.code === 0 || res.data.code === 200) {
      const itemData = res.data.data
      itemOwnerInfo.value = {
        userId: itemData.userId || itemData.publisherId,
        userRole: itemData.userRole || 0
      }
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

.connection-status {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  display: inline-block;
  margin-top: 4px;
  font-weight: 500;
  background-color: #f0f0f0;
  color: #666;
}

.connection-status.connected {
  background-color: #e7f7ed;
  color: #0ca750;
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
  display: flex;
  align-items: center;
  gap: 4px;
}

.sending-indicator {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.sending-indicator .dot {
  width: 4px;
  height: 4px;
  background-color: #999;
  border-radius: 50%;
  animation: dot-blink 1.4s infinite both;
}

.sending-indicator .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.sending-indicator .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-blink {
  0%, 80%, 100% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
}

.error-indicator {
  color: #ef4444;
  font-size: 10px;
  cursor: help;
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