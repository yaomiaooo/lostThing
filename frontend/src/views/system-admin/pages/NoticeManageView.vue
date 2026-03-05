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
          <p class="page-subtitle">发布全局公告，处置违规、虚假发布信息</p>
        </section>

        <!-- 标签页 -->
        <section class="notice-tabs">
          <div class="tab-buttons">
            <button 
              v-for="tab in tabs" 
              :key="tab.key"
              class="tab-btn"
              :class="{ active: currentTab === tab.key }"
              @click="switchTab(tab.key)"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-text">{{ tab.label }}</span>
              <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
            </button>
          </div>
        </section>

        <!-- 公告发布 -->
        <section v-if="currentTab === 'publish'" class="content-section">
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

        <!-- 违规处置 -->
        <section v-if="currentTab === 'violation'" class="content-section">
          <!-- 统计卡片 -->
          <div class="violation-stats">
            <div class="vio-stat-card warning">
              <div class="vio-icon"></div>
              <div class="vio-info">
                <span class="vio-value">{{ violationStats.pending }}</span>
                <span class="vio-label">待处理举报</span>
              </div>
            </div>
            <div class="vio-stat-card info">
              <div class="vio-icon"></div>
              <div class="vio-info">
                <span class="vio-value">{{ violationStats.today }}</span>
                <span class="vio-label">今日举报</span>
              </div>
            </div>
            <div class="vio-stat-card success">
              <div class="vio-icon"></div>
              <div class="vio-info">
                <span class="vio-value">{{ violationStats.resolved }}</span>
                <span class="vio-label">已处理</span>
              </div>
            </div>
            <div class="vio-stat-card danger">
              <div class="vio-icon"></div>
              <div class="vio-info">
                <span class="vio-value">{{ violationStats.deleted }}</span>
                <span class="vio-label">已删除内容</span>
              </div>
            </div>
          </div>

          <!-- 筛选工具栏 -->
          <div class="toolbar">
            <div class="toolbar-left">
              <select v-model="violationFilter.status" class="filter-select" @change="loadViolations">
                <option value="">全部状态</option>
                <option value="pending">待处理</option>
                <option value="processing">处理中</option>
                <option value="resolved">已处理</option>
              </select>
              <select v-model="violationFilter.type" class="filter-select" @change="loadViolations">
                <option value="">全部类型</option>
                <option value="fake">虚假信息</option>
                <option value="spam">垃圾广告</option>
                <option value="abuse">恶意辱骂</option>
                <option value="fraud">诈骗欺诈</option>
                <option value="other">其他违规</option>
              </select>
            </div>
            <div class="toolbar-right">
              <button class="refresh-btn" @click="loadViolations">
                <span :class="{ rotating: loading }"></span> 刷新
              </button>
            </div>
          </div>

          <!-- 举报列表 -->
          <div class="violation-list">
            <div 
              v-for="item in violationList" 
              :key="item.reportId"
              class="violation-card"
              :class="{ urgent: item.urgent }"
            >
              <div class="vio-header">
                <div class="vio-type">
                  <span class="type-tag" :class="'type-' + item.type">{{ getViolationType(item.type) }}</span>
                  <span class="status-tag" :class="'status-' + item.status">{{ getViolationStatus(item.status) }}</span>
                </div>
                <span class="vio-time">{{ timeAgo(item.createTime) }}</span>
              </div>

              <div class="vio-content">
                <div class="reported-item">
                  <div class="item-preview" v-if="item.itemImage">
                    <img :src="item.itemImage" />
                  </div>
                  <div class="item-info">
                    <h4 class="item-title">{{ item.itemTitle }}</h4>
                    <p class="item-desc">{{ truncateText(item.itemDesc, 80) }}</p>
                    <div class="item-meta">
                      <span>{{ item.publisherName }}</span>
                      <span>{{ formatDate(item.publishTime) }}</span>
                    </div>
                  </div>
                </div>

                <div class="report-info">
                  <div class="report-reason">
                    <strong>举报原因：</strong>
                    <p>{{ item.reason }}</p>
                  </div>
                  <div class="reporter">
                    <span>举报人：{{ item.reporterName }}</span>
                    <span>联系方式：{{ maskPhone(item.reporterContact) }}</span>
                  </div>
                  <div class="evidence" v-if="item.evidenceImages?.length">
                    <strong>证据图片：</strong>
                    <div class="evidence-images">
                      <img 
                        v-for="(img, idx) in item.evidenceImages" 
                        :key="idx"
                        :src="img"
                        @click="previewImage(img)"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div class="vio-actions">
                <template v-if="item.status === 'pending' || item.status === 'processing'">
                  <button class="action-btn view" @click="viewItemDetail(item)">
                    查看原帖
                  </button>
                  <button class="action-btn warn" @click="handleWarn(item)">
                    警告用户
                  </button>
                  <button class="action-btn delete" @click="confirmDeleteItem(item)">
                    删除内容
                  </button>
                  <button class="action-btn ban" @click="confirmBanUser(item)">
                    封禁用户
                  </button>
                </template>
                <template v-else>
                  <div class="resolve-info">
                    <span>处理人：{{ item.handlerName }}</span>
                    <span>结果：{{ item.resolveResult }}</span>
                    <span>时间：{{ formatDate(item.resolveTime) }}</span>
                  </div>
                </template>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="violationList.length === 0 && !loading" class="empty-state large">
            <div class="empty-icon"></div>
            <h3>暂无违规举报</h3>
            <p>系统运行良好，未发现违规内容</p>
          </div>

          <!-- 分页 -->
          <div class="pagination" v-if="violationList.length > 0">
            <button 
              class="page-btn" 
              :disabled="violationPage === 1"
              @click="changeViolationPage(violationPage - 1)"
            >
              上一页
            </button>
            <span class="page-info">第 {{ violationPage }} 页</span>
            <button 
              class="page-btn" 
              @click="changeViolationPage(violationPage + 1)"
            >
              下一页
            </button>
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
          <div class="preview-notice" :class="'preview-' + publishForm.type">

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

    <!-- 处置弹窗 -->
    <div v-if="showActionModal" class="modal-overlay" @click.self="closeActionModal">
      <div class="action-modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ actionTitle }}</h3>
          <button class="modal-close" @click="closeActionModal">×</button>
        </div>
        <div class="modal-body">
          <div class="action-target">
            <strong>处置对象：</strong>
            <p>{{ actionTarget }}</p>
          </div>
          <div class="form-group">
            <label class="form-label">处置原因 <span class="required">*</span></label>
            <textarea 
              v-model="actionReason"
              class="form-textarea"
              rows="4"
              placeholder="请详细说明处置原因..."
            ></textarea>
          </div>
          <div class="form-group" v-if="actionType === 'ban'">
            <label class="form-label">封禁时长</label>
            <div class="ban-duration">
              <label class="radio-card">
                <input type="radio" v-model="banDuration" value="1d">
                <span>1天</span>
              </label>
              <label class="radio-card">
                <input type="radio" v-model="banDuration" value="7d">
                <span>7天</span>
              </label>
              <label class="radio-card">
                <input type="radio" v-model="banDuration" value="30d">
                <span>30天</span>
              </label>
              <label class="radio-card">
                <input type="radio" v-model="banDuration" value="forever">
                <span>永久</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeActionModal">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="!actionReason.trim()"
            @click="executeAction"
          >
            确认处置
          </button>
        </div>
      </div>
    </div>

    <!-- 图片预览 -->
    <div v-if="previewImageUrl" class="image-preview-overlay" @click.self="closeImagePreview">
      <img :src="previewImageUrl" class="preview-large" />
      <button class="preview-close" @click="closeImagePreview">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SysAdminNavigation from '../components/SysAdminNavigation.vue'

const router = useRouter()

/* ================= 标签页配置 ================= */
const tabs = [
  { key: 'publish', label: '发布公告', icon: '' },
  { key: 'violation', label: '违规处置', icon: '', badge: null }
]
const currentTab = ref('publish')

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

/* ================= 违规处置 ================= */
const violationStats = reactive({
  pending: 0,
  today: 0,
  resolved: 0,
  deleted: 0
})

const violationFilter = reactive({
  status: '',
  type: ''
})

const violationList = ref<any[]>([])
const violationPage = ref(1)
const loading = ref(false)

/* ================= 弹窗状态 ================= */
const showPreviewModal = ref(false)
const showDeleteModal = ref(false)
const showActionModal = ref(false)
const deletingNotice = ref<any>(null)
const actionType = ref<'warn' | 'delete' | 'ban'>('warn')
const actionTarget = ref('')
const actionTitle = ref('')
const actionReason = ref('')
const banDuration = ref('7d')
const currentViolation = ref<any>(null)
const previewImageUrl = ref('')

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

/* ================= 标签切换 ================= */
const switchTab = (tab: string) => {
  currentTab.value = tab
  if (tab === 'publish') loadNotices()
  if (tab === 'violation') loadViolations()
}

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

/* ================= 违规处置方法 ================= */
const loadViolations = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/violations', {
      params: {
        page: violationPage.value,
        status: violationFilter.status || undefined,
        type: violationFilter.type || undefined
      }
    })
    if (res.data.code === 200) {
      violationList.value = res.data.data.list || []
      Object.assign(violationStats, res.data.data.statistics || {})
    }
  } catch (error) {
    violationList.value = [
      {
        reportId: 1,
        type: 'fake',
        status: 'pending',
        urgent: true,
        itemTitle: '捡到iPhone 15 Pro Max',
        itemDesc: '在图书馆捡到全新iPhone，要求支付500元感谢费才归还...',
        itemImage: null,
        publisherName: '用户A',
        publishTime: '2026-03-01 10:30:00',
        reason: '疑似诈骗，要求先转账才给物品',
        reporterName: '受害者B',
        reporterContact: '13800138000',
        evidenceImages: [],
        createTime: '2026-03-01 11:00:00'
      },
      {
        reportId: 2,
        type: 'spam',
        status: 'pending',
        urgent: false,
        itemTitle: '低价出售各类物品',
        itemDesc: '大量出售二手物品，加微信咨询...',
        itemImage: null,
        publisherName: '广告用户',
        publishTime: '2026-02-28 15:20:00',
        reason: '发布广告信息，非失物招领内容',
        reporterName: '热心用户',
        reporterContact: '13900139000',
        evidenceImages: [],
        createTime: '2026-03-01 09:15:00'
      }
    ]
    violationStats.pending = 2
    violationStats.today = 2
    violationStats.resolved = 15
    violationStats.deleted = 8
  } finally {
    loading.value = false
  }
}

const changeViolationPage = (page: number) => {
  violationPage.value = page
  loadViolations()
}

const viewItemDetail = (item: any) => {
  router.push(`/item-admin/items?itemId=${item.itemId}`)
}

const handleWarn = (item: any) => {
  currentViolation.value = item
  actionType.value = 'warn'
  actionTitle.value = '警告用户'
  actionTarget.value = `用户：${item.publisherName}`
  actionReason.value = ''
  showActionModal.value = true
}

const confirmDeleteItem = (item: any) => {
  currentViolation.value = item
  actionType.value = 'delete'
  actionTitle.value = '删除违规内容'
  actionTarget.value = `帖子：${item.itemTitle}`
  actionReason.value = ''
  showActionModal.value = true
}

const confirmBanUser = (item: any) => {
  currentViolation.value = item
  actionType.value = 'ban'
  actionTitle.value = '封禁用户'
  actionTarget.value = `用户：${item.publisherName}`
  actionReason.value = ''
  banDuration.value = '7d'
  showActionModal.value = true
}

const closeActionModal = () => {
  showActionModal.value = false
  currentViolation.value = null
  actionReason.value = ''
}

const executeAction = async () => {
  if (!currentViolation.value || !actionReason.value.trim()) return
  
  try {
    let url = ''
    const payload: any = {
      reportId: currentViolation.value.reportId,
      reason: actionReason.value
    }
    
    if (actionType.value === 'warn') {
      url = '/api/admin/violations/warn'
    } else if (actionType.value === 'delete') {
      url = '/api/admin/violations/delete'
    } else if (actionType.value === 'ban') {
      url = '/api/admin/violations/ban'
      payload.duration = banDuration.value
    }
    
    const res = await axios.post(url, payload)
    if (res.data.code === 200) {
      // 更新列表状态
      currentViolation.value.status = 'resolved'
      currentViolation.value.resolveResult = actionType.value === 'warn' ? '警告' : actionType.value === 'delete' ? '删除' : '封禁'
      currentViolation.value.handlerName = '当前管理员'
      currentViolation.value.resolveTime = new Date().toISOString()
      
      await loadViolations()
      closeActionModal()
    }
  } catch (error) {
    alert('处置失败，请重试')
  }
}

const previewImage = (url: string) => {
  previewImageUrl.value = url
}

const closeImagePreview = () => {
  previewImageUrl.value = ''
}

/* ================= 工具函数 ================= */
const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    system: '系统',
    policy: '政策',
    activity: '活动',
    urgent: '紧急'
  }
  return map[type] || '其他'
}

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

const getViolationType = (type: string) => {
  const map: Record<string, string> = {
    fake: '虚假信息',
    spam: '垃圾广告',
    abuse: '恶意辱骂',
    fraud: '诈骗欺诈',
    other: '其他违规'
  }
  return map[type] || '未知'
}

const getViolationStatus = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已处理'
  }
  return map[status] || status
}

const formatDate = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const timeAgo = (timeStr: string) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  return `${Math.floor(diff / 86400)}天前`
}

const truncateText = (text: string, length: number) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const maskPhone = (phone: string) => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
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

/* 违规处置区域 */
.violation-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.vio-stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  transition: all 0.3s ease;
}

.vio-stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.vio-stat-card.warning { border-color: rgba(255, 152, 0, 0.3); background: rgba(255, 152, 0, 0.05); }
.vio-stat-card.info { border-color: rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05); }
.vio-stat-card.success { border-color: rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05); }
.vio-stat-card.danger { border-color: rgba(244, 67, 54, 0.3); background: rgba(244, 67, 54, 0.05); }

.vio-icon {
  font-size: 32px;
}

.vio-info {
  display: flex;
  flex-direction: column;
}

.vio-value {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: #a67c52;
  font-weight: 700;
}

.vio-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  outline: none;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  background: rgba(166, 124, 82, 0.1);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.refresh-btn .rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 违规列表 */
.violation-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.violation-card {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  transition: all 0.3s ease;
}

.violation-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.violation-card.urgent {
  border-color: rgba(244, 67, 54, 0.4);
  background: rgba(244, 67, 54, 0.05);
}

.vio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.vio-type {
  display: flex;
  gap: 10px;
}

.type-tag,
.status-tag {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.type-tag.type-fake { background: rgba(244, 67, 54, 0.15); color: #f44336; }
.type-tag.type-spam { background: rgba(255, 152, 0, 0.15); color: #ff9800; }
.type-tag.type-abuse { background: rgba(156, 39, 176, 0.15); color: #9c27b0; }
.type-tag.type-fraud { background: rgba(244, 67, 54, 0.2); color: #d32f2f; }
.type-tag.type-other { background: rgba(158, 158, 158, 0.15); color: #757575; }

.status-tag.status-pending { background: rgba(255, 152, 0, 0.15); color: #ff9800; }
.status-tag.status-processing { background: rgba(33, 150, 243, 0.15); color: #2196f3; }
.status-tag.status-resolved { background: rgba(76, 175, 80, 0.15); color: #4caf50; }

.vio-time {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.6);
}

.vio-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.reported-item {
  display: flex;
  gap: 15px;
}

.item-preview {
  width: 100px;
  height: 100px;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(166, 124, 82, 0.1);
  flex-shrink: 0;
}

.item-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
}

.item-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 16px;
  color: #a67c52;
  margin: 0 0 8px 0;
}

.item-desc {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
  margin: 0 0 10px 0;
  line-height: 1.5;
}

.item-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-reason,
.reporter,
.evidence {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.9);
}

.report-reason strong,
.evidence strong {
  display: block;
  margin-bottom: 6px;
  color: #a67c52;
}

.report-reason p {
  margin: 0;
  padding: 10px;
  background: rgba(244, 67, 54, 0.05);
  border-radius: 8px;
  border-left: 3px solid #f44336;
}

.evidence-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.evidence-images img {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  object-fit: cover;
  cursor: pointer;
  transition: all 0.3s ease;
}

.evidence-images img:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.vio-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn.view {
  background: rgba(33, 150, 243, 0.15);
  color: #2196f3;
}

.action-btn.view:hover {
  background: rgba(33, 150, 243, 0.25);
}

.action-btn.warn {
  background: rgba(255, 152, 0, 0.15);
  color: #ff9800;
}

.action-btn.warn:hover {
  background: rgba(255, 152, 0, 0.25);
}

.action-btn.delete {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.action-btn.delete:hover {
  background: rgba(244, 67, 54, 0.25);
}

.action-btn.ban {
  background: rgba(156, 39, 176, 0.15);
  color: #9c27b0;
}

.action-btn.ban:hover {
  background: rgba(156, 39, 176, 0.25);
}

.resolve-info {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
  padding: 10px 15px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 8px;
}

/* 空状态 */
.empty-state.large {
  padding: 60px 0;
  text-align: center;
}

.empty-state.large .empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.empty-state.large h3 {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 22px;
  color: #a67c52;
  margin: 0 0 10px 0;
}

.empty-state.large p {
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.page-btn {
  padding: 10px 20px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
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

.preview-notice.preview-system { border-color: rgba(33, 150, 243, 0.3); background: rgba(33, 150, 243, 0.05); }
.preview-notice.preview-policy { border-color: rgba(156, 39, 176, 0.3); background: rgba(156, 39, 176, 0.05); }
.preview-notice.preview-activity { border-color: rgba(76, 175, 80, 0.3); background: rgba(76, 175, 80, 0.05); }
.preview-notice.preview-urgent { border-color: rgba(244, 67, 54, 0.3); background: rgba(244, 67, 54, 0.05); }

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

.action-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.action-target {
  padding: 15px;
  background: rgba(166, 124, 82, 0.05);
  border-radius: 10px;
  margin-bottom: 20px;
}

.action-target strong {
  display: block;
  margin-bottom: 6px;
  color: #a67c52;
}

.action-target p {
  margin: 0;
  color: #f44336;
  font-weight: 600;
}

.ban-duration {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.radio-card {
  position: relative;
  padding: 15px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.radio-card input {
  display: none;
}

.radio-card span {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
}

.radio-card:has(input:checked) {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.preview-large {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  border-radius: 8px;
}

.preview-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
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