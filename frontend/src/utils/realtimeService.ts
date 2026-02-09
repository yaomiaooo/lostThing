// 实时消息服务 - 轮询实现
import { ref, onUnmounted } from 'vue'
import axios from 'axios'

export interface MessageUpdate {
  conversationId: number
  messages: any[]
  lastMessageTime: string
}

export interface RealtimeCallback {
  (update: MessageUpdate): void
}

class RealtimeMessageService {
  private pollingInterval: number = 5000 // 5秒轮询一次
  private timer: number | null = null
  private callbacks: Map<number, RealtimeCallback[]> = new Map()
  private lastUpdateTimes: Map<number, string> = new Map()
  private isPolling: boolean = false

  // 开始轮询
  startPolling() {
    if (this.isPolling) return
    
    this.isPolling = true
    this.timer = window.setInterval(() => {
      this.pollForUpdates()
    }, this.pollingInterval)
  }

  // 停止轮询
  stopPolling() {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
    this.isPolling = false
    this.callbacks.clear()
    this.lastUpdateTimes.clear()
  }

  // 订阅对话更新
  subscribe(conversationId: number, callback: RealtimeCallback) {
    if (!this.callbacks.has(conversationId)) {
      this.callbacks.set(conversationId, [])
    }
    this.callbacks.get(conversationId)!.push(callback)
    
    // 如果还没有开始轮询，开始轮询
    if (!this.isPolling) {
      this.startPolling()
    }
  }

  // 取消订阅
  unsubscribe(conversationId: number, callback: RealtimeCallback) {
    const callbacks = this.callbacks.get(conversationId)
    if (callbacks) {
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
      if (callbacks.length === 0) {
        this.callbacks.delete(conversationId)
        this.lastUpdateTimes.delete(conversationId)
      }
    }
    
    // 如果没有订阅者了，停止轮询
    if (this.callbacks.size === 0) {
      this.stopPolling()
    }
  }

  // 轮询检查更新
  private async pollForUpdates() {
    if (this.callbacks.size === 0) return

    try {
      for (const [conversationId] of this.callbacks) {
        await this.checkConversationUpdates(conversationId)
      }
    } catch (error) {
      console.error('轮询更新失败:', error)
    }
  }

  // 检查单个对话的更新
  private async checkConversationUpdates(conversationId: number) {
    try {
      const response = await axios.get('/api/chat/conversation/messages', {
        params: { 
          conversationId,
          lastUpdateTime: this.lastUpdateTimes.get(conversationId) || ''
        }
      })

      if (response.data.code === 0) {
        const data = response.data.data
        
        // 检查是否有新消息
        if (data.messages && data.messages.length > 0) {
          const latestMessageTime = data.messages[data.messages.length - 1].createdAt
          const lastKnownTime = this.lastUpdateTimes.get(conversationId)
          
          // 如果有新消息，通知订阅者
          if (!lastKnownTime || new Date(latestMessageTime) > new Date(lastKnownTime)) {
            const update: MessageUpdate = {
              conversationId,
              messages: data.messages,
              lastMessageTime: latestMessageTime
            }
            
            this.notifySubscribers(conversationId, update)
            this.lastUpdateTimes.set(conversationId, latestMessageTime)
          }
        }
      }
    } catch (error) {
      console.error(`检查对话 ${conversationId} 更新失败:`, error)
    }
  }

  // 通知订阅者
  private notifySubscribers(conversationId: number, update: MessageUpdate) {
    const callbacks = this.callbacks.get(conversationId)
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(update)
        } catch (error) {
          console.error('回调函数执行失败:', error)
        }
      })
    }
  }

  // 手动触发更新（发送消息后立即检查）
  async triggerImmediateUpdate(conversationId: number) {
    await this.checkConversationUpdates(conversationId)
  }
}

// 创建单例实例
const realtimeService = new RealtimeMessageService()

// Vue 组合式函数
export function useRealtimeMessages() {
  const subscribedConversations = ref<Set<number>>(new Set())

  const subscribe = (conversationId: number, callback: RealtimeCallback) => {
    if (!subscribedConversations.value.has(conversationId)) {
      realtimeService.subscribe(conversationId, callback)
      subscribedConversations.value.add(conversationId)
    }
  }

  const unsubscribe = (conversationId: number, callback: RealtimeCallback) => {
    realtimeService.unsubscribe(conversationId, callback)
    subscribedConversations.value.delete(conversationId)
  }

  const triggerUpdate = (conversationId: number) => {
    realtimeService.triggerImmediateUpdate(conversationId)
  }

  // 组件卸载时自动取消订阅
  onUnmounted(() => {
    subscribedConversations.value.forEach(conversationId => {
      realtimeService.unsubscribe(conversationId, () => {})
    })
    subscribedConversations.value.clear()
  })

  return {
    subscribe,
    unsubscribe,
    triggerUpdate
  }
}

export default realtimeService