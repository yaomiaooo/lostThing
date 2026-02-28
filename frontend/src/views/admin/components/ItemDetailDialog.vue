<template>
  <teleport to="body">
    <transition name="mask-fade">
      <div v-if="visible" class="item-detail-dialog-mask" @click.self="handleClose">
        <transition name="dialog-pop">
          <div class="item-detail-dialog">
            <!-- 弹窗头部 -->
            <div class="dialog-header">
              <h3 class="dialog-title">物品详情</h3>
              <button class="close-btn" @click="handleClose" aria-label="关闭">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>

            <!-- 弹窗内容 -->
            <div class="dialog-content">
              <!-- 物品图片 -->
              <div class="item-images-section">
                <h4 class="section-title">物品图片</h4>
                <div class="images-container">
                  <div v-if="item.firstImageUrl" class="image-preview">
                    <img 
                      :src="item.firstImageUrl" 
                      :alt="item.name"
                      class="item-image"
                      @error="handleImageError"
                    >
                  </div>
                  <div v-else class="no-images">
                    <span class="no-image-icon">📷</span>
                    <span class="no-image-text">暂无图片</span>
                  </div>
                </div>
              </div>

              <!-- 基本信息 -->
              <div class="basic-info-section">
                <h4 class="section-title">基本信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">物品名称：</span>
                    <span class="info-value">{{ item.name }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">物品类型：</span>
                    <span class="info-value">{{ item.itemCategory === 1 ? '失物' : '招领' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">物品分类：</span>
                    <span class="info-value">{{ item.itemTypeName || '未知' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">当前状态：</span>
                    <span class="info-value status-badge" :class="getStatusClass(item.currentStatus)">
                      {{ getStatusText(item.currentStatus) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 地点信息 -->
              <div class="location-info-section">
                <h4 class="section-title">地点信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">发现地点：</span>
                    <span class="info-value">{{ item.locationName }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">详细位置：</span>
                    <span class="info-value">{{ item.locationDetail || '未填写' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">领取地点：</span>
                    <span class="info-value">{{ item.pickupLocation || '未填写' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">发现时间：</span>
                    <span class="info-value">{{ formatTime(item.happenTime) }}</span>
                  </div>
                </div>
              </div>

              <!-- 特征描述 -->
              <div class="feature-info-section">
                <h4 class="section-title">特征描述</h4>
                <div class="feature-content">
                  {{ item.feature || '未填写特征描述' }}
                </div>
              </div>

              <!-- 悬赏信息 -->
              <div v-if="item.rewardAmount > 0" class="reward-info-section">
                <h4 class="section-title">悬赏信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">悬赏金额：</span>
                    <span class="info-value reward-amount">￥{{ item.rewardAmount.toFixed(2) }}</span>
                  </div>
                  <div class="info-item full-width">
                    <span class="info-label">悬赏说明：</span>
                    <span class="info-value">{{ item.rewardDesc || '未填写说明' }}</span>
                  </div>
                </div>
              </div>

              <!-- 联系信息 -->
              <div class="contact-info-section">
                <h4 class="section-title">联系信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">联系人：</span>
                    <span class="info-value">{{ item.contactName }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">联系电话：</span>
                    <span class="info-value">{{ item.contactPhone }}</span>
                  </div>
                </div>
              </div>

              <!-- 审核信息 -->
              <div v-if="item.auditTime" class="audit-info-section">
                <h4 class="section-title">审核信息</h4>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">审核时间：</span>
                    <span class="info-value">{{ formatTime(item.auditTime) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">审核人：</span>
                    <span class="info-value">{{ item.auditUserId || '系统' }}</span>
                  </div>
                  <div v-if="item.rejectReason" class="info-item full-width">
                    <span class="info-label">驳回原因：</span>
                    <span class="info-value reject-reason">{{ item.rejectReason }}</span>
                  </div>
                </div>
              </div>

              <!-- 归档信息 -->
              <div v-if="item.archiveDesc" class="archive-info-section">
                <h4 class="section-title">归档信息</h4>
                <div class="info-grid">
                  <div class="info-item full-width">
                    <span class="info-label">归档说明：</span>
                    <span class="info-value">{{ item.archiveDesc }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 弹窗底部 -->
            <div class="dialog-footer">
              <button class="dialog-btn primary" @click="handleClose">关闭</button>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { watch } from 'vue'

interface Props {
  item: any
  visible: boolean
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 获取状态文本
const getStatusText = (status: number) => {
  const statusMap: Record<number, string> = {
    1: '待审核',
    2: '已通过',
    3: '已匹配',
    4: '已认领',
    5: '已驳回',
    6: '已归档',
    7: '已无效'
  }
  return statusMap[status] || '未知状态'
}

// 获取状态样式类
const getStatusClass = (status: number) => {
  const classMap: Record<number, string> = {
    1: 'status-pending',
    2: 'status-approved',
    3: 'status-matched',
    4: 'status-claimed',
    5: 'status-rejected',
    6: 'status-archived',
    7: 'status-invalid'
  }
  return classMap[status] || ''
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 图片加载失败处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  img.parentElement?.querySelector('.no-images')?.classList.remove('hidden')
}

// 处理关闭
const handleClose = () => {
  emit('close')
}

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    // 可以在这里加载更详细的物品信息
    console.log('加载物品详情:', props.item)
  }
})
</script>

<style scoped>
.item-detail-dialog-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.item-detail-dialog {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  color: #666;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.dialog-content {
  padding: 24px;
  max-height: calc(90vh - 140px);
  overflow-y: auto;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #f0f0f0;
}

.item-images-section {
  margin-bottom: 24px;
}

.images-container {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.image-preview {
  width: 200px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-images {
  width: 200px;
  height: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
  color: #999;
}

.no-image-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.no-image-text {
  font-size: 14px;
}

.basic-info-section,
.location-info-section,
.feature-info-section,
.reward-info-section,
.contact-info-section,
.audit-info-section,
.archive-info-section {
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-pending { background: #fffaf0; color: #dd6b20; }
.status-badge.status-approved { background: #f0fff4; color: #38a169; }
.status-badge.status-matched { background: #ebf8ff; color: #3182ce; }
.status-badge.status-claimed { background: #f0fff4; color: #38a169; }
.status-badge.status-rejected { background: #fff5f5; color: #e53e3e; }
.status-badge.status-archived { background: #fffaf0; color: #dd6b20; }
.status-badge.status-invalid { background: #f7fafc; color: #718096; }

.feature-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  line-height: 1.6;
  color: #333;
}

.reward-amount {
  color: #e53e3e;
  font-weight: 600;
  font-size: 16px;
}

.reject-reason {
  color: #e53e3e;
  background: #fff5f5;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid #e53e3e;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
}

.dialog-btn {
  padding: 10px 24px;
  border: 1px solid #007bff;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dialog-btn.primary {
  background: #007bff;
  color: white;
}

.dialog-btn.primary:hover {
  background: #0056b3;
  border-color: #0056b3;
}

/* 动画效果 */
.mask-fade-enter-active,
.mask-fade-leave-active {
  transition: opacity 0.3s ease;
}

.mask-fade-enter-from,
.mask-fade-leave-to {
  opacity: 0;
}

.dialog-pop-enter-active,
.dialog-pop-leave-active {
  transition: all 0.3s ease;
}

.dialog-pop-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

.dialog-pop-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .item-detail-dialog-mask {
    padding: 16px;
  }
  
  .item-detail-dialog {
    max-width: 100%;
    max-height: 95vh;
  }
  
  .dialog-header,
  .dialog-content,
  .dialog-footer {
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .images-container {
    justify-content: center;
  }
  
  .image-preview,
  .no-images {
    width: 100%;
    max-width: 300px;
  }
}
</style>