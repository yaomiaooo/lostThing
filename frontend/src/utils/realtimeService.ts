// 实时消息服务 - 轮询实现（完整修复版）
import { ref, onUnmounted } from 'vue'
import axios from 'axios'

export interface MessageUpdate {
  conversationId: number
  messages: any[]
  lastMessageTime: string
  source?: 'polling' | 'trigger'
}

export interface RealtimeCallback {
  (update: MessageUpdate): void
}

// 未读计数管理器 - 使用 localStorage 持久化存储
class UnreadCountManager {
  private static readonly STORAGE_KEY_PREFIX = 'unread_count_'
  private static readonly LAST_READ_PREFIX = 'last_read_time_'

  // 获取未读计数
  static getUnreadCount(userId: number, conversationId: number): number {
    if (!userId || !conversationId) return 0
    const key = `${this.STORAGE_KEY_PREFIX}${userId}_${conversationId}`
    const stored = localStorage.getItem(key)
    return stored ? parseInt(stored, 10) || 0 : 0
  }

  // 设置未读计数
  static setUnreadCount(userId: number, conversationId: number, count: number): void {
    if (!userId || !conversationId) return

    const key = `${this.STORAGE_KEY_PREFIX}${userId}_${conversationId}`
    const oldCount = this.getUnreadCount(userId, conversationId)

    if (count <= 0) {
      localStorage.removeItem(key)
    } else {
      localStorage.setItem(key, count.toString())
    }

    // 只有当数值真正变化时才触发事件
    if (oldCount !== count) {
      window.dispatchEvent(new CustomEvent('unread-count-changed', {
        detail: { userId, conversationId, count, oldCount }
      }))
    }
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
    if (!userId) return 0
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
    if (!userId) return map

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

  // 用户登出时清理
  static clearAll(userId: number): void {
    if (!userId) return

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
    console.log(`[UnreadCountManager] 清理用户 ${userId} 的 ${keysToRemove.length} 条未读记录`)
  }

  // 同步服务端未读数（登录时调用）
  static async syncWithServer(userId: number): Promise<void> {
    if (!userId) return

    try {
      const response = await axios.get('/api/chat/unread-count', {
        params: { userId }
      })

      if (response.data.code === 0 && response.data.data) {
        // 清理旧数据
        this.clearAll(userId)

        // 使用服务端数据初始化
        const unreadList = response.data.data || []
        unreadList.forEach((item: { conversationId: number, count: number }) => {
          if (item.count > 0) {
            this.setUnreadCount(userId, item.conversationId, item.count)
          }
        })

        console.log(`[UnreadCountManager] 已同步服务端未读数，共 ${unreadList.length} 个对话`)
      }
    } catch (err) {
      console.error('[UnreadCountManager] 同步服务端未读数失败:', err)
    }
  }

  // 获取最后阅读时间
  static getLastReadTime(userId: number, conversationId: number): number {
    if (!userId || !conversationId) return 0
    const key = `${this.LAST_READ_PREFIX}${userId}_${conversationId}`
    const stored = localStorage.getItem(key)
    return stored ? parseInt(stored, 10) || 0 : 0
  }
}

class RealtimeMessageService {
  private pollingInterval: number = 3000
  private timer: number | null = null
  private callbacks: Map<number, Set<RealtimeCallback>> = new Map()
  private lastUpdateTimes: Map<number, string> = new Map()
  private isPolling: boolean = false
  private isChecking: boolean = false
  private messageIds: Map<number, Set<string>> = new Map()
  private processedMessageIds: Set<string> = new Set()
  private userId: number | null = null

  constructor() {
    this.restoreProcessedIds()
  }

  // 设置当前用户ID
  setUserId(userId: number) {
    this.userId = userId
    this.restoreProcessedIds()
  }

  // 从 sessionStorage 恢复已处理的消息ID
  private restoreProcessedIds() {
    try {
      const stored = sessionStorage.getItem('processed_message_ids')
      if (stored) {
        const ids = JSON.parse(stored)
        this.processedMessageIds = new Set(ids)
        console.log(`[RealtimeService] 从 sessionStorage 恢复了 ${ids.length} 个已处理消息ID`)
      }

      const convStored = sessionStorage.getItem('conversation_message_ids')
      if (convStored) {
        const convData = JSON.parse(convStored)
        this.messageIds = new Map(Object.entries(convData).map(([k, v]) => [parseInt(k), new Set(v as string[])]))
      }
    } catch (e) {
      console.error('[RealtimeService] 恢复已处理消息ID失败:', e)
    }
  }

  // 保存已处理的消息ID到 sessionStorage
  private saveProcessedIds() {
    try {
      const idsToSave = Array.from(this.processedMessageIds).slice(-500)
      sessionStorage.setItem('processed_message_ids', JSON.stringify(idsToSave))

      const convData: Record<string, string[]> = {}
      this.messageIds.forEach((ids, convId) => {
        convData[convId] = Array.from(ids).slice(-200)
      })
      sessionStorage.setItem('conversation_message_ids', JSON.stringify(convData))
    } catch (e) {
      console.warn('[RealtimeService] 保存已处理消息ID失败:', e)
    }
  }

  // 开始轮询
  startPolling() {
    if (this.isPolling) return

    this.isPolling = true
    console.log('[RealtimeService] 开始轮询，间隔:', this.pollingInterval, 'ms')

    this.timer = window.setInterval(() => {
      this.pollForUpdates()
    }, this.pollingInterval)

    this.pollForUpdates()
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

    if (callbacks.has(callback)) {
      console.log(`[RealtimeService] 对话 ${conversationId} 已存在相同回调，跳过订阅`)
      return () => this.unsubscribe(conversationId, callback)
    }

    callbacks.add(callback)
    console.log(`[RealtimeService] 订阅对话 ${conversationId}，当前订阅数: ${callbacks.size}`)

    if (!this.isPolling) {
      this.startPolling()
    }

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

    if (this.callbacks.size === 0) {
      this.stopPolling()
    }
  }

  // 轮询检查更新
  private async pollForUpdates() {
    if (this.callbacks.size === 0 || this.isChecking) return

    this.isChecking = true

    try {
      for (const conversationId of this.callbacks.keys()) {
        await this.checkConversationUpdates(conversationId)
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
          limit: 50
        },
        timeout: 5000
      })

      if (response.data.code === 0) {
        const data = response.data.data

        if (data.messages && Array.isArray(data.messages) && data.messages.length > 0) {
          let processedIds = this.messageIds.get(conversationId)
          if (!processedIds) {
            processedIds = new Set()
            this.messageIds.set(conversationId, processedIds)
          }

          // 严格去重逻辑
          const newMessages = data.messages.filter((msg: any) => {
            const messageId = msg.id || msg.messageId || `${msg.senderId}_${msg.createTime}_${msg.content?.slice(0, 30)}_${msg.sequence || 0}`
            msg._uniqueId = messageId

            if (this.processedMessageIds.has(messageId)) {
              return false
            }
            if (processedIds!.has(messageId)) {
              return false
            }

            // 时间戳检查
            if (lastUpdateTime && msg.createTime) {
              const msgTime = new Date(msg.createTime).getTime()
              const lastTime = new Date(lastUpdateTime).getTime()
              if (!isNaN(msgTime) && !isNaN(lastTime) && msgTime <= lastTime) {
                return false
              }
            }

            return true
          })

          if (newMessages.length > 0) {
            newMessages.forEach((msg: any) => {
              const messageId = msg._uniqueId
              processedIds!.add(messageId)
              this.processedMessageIds.add(messageId)

              if (processedIds!.size > 1000) {
                const first = processedIds!.values().next().value
                if (first !== undefined) {
                  processedIds!.delete(first)
                }
              }
            })

            if (this.processedMessageIds.size > 5000) {
              this.processedMessageIds.clear()
            }

            this.saveProcessedIds()

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

            if (latestMessageTime) {
              this.lastUpdateTimes.set(conversationId, latestMessageTime)
            }

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

  // 手动触发更新
  async triggerImmediateUpdate(conversationId: number): Promise<void> {
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

  // 添加已处理消息ID（外部调用）
  addProcessedMessageId(conversationId: number, messageId: string) {
    let processedIds = this.messageIds.get(conversationId)
    if (!processedIds) {
      processedIds = new Set()
      this.messageIds.set(conversationId, processedIds)
    }
    processedIds.add(messageId)
    this.processedMessageIds.add(messageId)
    this.saveProcessedIds()
  }

  // 重置所有状态
  reset() {
    this.stopPolling()
    this.callbacks.clear()
    this.lastUpdateTimes.clear()
    this.messageIds.clear()
    this.processedMessageIds.clear()
    this.userId = null

    sessionStorage.removeItem('processed_message_ids')
    sessionStorage.removeItem('conversation_message_ids')

    console.log('[RealtimeService] 重置所有状态')
  }
}

// 创建单例实例
const realtimeService = new RealtimeMessageService()

// Vue 组合式函数
export function useRealtimeMessages() {
  const subscribedConversations = ref<Set<number>>(new Set())
  const unsubscribers = new Map<number, () => void>()

  const subscribe = (conversationId: number, callback: RealtimeCallback) => {
    if (!conversationId) {
      console.error('[useRealtimeMessages] conversationId 不能为空')
      return
    }

    if (subscribedConversations.value.has(conversationId)) {
      const oldUnsubscribe = unsubscribers.get(conversationId)
      if (oldUnsubscribe) {
        oldUnsubscribe()
      }
    }

    const unsubscribeFn = realtimeService.subscribe(conversationId, callback)
    subscribedConversations.value.add(conversationId)
    unsubscribers.set(conversationId, unsubscribeFn)

    console.log(`[useRealtimeMessages] 订阅对话 ${conversationId}`)
  }

  const unsubscribe = (conversationId: number, callback?: RealtimeCallback) => {
    if (subscribedConversations.value.has(conversationId)) {
      const unsubscribeFn = unsubscribers.get(conversationId)
      if (unsubscribeFn) {
        unsubscribeFn()
      } else if (callback) {
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

  // 暴露 realtimeService 的方法
  const addProcessedMessageId = (conversationId: number, messageId: string) => {
    realtimeService.addProcessedMessageId(conversationId, messageId)
  }

  const setUserId = (userId: number) => {
    realtimeService.setUserId(userId)
  }

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
    addProcessedMessageId,
    setUserId,
    subscribedConversations
  }
}

export { UnreadCountManager }
export default realtimeService