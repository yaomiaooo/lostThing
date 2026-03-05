<!-- src/views/system-admin/pages/DataManageView.vue -->
<template>
  <div class="data-manage-page">
    <!-- 背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航 -->
      <SysAdminNavigation 
        subtitle="数据管理"
        active-nav="数据管理"
        @logout="handleLogout"
      />

      <!-- 右侧主内容 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">数据管理中心</h1>
          <p class="page-subtitle">备份、导出、清理系统数据，处理用户投诉与反馈</p>
        </section>

        <!-- 数据概览卡片 -->
        <section class="data-overview">
          <div class="overview-card">
            <div class="overview-info">
              <span class="overview-value">{{ dataStats.items.total }}</span>
              <span class="overview-label">物品总数</span>
              <span class="overview-trend">本月新增 {{ dataStats.items.thisMonth }}</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="overview-info">
              <span class="overview-value">{{ dataStats.users.total }}</span>
              <span class="overview-label">注册用户</span>
              <span class="overview-trend">活跃 {{ dataStats.users.active }}</span>
            </div>
          </div>
          <div class="overview-card">
            <div class="overview-info">
              <span class="overview-value">{{ dataStats.images.count }}</span>
              <span class="overview-label">图片资源</span>
              <span class="overview-trend">占用 {{ formatSize(dataStats.images.size) }}</span>
            </div>
          </div>
          <div class="overview-card warning">
            <div class="overview-info">
              <span class="overview-value">{{ dataStats.trash.count }}</span>
              <span class="overview-label">待清理数据</span>
              <span class="overview-trend">可释放 {{ formatSize(dataStats.trash.size) }}</span>
            </div>
          </div>
        </section>

        <!-- 标签页 -->
        <section class="data-tabs">
          <div class="tab-buttons">
            <button 
              v-for="tab in tabs" 
              :key="tab.key"
              class="tab-btn"
              :class="{ active: currentTab === tab.key }"
              @click="switchTab(tab.key)"
            >
              <span class="tab-text">{{ tab.label }}</span>
            </button>
          </div>
        </section>

        <!-- 数据备份 -->
        <section v-if="currentTab === 'backup'" class="content-section">
          <div class="backup-layout">
            <!-- 自动备份设置 -->
            <div class="backup-config-panel">
              <h3 class="panel-title">自动备份设置</h3>
              
              <div class="config-item">
                <div class="config-header">
                  <label class="toggle-label">
                    <span class="toggle-switch">
                      <input type="checkbox" v-model="backupConfig.autoEnabled">
                      <span class="slider"></span>
                    </span>
                    <span class="label-text">启用自动备份</span>
                  </label>
                  <span class="config-status" :class="{ active: backupConfig.autoEnabled }">
                    {{ backupConfig.autoEnabled ? '已启用' : '已禁用' }}
                  </span>
                </div>
                <p class="config-desc">系统将按照设定周期自动执行全量备份</p>
              </div>

              <div class="config-item" v-if="backupConfig.autoEnabled">
                <label class="config-label">备份周期</label>
                <div class="cycle-options">
                  <label class="cycle-radio">
                    <input type="radio" v-model="backupConfig.cycle" value="daily">
                    <span>每天</span>
                  </label>
                  <label class="cycle-radio">
                    <input type="radio" v-model="backupConfig.cycle" value="weekly">
                    <span>每周</span>
                  </label>
                  <label class="cycle-radio">
                    <input type="radio" v-model="backupConfig.cycle" value="monthly">
                    <span>每月</span>
                  </label>
                </div>
              </div>

              <div class="config-item" v-if="backupConfig.autoEnabled">
                <label class="config-label">备份时间</label>
                <input type="time" v-model="backupConfig.time" class="time-input">
                <p class="config-hint">建议选择系统低峰期执行，避免影响用户体验</p>
              </div>

              <div class="config-item">
                <label class="config-label">保留策略</label>
                <div class="retention-setting">
                  <span>保留最近</span>
                  <input type="number" v-model.number="backupConfig.retention" min="1" max="30" class="number-input">
                  <span>个备份</span>
                </div>
                <p class="config-hint">超过保留数量的旧备份将被自动删除</p>
              </div>

              <button class="save-config-btn" @click="saveBackupConfig">
                保存设置
              </button>
            </div>

            <!-- 备份历史与手动备份 -->
            <div class="backup-history-panel">
              <div class="panel-header">
                <h3 class="panel-title">备份记录</h3>
                <button class="manual-backup-btn" @click="startManualBackup" :disabled="backingUp">
                  <span v-if="backingUp" class="loading-spinner-small"></span>
                  <span v-else>立即备份</span>
                </button>
              </div>

              <!-- 备份进度 -->
              <div v-if="backupProgress.show" class="backup-progress">
                <div class="progress-header">
                  <span>{{ backupProgress.status }}</span>
                  <span>{{ backupProgress.percent }}%</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: backupProgress.percent + '%' }"></div>
                </div>
                <div class="progress-detail">
                  <span>{{ backupProgress.currentTable }}</span>
                  <span>{{ backupProgress.processed }} / {{ backupProgress.total }} 表</span>
                </div>
              </div>

              <div class="backup-list">
                <div 
                  v-for="backup in backupList" 
                  :key="backup.id"
                  class="backup-item"
                  :class="{ 'auto-backup': backup.type === 'auto' }"
                >
                  <div class="backup-icon">
                    {{ backup.type === 'auto' ? '🤖' : '👤' }}
                  </div>
                  <div class="backup-info">
                    <div class="backup-name">{{ backup.name }}</div>
                    <div class="backup-meta">

                      <span :class="['backup-status', backup.status]">{{ getBackupStatus(backup.status) }}</span>
                    </div>
                    <div class="backup-tables">
                      包含: {{ backup.tables.join(', ') }}
                    </div>
                  </div>
                  <div class="backup-actions">
                    <button class="action-btn" @click="downloadBackup(backup)" title="下载">⬇️</button>
                    <button class="action-btn" @click="restoreBackup(backup)" title="恢复">↩️</button>
                    <button class="action-btn danger" @click="deleteBackup(backup)" title="删除">🗑️</button>
                  </div>
                </div>
              </div>

              <div v-if="backupList.length === 0" class="empty-state">
                <div class="empty-icon">💾</div>
                <p>暂无备份记录</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 数据导出 -->
        <section v-if="currentTab === 'export'" class="content-section">
          <div class="export-layout">
            <!-- 导出选项 -->
            <div class="export-options-panel">
              <h3 class="panel-title">数据导出</h3>
              
              <div class="export-section">
                <label class="section-label">选择数据范围</label>
                <div class="range-options">
                  <label class="range-card" :class="{ active: exportForm.range === 'all' }">
                    <input type="radio" v-model="exportForm.range" value="all">
                    <span class="range-icon">📦</span>
                    <span class="range-name">全部数据</span>
                    <span class="range-desc">导出系统所有历史数据</span>
                  </label>
                  <label class="range-card" :class="{ active: exportForm.range === 'year' }">
                    <input type="radio" v-model="exportForm.range" value="year">
                    <span class="range-icon">📅</span>
                    <span class="range-name">本年度</span>
                    <span class="range-desc">仅导出当前年度数据</span>
                  </label>
                  <label class="range-card" :class="{ active: exportForm.range === 'custom' }">
                    <input type="radio" v-model="exportForm.range" value="custom">
                    <span class="range-icon">🎯</span>
                    <span class="range-name">自定义</span>
                    <span class="range-desc">指定时间范围导出</span>
                  </label>
                </div>

                <div v-if="exportForm.range === 'custom'" class="custom-range">
                  <div class="date-inputs">
                    <div class="date-field">
                      <label>开始日期</label>
                      <input type="date" v-model="exportForm.startDate" class="form-input">
                    </div>
                    <div class="date-field">
                      <label>结束日期</label>
                      <input type="date" v-model="exportForm.endDate" class="form-input">
                    </div>
                  </div>
                </div>
              </div>

              <div class="export-section">
                <label class="section-label">选择数据类型</label>
                <div class="data-types">
                  <label class="type-checkbox" v-for="type in exportDataTypes" :key="type.value">
                    <input type="checkbox" v-model="exportForm.types" :value="type.value">
                    <span class="custom-checkbox"></span>
                    <div class="type-info">
                      <span class="type-name">{{ type.label }}</span>
                      <span class="type-desc">{{ type.desc }}</span>
                    </div>
                  </label>
                </div>
              </div>

              <div class="export-section">
                <label class="section-label">导出格式</label>
                <div class="format-options">
                  <label class="format-radio" :class="{ active: exportForm.format === 'excel' }">
                    <input type="radio" v-model="exportForm.format" value="excel">
                    <span class="format-icon">📊</span>
                    <span>Excel</span>
                  </label>
                  <label class="format-radio" :class="{ active: exportForm.format === 'csv' }">
                    <input type="radio" v-model="exportForm.format" value="csv">
                    <span class="format-icon">📄</span>
                    <span>CSV</span>
                  </label>
                  <label class="format-radio" :class="{ active: exportForm.format === 'json' }">
                    <input type="radio" v-model="exportForm.format" value="json">
                    <span class="format-icon">🗂️</span>
                    <span>JSON</span>
                  </label>
                </div>
              </div>

              <div class="export-section">
                <label class="type-checkbox">
                  <input type="checkbox" v-model="exportForm.includeImages">
                  <span class="custom-checkbox"></span>
                  <div class="type-info">
                    <span class="type-name">包含图片资源</span>
                    <span class="type-desc">将导出相关图片文件（会显著增加导出时间和文件大小）</span>
                  </div>
                </label>
              </div>

              <button 
                class="export-btn" 
                :disabled="!canExport || exporting"
                @click="startExport"
              >
                <span v-if="exporting" class="loading-spinner-small"></span>
                <span v-else>开始导出</span>
              </button>
            </div>

            <!-- 导出历史 -->
            <div class="export-history-panel">
              <h3 class="panel-title">导出记录</h3>
              
              <div class="export-list">
                <div 
                  v-for="task in exportHistory" 
                  :key="task.id"
                  class="export-item"
                  :class="{ 'exporting': task.status === 'processing', 'failed': task.status === 'failed' }"
                >
                  <div class="export-status-icon">
                    {{ task.status === 'completed' ? '✅' : task.status === 'processing' ? '🔄' : '❌' }}
                  </div>
                  <div class="export-info">
                    <div class="export-title">{{ task.name }}</div>
                    <div class="export-meta">
                      <span>{{ formatDate(task.createTime) }}</span>
                      <span v-if="task.recordCount && task.recordCount > 0">{{ task.recordCount }} 条记录</span>
                      <span v-if="task.size">{{ formatSize(task.size) }}</span>
                    </div>
                    <div v-if="task.status === 'processing'" class="export-progress">
                      <div class="progress-bar mini">
                        <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
                      </div>
                      <span>{{ task.progress }}%</span>
                    </div>
                    <div v-if="task.status === 'failed'" class="export-error">
                      失败原因: {{ task.error }}
                    </div>
                  </div>
                  <div class="export-actions">
                    <button 
                      v-if="task.status === 'completed'" 
                      class="action-btn"
                      @click="downloadExport(task)"
                    >
                      ⬇️
                    </button>
                    <button 
                      v-if="task.status === 'failed'" 
                      class="action-btn"
                      @click="retryExport(task)"
                    >
                      🔄
                    </button>
                    <button class="action-btn danger" @click="deleteExport(task)">🗑️</button>
                  </div>
                </div>
              </div>

              <div v-if="exportHistory.length === 0" class="empty-state">
                <div class="empty-icon">📭</div>
                <p>暂无导出记录</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 数据清理 -->
        <section v-if="currentTab === 'cleanup'" class="content-section">
          <div class="cleanup-layout">
            <!-- 清理规则 -->
            <div class="cleanup-rules-panel">
              <h3 class="panel-title">🧹 自动清理规则</h3>
              
              <div class="rule-list">
                <div class="rule-item" v-for="rule in cleanupRules" :key="rule.id">
                  <div class="rule-header">
                    <label class="toggle-switch small">
                      <input type="checkbox" v-model="rule.enabled">
                      <span class="slider"></span>
                    </label>
                    <span class="rule-name">{{ rule.name }}</span>
                    <span class="rule-status" :class="{ active: rule.enabled }">
                      {{ rule.enabled ? '启用' : '禁用' }}
                    </span>
                  </div>
                  <p class="rule-desc">{{ rule.description }}</p>
                  <div class="rule-config" v-if="rule.enabled">
                    <span>保留最近</span>
                    <input type="number" v-model.number="rule.retentionDays" min="1" class="number-input small">
                    <span>天的数据</span>
                  </div>
                  <div class="rule-preview" v-if="rule.enabled">
                    <span>预计清理: {{ rule.estimatedCount }} 条记录 ({{ formatSize(rule.estimatedSize) }})</span>
                  </div>
                </div>
              </div>

              <div class="cleanup-actions">
                <button class="preview-btn" @click="previewCleanup">
                  预览清理效果
                </button>
                <button class="execute-btn" @click="executeCleanup">
                  立即执行清理
                </button>
              </div>
            </div>

            <!-- 手动清理 -->
            <div class="manual-cleanup-panel">
              <h3 class="panel-title">手动清理</h3>
              
              <div class="cleanup-categories">
                <div class="category-card" v-for="cat in cleanupCategories" :key="cat.key">
                  <div class="category-info">
                    <span class="category-name">{{ cat.name }}</span>
                    <span class="category-count">{{ cat.count }} 项</span>
                    <span class="category-size">{{ formatSize(cat.size) }}</span>
                  </div>
                  <button class="cleanup-btn" @click="cleanupCategory(cat)">
                    清理
                  </button>
                </div>
              </div>

              <div class="orphan-files">
                <h4>孤儿文件清理</h4>
                <p class="orphan-desc">数据库中无引用的图片文件，可安全删除</p>
                <div class="orphan-stats">
                  <span>发现 {{ orphanFiles.count }} 个孤儿文件</span>
                  <span>占用 {{ formatSize(orphanFiles.size) }}</span>
                </div>
                <button class="cleanup-btn large" @click="cleanupOrphanFiles">
                  清理孤儿文件
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- 投诉反馈 -->
        <section v-if="currentTab === 'feedback'" class="content-section">
          <div class="feedback-layout">
            <!-- 投诉统计 -->
            <div class="feedback-stats">
              <div class="stat-card" v-for="stat in feedbackStats" :key="stat.label">
                <span class="stat-value">{{ stat.value }}</span>
                <span class="stat-label">{{ stat.label }}</span>
                <span class="stat-change" :class="stat.trend">{{ stat.change }}</span>
              </div>
            </div>

            <!-- 投诉列表 -->
            <div class="feedback-list-panel">
              <div class="panel-header">
                <h3 class="panel-title">用户投诉与反馈</h3>
                <div class="filter-group">
                  <select v-model="feedbackFilter.type" class="filter-select">
                    <option value="">全部类型</option>
                    <option value="bug">系统故障</option>
                    <option value="feature">功能建议</option>
                    <option value="complaint">投诉举报</option>
                    <option value="other">其他</option>
                  </select>
                  <select v-model="feedbackFilter.status" class="filter-select">
                    <option value="">全部状态</option>
                    <option value="pending">待处理</option>
                    <option value="processing">处理中</option>
                    <option value="resolved">已解决</option>
                  </select>
                </div>
              </div>

              <div class="feedback-list">
                <div 
                  v-for="item in feedbackList" 
                  :key="item.id"
                  class="feedback-item"
                  :class="{ urgent: item.priority === 'high', resolved: item.status === 'resolved' }"
                >
                  <div class="feedback-header">
                    <div class="feedback-type">
                      <span class="type-tag" :class="'type-' + item.type">{{ getFeedbackType(item.type) }}</span>
                      <span class="priority-tag" v-if="item.priority === 'high'">紧急</span>
                    </div>
                    <span class="feedback-time">{{ timeAgo(item.createTime) }}</span>
                  </div>
                  
                  <div class="feedback-user">
                    <img :src="item.userAvatar || '/default-avatar.png'" class="user-avatar-small">
                    <div class="user-info">
                      <span class="user-name">{{ item.userName }}</span>
                      <span class="user-contact">{{ maskPhone(item.userPhone) }}</span>
                    </div>
                  </div>

                  <h4 class="feedback-title">{{ item.title }}</h4>
                  <p class="feedback-content">{{ item.content }}</p>

                  <div v-if="item.images?.length" class="feedback-images">
                    <img 
                      v-for="(img, idx) in item.images" 
                      :key="idx"
                      :src="img"
                      @click="previewImage(img)"
                    />
                  </div>

                  <div v-if="item.status === 'resolved'" class="feedback-reply">
                    <div class="reply-header">
                      <span>💬 回复</span>
                      <span>{{ formatDate(item.replyTime) }}</span>
                    </div>
                    <p>{{ item.reply }}</p>
                  </div>

                  <div class="feedback-actions">
                    <template v-if="item.status !== 'resolved'">
                      <button class="action-btn reply" @click="openReplyModal(item)">
                        回复
                      </button>
                      <button class="action-btn resolve" @click="resolveFeedback(item)">
                        标记解决
                      </button>
                    </template>
                    <button class="action-btn contact" @click="contactUser(item)">
                        联系用户
                      </button>
                  </div>
                </div>
              </div>

              <div v-if="feedbackList.length === 0" class="empty-state large">
                <h3>暂无待处理反馈</h3>
                <p>系统运行良好，用户满意度高</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 恢复确认弹窗 -->
    <div v-if="showRestoreModal" class="modal-overlay" @click.self="closeRestoreModal">
      <div class="confirm-modal large">
        <div class="modal-header">
          <h3 class="modal-title">确认恢复备份</h3>
          <button class="modal-close" @click="closeRestoreModal">×</button>
        </div>
        <div class="modal-body">
          <div class="warning-box">
            <div class="warning-content">
              <h4>此操作将覆盖当前数据！</h4>
              <p>恢复备份将清空现有数据库并用备份数据替换，此操作不可撤销。</p>
            </div>
          </div>
          
          <div class="restore-info">
            <div class="info-row">
              <span>备份名称:</span>
              <strong>{{ restoringBackup?.name }}</strong>
            </div>
            <div class="info-row">
              <span>备份时间:</span>
              <strong>{{ formatDate(restoringBackup?.createTime) }}</strong>
            </div>
            <div class="info-row">
              <span>数据规模:</span>
              <strong>{{ formatSize(restoringBackup?.size) }}</strong>
            </div>
          </div>

          <div class="confirm-input">
            <label>请输入 "RESTORE" 以确认操作</label>
            <input 
              type="text" 
              v-model="restoreConfirmText"
              class="form-input"
              placeholder="RESTORE"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeRestoreModal">取消</button>
          <button 
            class="modal-btn danger-btn" 
            :disabled="restoreConfirmText !== 'RESTORE'"
            @click="executeRestore"
          >
            确认恢复
          </button>
        </div>
      </div>
    </div>

    <!-- 清理确认弹窗 -->
    <div v-if="showCleanupModal" class="modal-overlay" @click.self="closeCleanupModal">
      <div class="confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">确认数据清理</h3>
          <button class="modal-close" @click="closeCleanupModal">×</button>
        </div>
        <div class="modal-body">
          <div class="cleanup-preview">
            <h4>即将清理以下数据：</h4>
            <ul class="cleanup-list">
              <li v-for="item in cleanupPreview" :key="item.name">
                <span>{{ item.name }}</span>
                <strong>{{ item.count }} 条 ({{ formatSize(item.size) }})</strong>
              </li>
            </ul>
            <div class="cleanup-total">
              <span>预计释放空间:</span>
              <strong>{{ formatSize(cleanupPreviewTotal) }}</strong>
            </div>
          </div>
          <p class="cleanup-warning">清理后的数据将无法恢复，请确认已备份重要数据</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeCleanupModal">取消</button>
          <button class="modal-btn danger-btn" @click="executeCleanup">确认清理</button>
        </div>
      </div>
    </div>

    <!-- 回复弹窗 -->
    <div v-if="showReplyModal" class="modal-overlay" @click.self="closeReplyModal">
      <div class="reply-modal">
        <div class="modal-header">
          <h3 class="modal-title">回复用户反馈</h3>
          <button class="modal-close" @click="closeReplyModal">×</button>
        </div>
        <div class="modal-body">
          <div class="reply-to">
            <span>回复给: {{ replyingFeedback?.userName }}</span>
          </div>
          <div class="original-content">
            <strong>原反馈:</strong>
            <p>{{ replyingFeedback?.content }}</p>
          </div>
          <textarea 
            v-model="replyContent"
            class="form-textarea"
            rows="6"
            placeholder="请输入回复内容..."
          ></textarea>
          <label class="checkbox-label">
            <input type="checkbox" v-model="replyAndResolve">
            <span class="custom-checkbox"></span>
            <span>同时标记为已解决</span>
          </label>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeReplyModal">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="!replyContent.trim()"
            @click="sendReply"
          >
            发送回复
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
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SysAdminNavigation from '../components/SysAdminNavigation.vue'

const router = useRouter()

/* ================= 标签页配置 ================= */
const tabs = [
  { key: 'backup', label: '数据备份' },
  { key: 'export', label: '数据导出' },
  { key: 'cleanup', label: '数据清理' },
  { key: 'feedback', label: '投诉反馈' }
] as const
const currentTab = ref('backup')

/* ================= 数据概览 ================= */
const dataStats = reactive({
  items: { total: 0, thisMonth: 0 },
  users: { total: 0, active: 0 },
  images: { count: 0, size: 0 },
  trash: { count: 0, size: 0 }
})

/* ================= 备份管理 ================= */
const backupConfig = reactive({
  autoEnabled: true,
  cycle: 'weekly',
  time: '02:00',
  retention: 7
})

const backupList = ref<any[]>([])
const backingUp = ref(false)
const backupProgress = reactive({
  show: false,
  percent: 0,
  status: '准备中...',
  currentTable: '',
  processed: 0,
  total: 0
})

/* ================= 导出管理 ================= */
const exportDataTypes = [
  { value: 'items', label: '物品数据', desc: '失物招领物品信息' },
  { value: 'users', label: '用户数据', desc: '注册用户基本信息' },
  { value: 'claims', label: '认领记录', desc: '物品认领申请记录' },
  { value: 'images', label: '图片资源', desc: '所有上传的图片文件' }
]

const exportForm = reactive({
  range: 'all',
  startDate: '',
  endDate: '',
  types: ['items', 'users'],
  format: 'excel',
  includeImages: false
})

const exportHistory = ref<any[]>([])
const exporting = ref(false)
const exportPollingMap = ref<Map<number, ReturnType<typeof setInterval>>>(new Map())

const canExport = computed(() => {
  return exportForm.types.length > 0 && 
         (exportForm.range !== 'custom' || (exportForm.startDate && exportForm.endDate))
})

/* ================= 数据清理 ================= */
const cleanupRules = ref([
  { 
    id: 1, 
    name: '已删除物品', 
    description: '用户已删除或管理员已移除的物品数据',
    enabled: true,
    retentionDays: 30,
    estimatedCount: 156,
    estimatedSize: 1024 * 1024 * 50
  },
  { 
    id: 2, 
    name: '过期日志', 
    description: '系统操作日志和审计日志',
    enabled: true,
    retentionDays: 90,
    estimatedCount: 5000,
    estimatedSize: 1024 * 1024 * 200
  },
  { 
    id: 3, 
    name: '失效备份', 
    description: '超出保留策略的旧备份文件',
    enabled: true,
    retentionDays: 7,
    estimatedCount: 3,
    estimatedSize: 1024 * 1024 * 1024 * 2
  },
  { 
    id: 4, 
    name: '未激活账号', 
    description: '长期未登录且未发布内容的用户',
    enabled: false,
    retentionDays: 365,
    estimatedCount: 23,
    estimatedSize: 1024 * 1024 * 5
  }
])

const cleanupCategories = ref([
  { key: 'temp', name: '临时文件', count: 128, size: 1024 * 1024 * 10 },
  { key: 'cache', name: '缓存数据', count: 56, size: 1024 * 1024 * 25 },
  { key: 'log', name: '错误日志', count: 342, size: 1024 * 1024 * 80 }
])

const orphanFiles = reactive({
  count: 45,
  size: 1024 * 1024 * 120
})

/* ================= 投诉反馈 ================= */
const feedbackStats = ref([
  { value: 12, label: '待处理', change: '+3', trend: 'up' },
  { value: 89, label: '本周处理', change: '+12%', trend: 'up' },
  { value: 4.8, label: '满意度', change: '+0.2', trend: 'up' },
  { value: 2.5, label: '平均响应(小时)', change: '-0.5', trend: 'down' }
])

const feedbackFilter = reactive({
  type: '',
  status: ''
})

const feedbackList = ref<any[]>([])

/* ================= 弹窗状态 ================= */
const showRestoreModal = ref(false)
const showCleanupModal = ref(false)
const showReplyModal = ref(false)
const restoringBackup = ref<any>(null)
const restoreConfirmText = ref('')
const cleanupPreview = ref<any[]>([])
const replyingFeedback = ref<any>(null)
const replyContent = ref('')
const replyAndResolve = ref(true)
const previewImageUrl = ref('')

/* ================= 标签切换 ================= */
const switchTab = (tab: string) => {
  currentTab.value = tab
  if (tab === 'backup') loadBackups()
  if (tab === 'export') loadExportHistory()
  if (tab === 'cleanup') loadCleanupStats()
  if (tab === 'feedback') loadFeedback()
}

/* ================= 数据加载 ================= */
const loadDataStats = async () => {
  try {
    const res = await axios.get('/api/admin/data/stats')
    if (res.data.code === 200) {
      Object.assign(dataStats, res.data.data)
    }
  } catch (error) {
    // 模拟数据
    dataStats.items = { total: 1256, thisMonth: 89 }
    dataStats.users = { total: 3420, active: 2890 }
    dataStats.images = { count: 4532, size: 1024 * 1024 * 1024 * 2.5 }
    dataStats.trash = { count: 234, size: 1024 * 1024 * 180 }
  }
}

const loadBackups = async () => {
  try {
    const res = await axios.get('/api/admin/backups')
    if (res.data.code === 200) {
      backupList.value = res.data.data || []
    }
  } catch (error) {
    backupList.value = [
      { id: 1, name: '自动备份-20260301-020000', type: 'auto', createTime: '2026-03-01 02:00:00', size: 1024 * 1024 * 1024 * 1.2, status: 'completed', tables: ['users', 'items', 'records', 'images'] },
      { id: 2, name: '手动备份-20260228', type: 'manual', createTime: '2026-02-28 15:30:00', size: 1024 * 1024 * 1024 * 1.1, status: 'completed', tables: ['users', 'items', 'records'] },
      { id: 3, name: '自动备份-20260228-020000', type: 'auto', createTime: '2026-02-28 02:00:00', size: 1024 * 1024 * 1024 * 1.15, status: 'completed', tables: ['users', 'items', 'records', 'images'] }
    ]
  }
}

const loadExportHistory = async () => {
  try {
    const res = await axios.get('/api/admin/exports')
    if (res.data.code === 200) {
      exportHistory.value = res.data.data || []
    }
  } catch (error) {
    exportHistory.value = [
      { id: 1, name: '物品数据导出-20260301', createTime: '2026-03-01 10:30:00', recordCount: 1256, size: 1024 * 1024 * 5, status: 'completed', format: 'excel' },
      { id: 2, name: '用户数据导出-20260228', createTime: '2026-02-28 16:00:00', recordCount: 3420, size: 1024 * 1024 * 2, status: 'completed', format: 'csv' }
    ]
  }
}

const loadFeedback = async () => {
  try {
    const res = await axios.get('/api/admin/feedback', {
      params: {
        type: feedbackFilter.type || undefined,
        status: feedbackFilter.status || undefined
      }
    })
    if (res.data.code === 200) {
      feedbackList.value = res.data.data.list || []
    }
  } catch (error) {
    feedbackList.value = [
      {
        id: 1,
        type: 'bug',
        priority: 'high',
        status: 'pending',
        userName: '张三',
        userPhone: '13800138001',
        userAvatar: null,
        title: '无法上传图片',
        content: '发布物品时选择图片后一直显示加载中，无法完成上传...',
        images: [],
        createTime: '2026-03-01 09:15:00'
      },
      {
        id: 2,
        type: 'feature',
        priority: 'normal',
        status: 'pending',
        userName: '李四',
        userPhone: '13800138002',
        userAvatar: null,
        title: '建议增加物品标签功能',
        content: '希望能给物品添加标签，方便分类查找，比如"贵重"、"急需"等...',
        images: [],
        createTime: '2026-02-28 14:20:00'
      }
    ]
  }
}

const loadCleanupStats = async () => {
  try {
    const res = await axios.get('/api/admin/cleanup/stats')
    if (res.data.code === 200) {
      const data = res.data.data
      cleanupRules.value = data.cleanupRules
      cleanupCategories.value = data.cleanupCategories
      orphanFiles.count = data.orphanFiles.count
      orphanFiles.size = data.orphanFiles.size
    }
  } catch (error) {
    // 模拟数据
    cleanupRules.value = [
      { 
        id: 1, 
        name: '已删除物品', 
        description: '用户已删除或管理员已移除的物品数据',
        enabled: true,
        retentionDays: 30,
        estimatedCount: 156,
        estimatedSize: 1024 * 1024 * 50
      },
      { 
        id: 2, 
        name: '过期日志', 
        description: '系统操作日志和审计日志',
        enabled: true,
        retentionDays: 90,
        estimatedCount: 5000,
        estimatedSize: 1024 * 1024 * 200
      },
      { 
        id: 3, 
        name: '失效备份', 
        description: '超出保留策略的旧备份文件',
        enabled: true,
        retentionDays: 7,
        estimatedCount: 3,
        estimatedSize: 1024 * 1024 * 1024 * 2
      },
      { 
        id: 4, 
        name: '未激活账号', 
        description: '长期未登录且未发布内容的用户',
        enabled: false,
        retentionDays: 365,
        estimatedCount: 23,
        estimatedSize: 1024 * 1024 * 5
      }
    ]
    cleanupCategories.value = [
      { key: 'temp', name: '临时文件', count: 128, size: 1024 * 1024 * 10 },
      { key: 'cache', name: '缓存数据', count: 56, size: 1024 * 1024 * 25 },
      { key: 'log', name: '错误日志', count: 342, size: 1024 * 1024 * 80 }
    ]
    orphanFiles.count = 45
    orphanFiles.size = 1024 * 1024 * 120
  }
}

/* ================= 备份操作 ================= */
const saveBackupConfig = async () => {
  try {
    await axios.post('/api/admin/backup-config', backupConfig)
    alert('设置已保存')
  } catch (error) {
    alert('保存失败')
  }
}

const startManualBackup = async () => {
  backingUp.value = true
  backupProgress.show = true
  backupProgress.percent = 0
  backupProgress.status = '准备中...'
  
  try {
    const res = await axios.post('/api/admin/backups/create', { type: 'full' })
    if (res.data.code === 200) {
      // 模拟进度更新
      const tables = ['users', 'items', 'records', 'images', 'logs']
      backupProgress.total = tables.length
      
      for (let i = 0; i < tables.length; i++) {
        backupProgress.currentTable = tables[i]
        backupProgress.processed = i
        backupProgress.status = `正在备份 ${tables[i]}...`
        
        await new Promise(resolve => setTimeout(resolve, 800))
        backupProgress.percent = Math.round(((i + 1) / tables.length) * 100)
      }
      
      backupProgress.status = '备份完成'
      await loadBackups()
      showMessage('备份成功！')
      
      setTimeout(() => {
        backupProgress.show = false
        backingUp.value = false
      }, 1000)
    }
  } catch (error: any) {
    showMessage(error.response?.data?.message || '备份失败', 'error')
    backingUp.value = false
  }
}

const downloadBackup = (backup: any) => {
  window.open(`/api/admin/backups/${backup.id}/download`, '_blank')
}

const restoreBackup = (backup: any) => {
  restoringBackup.value = backup
  restoreConfirmText.value = ''
  showRestoreModal.value = true
}

const closeRestoreModal = () => {
  showRestoreModal.value = false
  restoringBackup.value = null
}

const executeRestore = async () => {
  try {
    await axios.post(`/api/admin/backups/${restoringBackup.value.id}/restore`)
    alert('恢复任务已启动，请稍后刷新页面查看')
    closeRestoreModal()
  } catch (error) {
    alert('恢复失败')
  }
}

const deleteBackup = async (backup: any) => {
  if (!confirm(`确定要删除备份 "${backup.name}" 吗？`)) return
  try {
    await axios.delete(`/api/admin/backups/${backup.id}`)
    await loadBackups()
  } catch (error) {
    alert('删除失败')
  }
}

/* ================= 导出操作 ================= */
const startExport = async () => {
  exporting.value = true
  try {
    const res = await axios.post('/api/admin/exports/create', exportForm)
    if (res.data.code === 200) {
      await loadExportHistory()
      // 开始轮询最新任务的进度
      const latestTask = exportHistory.value[0]
      if (latestTask && latestTask.status === 'processing') {
        startExportPolling(latestTask.id)
      }
      // 重置表单
      exportForm.types = ['items', 'users']
      exportForm.includeImages = false
      showMessage('导出任务已创建！')
    }
  } catch (error: any) {
    showMessage(error.response?.data?.message || '导出失败', 'error')
  } finally {
    exporting.value = false
  }
}

const startExportPolling = (taskId: number) => {
  const pollInterval = setInterval(async () => {
    try {
      const res = await axios.get('/api/admin/exports')
      if (res.data.code === 200) {
        const task = res.data.data.find((t: any) => t.id === taskId)
        if (task) {
          // 更新进度
          const existingTask = exportHistory.value.find((t: any) => t.id === taskId)
          if (existingTask) {
            existingTask.progress = task.progress
            existingTask.status = task.status
            existingTask.recordCount = task.recordCount
            if (task.file_size) {
              existingTask.size = task.file_size
            }
          }
          
          // 完成或失败则停止轮询
          if (task.status === 'completed' || task.status === 'failed') {
            clearInterval(pollInterval)
            exportPollingMap.value.delete(taskId)
            if (task.status === 'completed') {
              showMessage('导出完成！')
            } else {
              showMessage('导出失败', 'error')
            }
          }
        }
      }
    } catch (error) {
      clearInterval(pollInterval)
      exportPollingMap.value.delete(taskId)
    }
  }, 1000)
  
  exportPollingMap.value.set(taskId, pollInterval)
}

const downloadExport = (task: any) => {
  window.open(`/api/admin/exports/${task.id}/download`, '_blank')
}

const retryExport = async (task: any) => {
  try {
    await axios.post(`/api/admin/exports/${task.id}/retry`)
    await loadExportHistory()
    // 重试后开始轮询进度
    startExportPolling(task.id)
  } catch (error) {
    alert('重试失败')
  }
}

const deleteExport = async (task: any) => {
  if (!confirm('确定要删除这条导出记录吗？')) return
  try {
    await axios.delete(`/api/admin/exports/${task.id}`)
    await loadExportHistory()
  } catch (error) {
    alert('删除失败')
  }
}

/* ================= 清理操作 ================= */
const previewCleanup = () => {
  cleanupPreview.value = cleanupRules.value
    .filter(r => r.enabled)
    .map(r => ({
      name: r.name,
      count: r.estimatedCount,
      size: r.estimatedSize
    }))
  showCleanupModal.value = true
}

const closeCleanupModal = () => {
  showCleanupModal.value = false
}

const executeCleanup = async () => {
  try {
    await axios.post('/api/admin/cleanup', {
      rules: cleanupRules.value.filter(r => r.enabled)
    })
    alert('清理任务已启动')
    closeCleanupModal()
    await loadDataStats()
  } catch (error) {
    alert('清理失败')
  }
}

const cleanupCategory = async (cat: any) => {
  if (!confirm(`确定要清理 ${cat.name} 吗？`)) return
  try {
    await axios.post(`/api/admin/cleanup/category`, { category: cat.key })
    alert('清理完成')
    await loadDataStats()
  } catch (error) {
    alert('清理失败')
  }
}

const cleanupOrphanFiles = async () => {
  if (!confirm(`确定要清理 ${orphanFiles.count} 个孤儿文件吗？`)) return
  try {
    await axios.post('/api/admin/cleanup/orphan-files')
    alert('清理完成')
    await loadDataStats()
  } catch (error) {
    alert('清理失败')
  }
}

/* ================= 反馈操作 ================= */
const openReplyModal = (item: any) => {
  replyingFeedback.value = item
  replyContent.value = ''
  replyAndResolve.value = true
  showReplyModal.value = true
}

const closeReplyModal = () => {
  showReplyModal.value = false
  replyingFeedback.value = null
}

const sendReply = async () => {
  try {
    await axios.post(`/api/admin/feedback/${replyingFeedback.value.id}/reply`, {
      content: replyContent.value,
      resolve: replyAndResolve.value
    })
    await loadFeedback()
    closeReplyModal()
  } catch (error) {
    alert('发送失败')
  }
}

const resolveFeedback = async (item: any) => {
  try {
    await axios.post(`/api/admin/feedback/${item.id}/resolve`)
    item.status = 'resolved'
  } catch (error) {
    alert('操作失败')
  }
}

const contactUser = (item: any) => {
  // 打开用户详情或发起会话
  window.open(`tel:${item.userPhone}`)
}

/* ================= 工具函数 ================= */
const formatSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(2)} ${units[i]}`
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

const getBackupStatus = (status: string) => {
  const map: Record<string, string> = {
    completed: '完成',
    processing: '进行中',
    failed: '失败'
  }
  return map[status] || status
}

const getFeedbackType = (type: string) => {
  const map: Record<string, string> = {
    bug: '系统故障',
    feature: '功能建议',
    complaint: '投诉举报',
    other: '其他'
  }
  return map[type] || type
}

const maskPhone = (phone: string) => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const previewImage = (url: string) => {
  previewImageUrl.value = url
}

const closeImagePreview = () => {
  previewImageUrl.value = ''
}

const cleanupPreviewTotal = computed(() => {
  return cleanupPreview.value.reduce((sum, item) => sum + item.size, 0)
})



// 简单的通知函数
const showMessage = (msg: string, type: 'success' | 'error' | 'warning' = 'success') => {
  alert(`${type.toUpperCase()}: ${msg}`)
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadDataStats()
  loadBackups()
  loadCleanupStats()
})

onUnmounted(() => {
  // 清理所有轮询定时器
  exportPollingMap.value.forEach((intervalId) => {
    clearInterval(intervalId)
  })
  exportPollingMap.value.clear()
})
</script>

<style scoped>
/* 基础布局 */
.data-manage-page {
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

/* 数据概览 */
.data-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 25px;
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
}

.overview-card.warning {
  border-color: rgba(255, 152, 0, 0.3);
  background: rgba(255, 152, 0, 0.08);
}

.overview-icon {
  font-size: 40px;
}

.overview-info {
  display: flex;
  flex-direction: column;
}

.overview-value {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 28px;
  color: #a67c52;
  font-weight: 700;
}

.overview-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin: 4px 0;
}

.overview-trend {
  font-size: 12px;
  color: #4caf50;
  font-weight: 500;
}

/* 标签页 */
.data-tabs {
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

/* 备份布局 */
.backup-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 25px;
}

.backup-config-panel,
.backup-history-panel {
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

.config-item {
  margin-bottom: 25px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.toggle-switch.small {
  width: 40px;
  height: 22px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(166, 124, 82, 0.3);
  transition: .4s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.toggle-switch.small .slider:before {
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
}

input:checked + .slider {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.toggle-switch.small input:checked + .slider:before {
  transform: translateX(18px);
}

.label-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
}

.config-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(158, 158, 158, 0.2);
  color: #9e9e9e;
}

.config-status.active {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.config-desc {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin: 0;
}

.config-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  margin-bottom: 10px;
  font-weight: 500;
}

.cycle-options {
  display: flex;
  gap: 10px;
}

.cycle-radio {
  flex: 1;
}

.cycle-radio input {
  display: none;
}

.cycle-radio span {
  display: block;
  padding: 12px;
  text-align: center;
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cycle-radio input:checked + span {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
  color: #f38181;
}

.time-input,
.number-input {
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.5);
  outline: none;
}

.number-input.small {
  width: 70px;
  text-align: center;
}

.config-hint {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin: 8px 0 0 0;
}

.retention-setting {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.save-config-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-config-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.3);
}

/* 备份历史 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.manual-backup-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.manual-backup-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.manual-backup-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.backup-progress {
  background: rgba(243, 129, 129, 0.1);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.progress-bar {
  height: 8px;
  background: rgba(166, 124, 82, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(to right, #f38181, #f77d5f);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-detail {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.backup-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.backup-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.1);
  transition: all 0.3s ease;
}

.backup-item:hover {
  border-color: rgba(243, 129, 129, 0.3);
  transform: translateX(4px);
}

.backup-item.auto-backup {
  border-left: 4px solid #f38181;
}

.backup-icon {
  font-size: 24px;
  width: 40px;
  text-align: center;
}

.backup-info {
  flex: 1;
}

.backup-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 6px;
}

.backup-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 6px;
}

.backup-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.backup-status.completed {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.backup-tables {
  font-size: 11px;
  color: rgba(166, 124, 82, 0.6);
}

.backup-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(166, 124, 82, 0.1);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(166, 124, 82, 0.2);
  transform: scale(1.1);
}

.action-btn.danger:hover {
  background: rgba(244, 67, 54, 0.15);
}

/* 导出布局 */
.export-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 25px;
}

.export-options-panel,
.export-history-panel {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.15);
}

.export-section {
  margin-bottom: 25px;
}

.section-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  margin-bottom: 12px;
  font-weight: 500;
}

.range-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.range-card {
  position: relative;
  padding: 20px 15px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.5);
}

.range-card input {
  display: none;
}

.range-card:hover {
  border-color: rgba(243, 129, 129, 0.4);
}

.range-card.active {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.range-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 10px;
}

.range-name {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 6px;
}

.range-desc {
  display: block;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.custom-range {
  margin-top: 15px;
  padding: 20px;
  background: rgba(166, 124, 82, 0.05);
  border-radius: 12px;
}

.date-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.date-field label {
  display: block;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
  margin-bottom: 8px;
}

.data-types {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.type-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.type-checkbox:hover {
  border-color: rgba(243, 129, 129, 0.3);
}

.type-checkbox input {
  display: none;
}

.custom-checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(166, 124, 82, 0.4);
  border-radius: 6px;
  position: relative;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.type-checkbox input:checked + .custom-checkbox {
  background: linear-gradient(to right, #f38181, #f77d5f);
  border-color: #f38181;
}

.type-checkbox input:checked + .custom-checkbox::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.type-info {
  flex: 1;
}

.type-name {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
}

.type-desc {
  display: block;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.format-options {
  display: flex;
  gap: 12px;
}

.format-radio {
  flex: 1;
  padding: 15px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.format-radio input {
  display: none;
}

.format-radio.active {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.format-icon {
  display: block;
  font-size: 28px;
  margin-bottom: 8px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
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

.export-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.export-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.3);
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 导出历史 */
.export-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.export-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.1);
}

.export-item.exporting {
  border-color: rgba(33, 150, 243, 0.3);
  background: rgba(33, 150, 243, 0.05);
}

.export-item.failed {
  border-color: rgba(244, 67, 54, 0.3);
  background: rgba(244, 67, 54, 0.05);
}

.export-status-icon {
  font-size: 20px;
  width: 30px;
  text-align: center;
}

.export-info {
  flex: 1;
}

.export-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 6px;
}

.export-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 8px;
}

.export-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar.mini {
  flex: 1;
  height: 6px;
  margin: 0;
}

.export-error {
  font-size: 12px;
  color: #f44336;
}

/* 清理布局 */
.cleanup-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 25px;
}

.cleanup-rules-panel,
.manual-cleanup-panel {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.15);
}

.rule-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 25px;
}

.rule-item {
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.1);
}

.rule-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.rule-name {
  flex: 1;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
}

.rule-status {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(158, 158, 158, 0.2);
  color: #9e9e9e;
}

.rule-status.active {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.rule-desc {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin: 0 0 12px 0;
}

.rule-config {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.rule-preview {
  padding: 10px;
  background: rgba(255, 152, 0, 0.1);
  border-radius: 8px;
  font-size: 13px;
  color: #ff9800;
}

.cleanup-actions {
  display: flex;
  gap: 12px;
}

.preview-btn,
.execute-btn {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.preview-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
}

.preview-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.execute-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.execute-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(244, 67, 54, 0.3);
}

.cleanup-categories {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 25px;
}

.category-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
}

.category-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
}

.category-info {
  flex: 1;
}

.category-name {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 4px;
}

.category-count,
.category-size {
  display: inline-block;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin-right: 15px;
}

.cleanup-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cleanup-btn:hover {
  background: rgba(244, 67, 54, 0.2);
}

.cleanup-btn.large {
  width: 100%;
  padding: 16px;
  font-size: 15px;
  margin-top: 15px;
}

.orphan-files {
  padding: 20px;
  background: rgba(255, 152, 0, 0.08);
  border-radius: 12px;
  border: 2px dashed rgba(255, 152, 0, 0.3);
}

.orphan-files h4 {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin: 0 0 10px 0;
}

.orphan-desc {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin: 0 0 15px 0;
}

.orphan-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #ff9800;
}

/* 反馈布局 */
.feedback-layout {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.feedback-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 25px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  border: 2px solid rgba(166, 124, 82, 0.15);
}

.stat-value {
  display: block;
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 32px;
  color: #a67c52;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
  margin-bottom: 8px;
}

.stat-change {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.stat-change.up {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.stat-change.down {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.feedback-list-panel {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.15);
}

.filter-group {
  display: flex;
  gap: 12px;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.feedback-item {
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.1);
  transition: all 0.3s ease;
}

.feedback-item:hover {
  border-color: rgba(243, 129, 129, 0.3);
  transform: translateX(4px);
}

.feedback-item.urgent {
  border-color: rgba(244, 67, 54, 0.4);
  background: rgba(244, 67, 54, 0.05);
}

.feedback-item.resolved {
  opacity: 0.7;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.feedback-type {
  display: flex;
  gap: 10px;
}

.type-tag {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.type-tag.type-bug { background: rgba(244, 67, 54, 0.15); color: #f44336; }
.type-tag.type-feature { background: rgba(33, 150, 243, 0.15); color: #2196f3; }
.type-tag.type-complaint { background: rgba(156, 39, 176, 0.15); color: #9c27b0; }
.type-tag.type-other { background: rgba(158, 158, 158, 0.15); color: #757575; }

.priority-tag {
  padding: 4px 10px;
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.feedback-time {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.6);
}

.feedback-user {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.user-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
}

.user-contact {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

.feedback-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 16px;
  color: #a67c52;
  margin: 0 0 10px 0;
}

.feedback-content {
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
  line-height: 1.6;
  margin: 0 0 15px 0;
}

.feedback-images {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.feedback-images img {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feedback-images img:hover {
  transform: scale(1.1);
}

.feedback-reply {
  padding: 15px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 12px;
  margin-bottom: 15px;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #4caf50;
  font-weight: 600;
}

.feedback-reply p {
  margin: 0;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
}

.feedback-actions {
  display: flex;
  gap: 12px;
}

.feedback-actions .action-btn {
  width: auto;
  padding: 10px 20px;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
}

.action-btn.reply {
  background: rgba(33, 150, 243, 0.15);
  color: #2196f3;
}

.action-btn.resolve {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.action-btn.contact {
  background: rgba(156, 39, 176, 0.15);
  color: #9c27b0;
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

.confirm-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.confirm-modal.large {
  max-width: 500px;
}

/* ================= 弹窗样式 ================= */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 2px solid rgba(166, 124, 82, 0.15);
}

.modal-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 20px;
  color: #a67c52;
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(166, 124, 82, 0.2);
  transform: rotate(90deg);
}

.modal-body {
  padding: 25px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 25px;
  border-top: 2px solid rgba(166, 124, 82, 0.15);
}

.modal-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-btn.cancel-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
}

.modal-btn.cancel-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.modal-btn.confirm-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.modal-btn.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.3);
}

.modal-btn.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-btn.danger-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.modal-btn.danger-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(244, 67, 54, 0.3);
}

.modal-btn.danger-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 警告框样式 */
.warning-box {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 152, 0, 0.1);
  border-radius: 12px;
  border: 2px solid rgba(255, 152, 0, 0.3);
  margin-bottom: 20px;
}

.warning-icon {
  font-size: 32px;
}

.warning-content h4 {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #ff9800;
  margin: 0 0 8px 0;
}

.warning-content p {
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
  margin: 0;
}

/* 恢复信息 */
.restore-info {
  background: rgba(166, 124, 82, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  border-bottom: 1px dashed rgba(166, 124, 82, 0.2);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row strong {
  color: #f38181;
}

/* 确认输入 */
.confirm-input {
  margin-top: 15px;
}

.confirm-input label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  margin-bottom: 8px;
}

/* 清理预览 */
.cleanup-preview {
  background: rgba(255, 152, 0, 0.05);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.cleanup-preview h4 {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin: 0 0 15px 0;
}

.cleanup-list {
  list-style: none;
  padding: 0;
  margin: 0 0 15px 0;
}

.cleanup-list li {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
}

.cleanup-list li strong {
  color: #f38181;
}

.cleanup-total {
  display: flex;
  justify-content: space-between;
  padding-top: 15px;
  border-top: 2px solid rgba(166, 124, 82, 0.2);
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
}

.cleanup-total strong {
  color: #f44336;
  font-size: 18px;
}

.cleanup-warning {
  font-size: 14px;
  color: #f44336;
  text-align: center;
  margin: 0;
  padding: 10px;
  background: rgba(244, 67, 54, 0.05);
  border-radius: 8px;
}

/* 回复弹窗 */
.reply-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.reply-to {
  padding: 10px 15px;
  background: rgba(166, 124, 82, 0.05);
  border-radius: 8px;
  margin-bottom: 15px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.original-content {
  padding: 15px;
  background: rgba(243, 129, 129, 0.05);
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid #f38181;
}

.original-content strong {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  margin-bottom: 8px;
}

.original-content p {
  margin: 0;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
  line-height: 1.6;
}

/* 表单元素 */
.form-input {
  width: 80%;
  padding: 12px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.8);
  outline: none;
  transition: all 0.3s ease;
}

.form-input:focus {
  border-color: #f38181;
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.2);
}

.form-textarea {
  width: 100%;
  padding: 12px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.8);
  outline: none;
  resize: vertical;
  transition: all 0.3s ease;
}

.form-textarea:focus {
  border-color: #f38181;
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.2);
}

/* 筛选下拉框 */
.filter-select {
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.8);
  outline: none;
  cursor: pointer;
  min-width: 140px;
}

.filter-select:focus {
  border-color: #f38181;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 16px;
}

.empty-state.large {
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.5);
  margin: 0;
}

.empty-state.large h3 {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: rgba(166, 124, 82, 0.4);
  margin: 0 0 10px 0;
}

/* 加载旋转动画 */
.loading-spinner-small {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 图片预览 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 20px;
}

.preview-large {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.preview-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.preview-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 备份状态补全 */
.backup-status.failed {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

/* 确保一些全局样式一致 */
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

/* 小工具 */
.number-input {
  width: 80px;
}

.time-input {
  width: 120px;
}

/* 确保所有输入框在深色背景下可见 */
input, select, textarea {
  background: rgba(255, 255, 255, 0.9);
}

/* 调整滚动条样式（可选） */
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(166, 124, 82, 0.1);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: rgba(166, 124, 82, 0.3);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(166, 124, 82, 0.5);
}
</style>
