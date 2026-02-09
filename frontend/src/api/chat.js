import request from '@/utils/request'

/**
 * 1️⃣ 进入或创建会话（点击“去询问”）
 * POST /api/chat/conversation/enter
 */
export function enterConversation(itemId) {
  return request({
    url: '/api/chat/conversation/enter',
    method: 'post',
    data: {
      itemId
    }
  })
}

/**
 * 2️⃣ 获取会话详情 + 消息列表
 * GET /api/chat/conversation/{conversationId}
 */
export function getConversationDetail(conversationId) {
  return request({
    url: `/api/chat/conversation/${conversationId}`,
    method: 'get'
  })
}

/**
 * 3️⃣ 发送消息
 * POST /api/chat/message/send
 */
export function sendMessage(conversationId, content) {
  return request({
    url: '/api/chat/message/send',
    method: 'post',
    data: {
      conversationId,
      content
    }
  })
}

/**
 * 4️⃣ 获取我的会话列表
 * GET /api/chat/conversation/list
 */
export function getMyConversations() {
  return request({
    url: '/api/chat/conversation/list',
    method: 'get'
  })
}

/**
 * 5️⃣ 判断是否可以发送消息
 * 
 *
 * GET /api/chat/conversation/can-send
 */
export function canSendMessage(conversationId) {
  return request({
    url: `/api/chat/conversation/can-send`,
    method: 'get',
    params: {
      conversationId
    }
  })
}
