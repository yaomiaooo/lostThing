<!-- src/views/system-admin/pages/NoticeManageView.vue -->
<template>
  <div class="notice-manage-page">
    <!-- 背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航 -->
      <SysAdminNavigation 
        subtitle="公告管理"
        active-nav="公告管理"
        @logout="handleLogout"
      />

      <!-- 右侧主内容 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">公告与内容管理</h1>
          <p class="page-subtitle">发布和管理全局公告</p>
        </section>



        <!-- 公告发布 -->
        <section class="content-section">
          <div class="publish-layout">
            <!-- 左侧：公告表单 -->
            <div class="publish-form-panel">
              <h3 class="panel-title">发布公告</h3>
              
              <div class="form-section">
                <label class="form-label">公告标题 <span class="required">*</span></label>
                <input 
                  v-model="publishForm.title"
                  type="text" 
                  class="form-input"
                  placeholder="请输入公告标题，简洁明了..."
                  maxlength="100"
                />
                <span class="char-count">{{ publishForm.title.length }}/100</span>
              </div>

              <div class="form-section">
                <label class="form-label">公告内容 <span class="required">*</span></label>
                <div class="editor-toolbar">
                  <button class="tool-btn" @click="insertTag('【重要】')" title="重要标记">🔴</button>
                  <button class="tool-btn" @click="insertTag('【提示】')" title="提示标记">🔵</button>
                  <button class="tool-btn" @click="insertTag('【注意】')" title="注意标记">🟡</button>
                  <div class="divider"></div>
                  <button class="tool-btn" @click="insertTag('【日期】')" title="日期">📅</button>
                  <button class="tool-btn" @click="insertTag('【时间】')" title="时间">🕒</button>
                  <button class="tool-btn" @click="insertTag('【地点】')" title="地点">📍</button>
                </div>
                <textarea 
                  v-model="publishForm.content"
                  class="form-textarea editor"
                  rows="10"
                  placeholder="请输入公告详细内容..."
                ></textarea>
              </div>

              <div class="form-section">
                <label class="form-label">生效设置</label>
                <div class="setting-row">
                  <div class="setting-item">
                    <span class="setting-label">生效时间</span>
                    <input 
                      type="datetime-local" 
                      v-model="publishForm.startTime"
                      class="form-input"
                    />
                  </div>
                  <div class="setting-item">
                    <span class="setting-label">过期时间（可选）</span>
                    <input 
                      type="datetime-local" 
                      v-model="publishForm.endTime"
                      class="form-input"
                    />
                  </div>
                </div>
              </div>

              <div class="form-section">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="publishForm.isTop">
                  <span class="custom-checkbox"></span>
                  <span class="checkbox-text">
                    <strong>置顶公告</strong>
                    <small>将在所有公告顶部显示，最多同时置顶3条</small>
                  </span>
                </label>
              </div>

              <div class="form-section">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="publishForm.needConfirm">
                  <span class="custom-checkbox"></span>
                  <span class="checkbox-text">
                    <strong>要求确认</strong>
                    <small>用户登录时必须确认阅读后才能继续使用</small>
                  </span>
                </label>
              </div>

              <div class="form-actions">
                <button class="preview-btn" @click="previewNotice">
                  预览
                </button>
                <button 
                  class="submit-btn" 
                  :disabled="!canPublish || publishing"
                  @click="publishNotice"
                >
                  <span v-if="publishing" class="loading-spinner-small"></span>
                  <span v-else>{{ editingNoticeId ? '更新公告' : '立即发布' }}</span>
                </button>
              </div>
            </div>

            <!-- 右侧：公告管理 -->
            <div class="notice-list-panel">
              <div class="panel-header">
                <h3 class="panel-title">已发布公告</h3>
                <div class="filter-tabs">
                  <button 
                    class="filter-tab"
                    :class="{ active: noticeFilter === 'all' }"
                    @click="noticeFilter = 'all'"
                  >
                    全部
                  </button>
                  <button 
                    class="filter-tab"
                    :class="{ active: noticeFilter === 'top' }"
                    @click="noticeFilter = 'top'"
                  >
                    置顶
                  </button>
                  <button 
                    class="filter-tab"
                    :class="{ active: noticeFilter === 'active' }"
                    @click="noticeFilter = 'active'"
                  >
                    生效中
                  </button>
                </div>
              </div>

              <div class="notice-list">
                <div 
                  v-for="notice in filteredNotices" 
                  :key="notice.id"
                  class="notice-item"
                  :class="{ 
                    top: notice.isTop, 
                    expired: isExpired(notice.endTime),
                    pending: isPending(notice.startTime)
                  }"
                >

                  <div class="notice-header">

                    <div class="notice-actions">
                      <button class="action-btn edit" @click="editNotice(notice)" title="编辑">编辑</button>
                      <button class="action-btn top" @click="toggleTop(notice)" :title="notice.isTop ? '取消置顶' : '置顶'">
                        {{ notice.isTop ? '取消置顶' : '置顶' }}
                      </button>
                      <button class="action-btn delete" @click="confirmDeleteNotice(notice)" title="删除">删除</button>
                    </div>
                  </div>
                  <h4 class="notice-title">{{ notice.title }}</h4>
                  <p class="notice-content">{{ truncateText(notice.content, 60) }}</p>
                  <div class="notice-meta">
                    <span class="meta-time">{{ formatDate(notice.createTime) }}</span>
                    <span class="meta-status" :class="getNoticeStatus(notice)">
                      {{ getStatusText(notice) }}
                    </span>
                  </div>

                </div>
              </div>

              <div v-if="filteredNotices.length === 0" class="empty-state">
                <div class="empty-icon"></div>
                <p>暂无公告</p>
              </div>
            </div>
          </div>
        </section>


      </main>
    </div>

    <!-- 预览弹窗 -->
    <div v-if="showPreviewModal" class="modal-overlay" @click.self="closePreviewModal">
      <div class="preview-modal">
        <div class="preview-header">
          <h3>公告预览</h3>
          <button class="modal-close" @click="closePreviewModal">×</button>
        </div>
        <div class="preview-body">
          <div class="preview-notice">

            <h2 class="preview-title">{{ publishForm.title || '公告标题' }}</h2>
            <div class="preview-meta">
              <span>{{ currentDate }}</span>
              <span>系统管理员</span>
            </div>
            <div class="preview-content">
              {{ publishForm.content || '公告内容预览...' }}
            </div>
            <div class="preview-footer" v-if="publishForm.needConfirm">
              <button class="confirm-read-btn">我已阅读并知晓</button>
            </div>
          </div>
        </div>
        <div class="preview-footer-actions">
          <button class="modal-btn cancel-btn" @click="closePreviewModal">关闭</button>
          <button class="modal-btn confirm-btn" @click="confirmAndPublish">确认发布</button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="confirm-modal">
        <div class="preview-header">
          <h3>确认删除</h3>
          <button class="modal-close" @click="closeDeleteModal">×</button>
        </div>
        <div class="preview-body">
          <div class="confirm-content">
            <p class="confirm-text">确定要删除这条公告吗？</p>
            <div class="confirm-detail-box">
              <p class="confirm-detail">「{{ deletingNotice?.title }}」</p>
            </div>
            <p class="confirm-hint">删除后无法恢复，已读用户记录也将清除</p>
          </div>
        </div>
        <div class="preview-footer-actions">
          <button class="modal-btn cancel-btn" @click="closeDeleteModal">取消</button>
          <button class="modal-btn delete-btn" @click="executeDeleteNotice">确认删除</button>
        </div>
      </div>
    </div>




  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SysAdminNavigation from '../components/SysAdminNavigation.vue'

const router = useRouter()



/* ================= 公告发布 ================= */
const publishForm = reactive({
  title: '',
  content: '',
  startTime: '',
  endTime: '',
  isTop: false,
  needConfirm: false
})

const publishing = ref(false)
const noticeList = ref<any[]>([])
const noticeFilter = ref('all')
const editingNoticeId = ref<string | null>(null)

const canPublish = computed(() => {
  return publishForm.title.trim() && publishForm.content.trim()
})

const filteredNotices = computed(() => {
  let list = noticeList.value
  if (noticeFilter.value === 'top') {
    list = list.filter(n => n.isTop)
  } else if (noticeFilter.value === 'active') {
    list = list.filter(n => !isExpired(n.endTime) && !isPending(n.startTime))
  }
  return list.sort((a, b) => {
    if (a.isTop && !b.isTop) return -1
    if (!a.isTop && b.isTop) return 1
    return new Date(b.createTime).getTime() - new Date(a.createTime).getTime()
  })
})



/* ================= 弹窗状态 ================= */
const showPreviewModal = ref(false)
const showDeleteModal = ref(false)
const deletingNotice = ref<any>(null)

/* ================= 计算属性 ================= */
const currentDate = computed(() => {
  return new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
})



/* ================= 公告管理方法 ================= */
const loadNotices = async () => {
  try {
    const res = await axios.get('/api/announcements/admin/list')
    if (res.data.code === 200) {
      // 转换数据格式以适配前端
      noticeList.value = (res.data.data?.list || []).map((item: any) => ({
        id: item.noticeId,
        type: 'system',
        title: item.title,
        content: item.content,
        createTime: item.createTime,
        isTop: item.priority === 1,
        needConfirm: item.priority === 1,
        readCount: 0,
        confirmCount: 0,
        startTime: item.startTime,
        endTime: item.endTime
      }))
    }
  } catch (error) {
    console.error('加载公告列表失败:', error)
    noticeList.value = []
  }
}

const insertTag = (tag: string) => {
  const textarea = document.querySelector('.form-textarea.editor') as HTMLTextAreaElement
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = publishForm.content
  
  publishForm.content = text.substring(0, start) + tag + text.substring(end)
  
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + tag.length, start + tag.length)
  })
}

const previewNotice = () => {
  showPreviewModal.value = true
}

const closePreviewModal = () => {
  showPreviewModal.value = false
}

const confirmAndPublish = () => {
  closePreviewModal()
  publishNotice()
}

const publishNotice = async () => {
  publishing.value = true
  try {
    // 准备请求数据
    const requestData: any = {
      title: publishForm.title,
      content: publishForm.content,
      priority: publishForm.isTop ? 1 : 2,
      startTime: formatDateTimeForBackend(publishForm.startTime) || getDefaultStartTime(),
      endTime: formatDateTimeForBackend(publishForm.endTime) || getDefaultEndTime()
    }
    
    let res
    if (editingNoticeId.value) {
      // 编辑模式 - 更新公告
      console.log('更新公告请求数据:', requestData, 'ID:', editingNoticeId.value)
      res = await axios.put(`/api/announcements/admin/${editingNoticeId.value}`, requestData)
      console.log('更新公告响应:', res.data)
    } else {
      // 新建模式 - 发布公告
      console.log('发布公告请求数据:', requestData)
      res = await axios.post('/api/announcements/admin', requestData)
      console.log('发布公告响应:', res.data)
    }
    
    if (res.data.code === 200) {
      // 重置表单
      Object.assign(publishForm, {
        type: 'system',
        title: '',
        content: '',
        startTime: '',
        endTime: '',
        isTop: false,
        needConfirm: false
      })
      editingNoticeId.value = null
      await loadNotices()
      alert(editingNoticeId.value ? '公告更新成功！' : '公告发布成功！')
    } else {
      alert(`${editingNoticeId.value ? '更新' : '发布'}失败: ${res.data.msg || '未知错误'}`)
    }
  } catch (error: any) {
    console.error(`${editingNoticeId.value ? '更新' : '发布'}失败:`, error)
    alert(`${editingNoticeId.value ? '更新' : '发布'}失败: ${error.message || '请重试'}`)
  } finally {
    publishing.value = false
  }
}

// 格式化时间为后端需要的格式：YYYY-MM-DD HH:MM:SS
const formatDateTimeForBackend = (dateTimeStr: string) => {
  if (!dateTimeStr) return ''
  
  // 如果是 datetime-local 格式（YYYY-MM-DDTHH:MM），转换为 YYYY-MM-DD HH:MM:SS
  if (dateTimeStr.includes('T')) {
    return dateTimeStr.replace('T', ' ') + ':00'
  }
  
  // 如果已经是 YYYY-MM-DD HH:MM:SS 格式，直接返回
  if (dateTimeStr.includes(' ') && dateTimeStr.includes(':')) {
    return dateTimeStr
  }
  
  return dateTimeStr
}

// 获取默认开始时间（现在）
const getDefaultStartTime = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:00`
}

// 获取默认结束时间（30天后）
const getDefaultEndTime = () => {
  const now = new Date()
  now.setDate(now.getDate() + 30)
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} 23:59:59`
}

const editNotice = (notice: any) => {
  editingNoticeId.value = notice.id
  Object.assign(publishForm, {
    title: notice.title,
    content: notice.content,
    startTime: notice.startTime || '',
    endTime: notice.endTime || '',
    isTop: notice.isTop || false,
    needConfirm: notice.needConfirm || false
  })
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const toggleTop = async (notice: any) => {
  try {
    // 先乐观更新UI
    const oldIsTop = notice.isTop
    notice.isTop = !notice.isTop
    
    // 使用更新接口修改 priority 字段（1=置顶，2=普通）
    const res = await axios.put(`/api/announcements/admin/${notice.id}`, {
      priority: notice.isTop ? 1 : 2
    })
    
    if (res.data.code !== 200) {
      // 如果失败，回滚
      notice.isTop = oldIsTop
      alert('操作失败: ' + (res.data.msg || '未知错误'))
    } else {
      alert(notice.isTop ? '置顶成功！' : '取消置顶成功！')
    }
  } catch (error: any) {
    // 如果失败，回滚
    notice.isTop = !notice.isTop
    console.error('置顶操作失败:', error)
    alert('操作失败: ' + (error.message || '网络错误'))
  }
}

const confirmDeleteNotice = (notice: any) => {
  deletingNotice.value = notice
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  deletingNotice.value = null
}

const executeDeleteNotice = async () => {
  if (!deletingNotice.value) return
  try {
    const res = await axios.delete(`/api/announcements/admin/${deletingNotice.value.id}/delete`)
    if (res.data.code === 200) {
      noticeList.value = noticeList.value.filter(n => n.id !== deletingNotice.value.id)
      closeDeleteModal()
      alert('删除成功！')
    } else {
      alert('删除失败: ' + (res.data.msg || '未知错误'))
    }
  } catch (error: any) {
    console.error('删除失败:', error)
    alert('删除失败: ' + (error.message || '网络错误'))
  }
}



/* ================= 工具函数 ================= */
const getNoticeStatus = (notice: any) => {
  if (isExpired(notice.endTime)) return 'expired'
  if (isPending(notice.startTime)) return 'pending'
  return 'active'
}

const getStatusText = (notice: any) => {
  if (isExpired(notice.endTime)) return '已过期'
  if (isPending(notice.startTime)) return '待生效'
  return '生效中'
}

const isExpired = (endTime?: string) => {
  if (!endTime) return false
  return new Date(endTime) < new Date()
}

const isPending = (startTime?: string) => {
  if (!startTime) return false
  return new Date(startTime) > new Date()
}

const formatDate = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const truncateText = (text: string, length: number) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadNotices()
})
</script>

<style scoped>
/* 基础布局 */
.notice-manage-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

.background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.solid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #f8f3d4;
  pointer-events: none;
}

.layout-container {
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 100vh;
  display: flex;
}

.main-content {
  flex: 1;
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

/* 页面标题 */
.page-header {
  margin-bottom: 25px;
}

.page-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 32px;
  color: #a67c52;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.page-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.7);
}

/* 标签页 */
.notice-tabs {
  margin-bottom: 25px;
}

.tab-buttons {
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 8px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  width: fit-content;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  background: transparent;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tab-btn:hover {
  background: rgba(166, 124, 82, 0.1);
}

.tab-btn.active {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.tab-icon {
  font-size: 18px;
}

.tab-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  background: #f44336;
  color: white;
  font-size: 11px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 内容区域 */
.content-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

/* 发布公告布局 */
.publish-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 25px;
}

.publish-form-panel,
.notice-list-panel {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.15);
}

.panel-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0 0 20px 0;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(166, 124, 82, 0.1);
}

.form-section {
  margin-bottom: 20px;
}

.form-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
}

/* 类型卡片 */
.type-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.type-card {
  padding: 15px;
  background: rgba(255, 255, 255, 0.6);
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.type-card:hover {
  border-color: rgba(243, 129, 129, 0.4);
  transform: translateY(-2px);
}

.type-card.active {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.2);
}

.type-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.type-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  color: #a67c52;
  margin-bottom: 4px;
}

.type-desc {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

/* 表单输入 */
.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.6);
  outline: none;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin-top: 6px;
}

/* 编辑器工具栏 */
.editor-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  padding: 10px;
  background: rgba(166, 124, 82, 0.05);
  border-radius: 8px;
}

.tool-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.tool-btn:hover {
  background: rgba(243, 129, 129, 0.2);
  transform: scale(1.1);
}

.divider {
  width: 1px;
  height: 24px;
  background: rgba(166, 124, 82, 0.2);
  margin: 0 5px;
}

.form-textarea.editor {
  min-height: 150px;
  resize: vertical;
}

/* 设置行 */
.setting-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
}

/* 复选框 */
.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  padding: 15px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  transition: all 0.3s ease;
}

.checkbox-label:hover {
  border-color: rgba(243, 129, 129, 0.4);
}

.checkbox-label input {
  display: none;
}

.custom-checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(166, 124, 82, 0.4);
  border-radius: 6px;
  position: relative;
  flex-shrink: 0;
  margin-top: 2px;
  transition: all 0.3s ease;
}

.checkbox-label input:checked + .custom-checkbox {
  background: linear-gradient(to right, #f38181, #f77d5f);
  border-color: #f38181;
}

.checkbox-label input:checked + .custom-checkbox::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.checkbox-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.checkbox-text strong {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.checkbox-text small {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

/* 表单操作 */
.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.preview-btn,
.submit-btn {
  flex: 1;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.preview-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
}

.preview-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.submit-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 公告列表面板 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(166, 124, 82, 0.1);
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 6px 14px;
  border: none;
  border-radius: 20px;
  background: rgba(166, 124, 82, 0.1);
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab:hover {
  background: rgba(166, 124, 82, 0.2);
}

.filter-tab.active {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 800px;

}

.notice-item {
  position: relative;
  padding: 15px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.15);
  transition: all 0.3s ease;
  pointer-events: auto;
}

.notice-item:hover {
  transform: translateX(4px);
  border-color: rgba(243, 129, 129, 0.3);
}

.notice-item.top {
  border-color: rgba(243, 129, 129, 0.4);
  background: rgba(243, 129, 129, 0.08);
}

.notice-item.expired {
  opacity: 0.7;
}

.notice-item.pending {
  border-style: dashed;
}

.notice-badge {
  position: absolute;
  top: -12px;
  right: 15px;
  padding: 5px 14px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(243, 129, 129, 0.3);
  z-index: 10;
}

.notice-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 10px;
}





.notice-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  z-index: 1;
  position: relative;

}

.action-icon {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: rgba(166, 124, 82, 0.1);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-icon:hover {
  background: rgba(166, 124, 82, 0.2);
  transform: scale(1.1);
}

.action-icon.danger:hover {
  background: rgba(244, 67, 54, 0.15);
}

/* 新的按钮样式 */
.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
  pointer-events: auto;
  user-select: none;
  z-index: 2;
}

.action-btn.edit {
  background: rgba(33, 150, 243, 0.1);
  color: #2196f3;
}

.action-btn.edit:hover {
  background: rgba(33, 150, 243, 0.2);
  transform: translateY(-1px);
}

.action-btn.top {
  background: rgba(243, 129, 129, 0.1);
  color: #f38181;
}

.action-btn.top:hover {
  background: rgba(243, 129, 129, 0.2);
  transform: translateY(-1px);
}

.action-btn.delete {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

.action-btn.delete:hover {
  background: rgba(244, 67, 54, 0.2);
  transform: translateY(-1px);
}

.notice-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 15px;
  color: #a67c52;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.notice-content {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.notice-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

.meta-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.meta-status.active { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
.meta-status.expired { background: rgba(158, 158, 158, 0.15); color: #9e9e9e; }
.meta-status.pending { background: rgba(255, 152, 0, 0.15); color: #ff9800; }



.empty-state {
  text-align: center;
  padding: 40px 0;
  color: rgba(166, 124, 82, 0.6);
}

.empty-state .empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.preview-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.preview-header h3 {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0;
}

.preview-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.preview-notice {
  padding: 25px;
  border-radius: 16px;
  background: rgba(166, 124, 82, 0.05);
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.preview-badge {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  margin-bottom: 15px;
}

.preview-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 22px;
  color: #a67c52;
  margin: 0 0 15px 0;
  line-height: 1.4;
}

.preview-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.preview-content {
  font-size: 15px;
  color: rgba(166, 124, 82, 0.9);
  line-height: 1.8;
  white-space: pre-wrap;
}

.preview-footer {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
  text-align: center;
}

.confirm-read-btn {
  padding: 12px 40px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.preview-footer-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.confirm-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 450px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.confirm-content {
  text-align: center;
  padding: 10px 0;
}

.confirm-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0 0 20px 0;
}

.confirm-detail-box {
  padding: 20px;
  border-radius: 12px;
  background: rgba(244, 67, 54, 0.08);
  border: 2px solid rgba(244, 67, 54, 0.2);
  margin-bottom: 20px;
}

.confirm-detail {
  font-size: 15px;
  color: #f44336;
  font-weight: 600;
  margin: 0;
  word-break: break-all;
}

.confirm-hint {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin: 0;
}




.modal-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 1200px) {
  .publish-layout {
    grid-template-columns: 1fr;
  }
  
  .vio-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .type-cards {
    grid-template-columns: 1fr;
  }
  
  .setting-row {
    grid-template-columns: 1fr;
  }
  
  .violation-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .vio-actions {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .ban-duration {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>