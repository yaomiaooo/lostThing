// 实时消息服务 - 轮询实现 (修复版)
import { ref, onUnmounted } from 'vue'
import axios from 'axios'

export interface MessageUpdate {
  conversationId: number
  messages: any[]
  lastMessageTime: string
  source?: 'polling' | 'trigger' // 标记更新来源
}

export interface RealtimeCallback {
  (update: MessageUpdate): void
}

// 未读计数管理器 - 使用 localStorage 替代 sessionStorage，确保持久化
class UnreadCountManager {
  private static readonly STORAGE_KEY_PREFIX = 'unread_count_'
  private static readonly LAST_READ_PREFIX = 'last_read_time_'
  
  // 获取未读计数
  static getUnreadCount(userId: number, conversationId: number): number {
    const key = `${this.STORAGE_KEY_PREFIX}${userId}_${conversationId}`
    const stored = localStorage.getItem(key)
    return stored ? parseInt(stored, 10) || 0 : 0
  }
  
  // 设置未读计数
  static setUnreadCount(userId: number, conversationId: number, count: number): void {
    const key = `${this.STORAGE_KEY_PREFIX}${userId}_${conversationId}`
    if (count <= 0) {
      localStorage.removeItem(key)
    } else {
      localStorage.setItem(key, count.toString())
    }
    // 触发全局事件，通知所有监听者
    window.dispatchEvent(new CustomEvent('unread-count-changed', {
      detail: { userId, conversationId, count }
    }))
  }
  
  // 增加未读计数
  static incrementUnreadCount(userId: number, conversationId: number, increment: number = 1): number {
    const current = this.getUnreadCount(userId, conversationId)
    const newCount = current + increment
    this.setUnreadCount(userId, conversationId, newCount)
    return newCount
  }
  
  // 清除未读计数
  static clearUnreadCount(userId: number, conversationId: number): void {
    this.setUnreadCount(userId, conversationId, 0)
    const timeKey = `${this.LAST_READ_PREFIX}${userId}_${conversationId}`
    localStorage.setItem(timeKey, Date.now().toString())
  }
  
  // 获取所有未读计数总和
  static getTotalUnreadCount(userId: number): number {
    let total = 0
    const prefix = `${this.STORAGE_KEY_PREFIX}${userId}_`
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith(prefix)) {
        const count = parseInt(localStorage.getItem(key) || '0', 10)
        total += count
      }
    }
    return total
  }
  
  // 获取所有对话的未读计数映射
  static getAllUnreadCounts(userId: number): Map<number, number> {
    const map = new Map<number, number>()
    const prefix = `${this.STORAGE_KEY_PREFIX}${userId}_`
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith(prefix)) {
        const conversationId = parseInt(key.replace(prefix, ''), 10)
        const count = parseInt(localStorage.getItem(key) || '0', 10)
        if (!isNaN(conversationId)) {
          map.set(conversationId, count)
        }
      }
    }
    return map
  }
  
  // 清理指定用户的所有数据
  static clearAll(userId: number): void {
    const prefix1 = `${this.STORAGE_KEY_PREFIX}${userId}_`
    const prefix2 = `${this.LAST_READ_PREFIX}${userId}_`
    const keysToRemove: string[] = []
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && (key.startsWith(prefix1) || key.startsWith(prefix2))) {
        keysToRemove.push(key)
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key))
  }
}

class RealtimeMessageService {
  private pollingInterval: number = 3000 // 调整为3秒，减少服务器压力
  private timer: number | null = null
  private callbacks: Map<number, Set<RealtimeCallback>> = new Map() // 使用Set避免重复回调
  private lastUpdateTimes: Map<number, string> = new Map()
  private isPolling: boolean = false
  private isChecking: boolean = false
  private messageIds: Map<number, Set<string>> = new Map()
  private processedMessageIds: Set<string> = new Set() // 全局消息去重
  
  // 开始轮询
  startPolling() {
    if (this.isPolling) return
    
    this.isPolling = true
    console.log('[RealtimeService] 开始轮询，间隔:', this.pollingInterval, 'ms')
    
    // 立即执行一次检查
    this.pollForUpdates()
    
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
    console.log('[RealtimeService] 停止轮询')
  }

  // 订阅对话更新
  subscribe(conversationId: number, callback: RealtimeCallback): () => void {
    if (!conversationId) {
      console.error('[RealtimeService] 订阅失败：对话ID为空')
      return () => {}
    }
    
    if (!this.callbacks.has(conversationId)) {
      this.callbacks.set(conversationId, new Set())
    }
    
    const callbacks = this.callbacks.get(conversationId)!
    
    // 检查是否已存在相同回调（通过引用比较）
    if (callbacks.has(callback)) {
      console.log(`[RealtimeService] 对话 ${conversationId} 已存在相同回调，跳过订阅`)
      return () => this.unsubscribe(conversationId, callback)
    }
    
    callbacks.add(callback)
    console.log(`[RealtimeService] 订阅对话 ${conversationId}，当前订阅数: ${callbacks.size}`)
    
    // 如果还没有开始轮询，开始轮询
    if (!this.isPolling) {
      this.startPolling()
    }
    
    // 返回取消订阅函数
    return () => this.unsubscribe(conversationId, callback)
  }

  // 取消订阅
  unsubscribe(conversationId: number, callback: RealtimeCallback) {
    const callbacks = this.callbacks.get(conversationId)
    if (callbacks) {
      const hadCallback = callbacks.delete(callback)
      if (hadCallback) {
        console.log(`[RealtimeService] 取消订阅对话 ${conversationId}，剩余订阅数: ${callbacks.size}`)
      }
      
      if (callbacks.size === 0) {
        this.callbacks.delete(conversationId)
        this.lastUpdateTimes.delete(conversationId)
        this.messageIds.delete(conversationId)
        console.log(`[RealtimeService] 对话 ${conversationId} 已无订阅者，清理状态`)
      }
    }
    
    // 如果没有订阅者了，停止轮询
    if (this.callbacks.size === 0) {
      this.stopPolling()
    }
  }

  // 轮询检查更新
  private async pollForUpdates() {
    if (this.callbacks.size === 0 || this.isChecking) return
    
    this.isChecking = true
    
    try {
      // 串行检查，避免并发请求导致的问题
      for (const conversationId of this.callbacks.keys()) {
        await this.checkConversationUpdates(conversationId)
        // 添加小延迟，避免请求过于密集
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    } catch (error) {
      console.error('[RealtimeService] 轮询更新失败:', error)
    } finally {
      this.isChecking = false
    }
  }

  // 检查单个对话的更新
  private async checkConversationUpdates(conversationId: number) {
    try {
      const lastUpdateTime = this.lastUpdateTimes.get(conversationId) || ''
      
      const response = await axios.get('/api/chat/conversation/messages', {
        params: { 
          conversationId,
          lastUpdateTime,
          limit: 50 // 限制返回消息数量
        },
        timeout: 5000 // 增加超时时间
      })

      if (response.data.code === 0) {
        const data = response.data.data
        
        if (data.messages && Array.isArray(data.messages) && data.messages.length > 0) {
          // 获取该对话的已处理消息ID集合
          let processedIds = this.messageIds.get(conversationId)
          if (!processedIds) {
            processedIds = new Set()
            this.messageIds.set(conversationId, processedIds)
          }
          
          // 过滤掉已处理的消息（使用更可靠的消息ID生成逻辑）
          const newMessages = data.messages.filter((msg: any) => {
            // 生成唯一消息ID：优先使用服务端ID，否则组合生成
            const messageId = msg.id || msg.messageId || `${msg.senderId}_${msg.createTime}_${msg.content?.slice(0, 20)}`
            msg._uniqueId = messageId // 保存生成的ID到消息对象
            
            // 全局去重 + 对话内去重
            if (this.processedMessageIds.has(messageId) || processedIds!.has(messageId)) {
              return false
            }
            return true
          })
          
          if (newMessages.length > 0) {
            // 记录这些消息ID到两个集合
            newMessages.forEach((msg: any) => {
              const messageId = msg._uniqueId
              processedIds!.add(messageId)
              this.processedMessageIds.add(messageId)
              
              // 限制集合大小，防止内存泄漏
              if (processedIds!.size > 1000) {
                const first = processedIds!.values().next().value
                processedIds!.delete(first)
              }
            })
            
            if (this.processedMessageIds.size > 5000) {
              this.processedMessageIds.clear()
            }
            
            // 按时间排序
            const sortedMessages = [...newMessages].sort((a, b) => {
              const timeA = new Date(a.createTime || a.createdAt || 0).getTime()
              const timeB = new Date(b.createTime || b.createdAt || 0).getTime()
              return timeA - timeB
            })
            
            const latestMessage = sortedMessages[sortedMessages.length - 1]
            const latestMessageTime = latestMessage.createTime || latestMessage.createdAt
            
            const update: MessageUpdate = {
              conversationId,
              messages: sortedMessages,
              lastMessageTime: latestMessageTime,
              source: 'polling'
            }
            
            // 更新最后更新时间
            if (latestMessageTime) {
              this.lastUpdateTimes.set(conversationId, latestMessageTime)
            }
            
            // 通知订阅者
            this.notifySubscribers(conversationId, update)
            
            console.log(`[RealtimeService] 对话 ${conversationId} 收到 ${newMessages.length} 条新消息`)
          }
        }
      }
    } catch (error: any) {
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        console.warn(`[RealtimeService] 检查对话 ${conversationId} 更新超时`)
      } else {
        console.error(`[RealtimeService] 检查对话 ${conversationId} 更新失败:`, error.message)
      }
    }
  }

  // 通知订阅者
  private notifySubscribers(conversationId: number, update: MessageUpdate) {
    const callbacks = this.callbacks.get(conversationId)
    if (callbacks && callbacks.size > 0) {
      // 使用 requestAnimationFrame 避免阻塞主线程，但保持及时性
      requestAnimationFrame(() => {
        callbacks.forEach(callback => {
          try {
            callback(update)
          } catch (error) {
            console.error('[RealtimeService] 回调函数执行失败:', error)
          }
        })
      })
    }
  }

  // 手动触发更新（发送消息后立即检查）
  async triggerImmediateUpdate(conversationId: number): Promise<void> {
    // 使用队列避免并发触发
    if (this.isChecking) {
      await new Promise(resolve => setTimeout(resolve, 200))
      return this.triggerImmediateUpdate(conversationId)
    }
    
    await this.checkConversationUpdates(conversationId)
  }

  // 清除对话的消息记录
  clearConversationCache(conversationId: number) {
    this.messageIds.delete(conversationId)
    this.lastUpdateTimes.delete(conversationId)
    console.log(`[RealtimeService] 清除对话 ${conversationId} 的缓存`)
  }
  
  // 重置所有状态（用于登出等场景）
  reset() {
    this.stopPolling()
    this.callbacks.clear()
    this.lastUpdateTimes.clear()
    this.messageIds.clear()
    this.processedMessageIds.clear()
    console.log('[RealtimeService] 重置所有状态')
  }
}

// 创建单例实例
const realtimeService = new RealtimeMessageService()

// Vue 组合式函数 (修复版)
export function useRealtimeMessages() {
  const subscribedConversations = ref<Set<number>>(new Set())
  const unsubscribers = new Map<number, () => void>() // 存储取消订阅函数

  const subscribe = (conversationId: number, callback: RealtimeCallback) => {
    if (!conversationId) {
      console.error('[useRealtimeMessages] conversationId 不能为空')
      return
    }
    
    // 如果已订阅，先取消旧订阅
    if (subscribedConversations.value.has(conversationId)) {
      const oldUnsubscribe = unsubscribers.get(conversationId)
      if (oldUnsubscribe) {
        oldUnsubscribe()
      }
    }
    
    // 执行新订阅并保存取消函数
    const unsubscribeFn = realtimeService.subscribe(conversationId, callback)
    subscribedConversations.value.add(conversationId)
    unsubscribers.set(conversationId, unsubscribeFn)
    
    console.log(`[useRealtimeMessages] 订阅对话 ${conversationId}`)
  }

  const unsubscribe = (conversationId: number, callback?: RealtimeCallback) => {
    if (subscribedConversations.value.has(conversationId)) {
      // 使用保存的取消订阅函数
      const unsubscribeFn = unsubscribers.get(conversationId)
      if (unsubscribeFn) {
        unsubscribeFn()
      } else if (callback) {
        // 回退到直接调用
        realtimeService.unsubscribe(conversationId, callback)
      }
      
      subscribedConversations.value.delete(conversationId)
      unsubscribers.delete(conversationId)
      console.log(`[useRealtimeMessages] 取消订阅对话 ${conversationId}`)
    }
  }

  const unsubscribeAll = () => {
    subscribedConversations.value.forEach(conversationId => {
      const unsubscribeFn = unsubscribers.get(conversationId)
      if (unsubscribeFn) {
        unsubscribeFn()
      }
    })
    subscribedConversations.value.clear()
    unsubscribers.clear()
    console.log('[useRealtimeMessages] 取消所有订阅')
  }

  const triggerUpdate = (conversationId: number) => {
    realtimeService.triggerImmediateUpdate(conversationId)
  }

  const clearCache = (conversationId: number) => {
    realtimeService.clearConversationCache(conversationId)
  }

  // 组件卸载时自动取消所有订阅
  onUnmounted(() => {
    console.log('[useRealtimeMessages] 组件卸载，清理所有订阅')
    unsubscribeAll()
  })

  return {
    subscribe,
    unsubscribe,
    unsubscribeAll,
    triggerUpdate,
    clearCache,
    subscribedConversations
  }
}

// 导出未读计数管理器
export { UnreadCountManager }
export default realtimeService