<template>
  <teleport to="body">
    <transition name="mask-fade">
      <div v-if="visible" class="audit-dialog-mask" @click.self="handleCancel">
        <transition name="dialog-pop">
          <div class="audit-dialog">
            <!-- 弹窗头部 -->
            <div class="dialog-header">
              <h3 class="dialog-title">
                {{ auditType === 'approve' ? '审核通过' : '审核驳回' }}
              </h3>
              <button class="close-btn" @click="handleCancel" aria-label="关闭">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>

            <!-- 弹窗内容 -->
            <div class="dialog-content">
              <!-- 物品信息 -->
              <div class="item-info-section">
                <h4 class="section-title">物品信息</h4>
                <div class="item-details">
                  <div class="detail-row">
                    <span class="detail-label">物品名称：</span>
                    <span class="detail-value">{{ item.name }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">物品类型：</span>
                    <span class="detail-value">{{ item.itemCategory === 1 ? '失物' : '招领' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">发现地点：</span>
                    <span class="detail-value">{{ item.locationName }} {{ item.locationDetail || '' }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">特征描述：</span>
                    <span class="detail-value">{{ item.feature }}</span>
                  </div>
                </div>
              </div>

              <!-- 驳回原因输入框 -->
              <div v-if="auditType === 'reject'" class="reject-reason-section">
                <h4 class="section-title">驳回原因</h4>
                <div class="input-group">
                  <label for="rejectReason" class="input-label">请填写驳回原因：</label>
                  <textarea
                    id="rejectReason"
                    v-model="rejectReason"
                    class="reason-textarea"
                    placeholder="请输入驳回的具体原因，如信息不完整、照片不清晰等..."
                    rows="4"
                    maxlength="200"
                  ></textarea>
                  <div class="char-counter">{{ rejectReason.length }}/200</div>
                </div>
              </div>

              <!-- 审核提示 -->
              <div class="audit-tips">
                <div class="tip-item">
                  <span class="tip-icon">💡</span>
                  <span>请仔细核对物品信息，确保审核准确无误</span>
                </div>
                <div v-if="auditType === 'reject'" class="tip-item">
                  <span class="tip-icon">⚠️</span>
                  <span>驳回时必须填写具体原因，以便用户了解问题所在</span>
                </div>
              </div>
            </div>

            <!-- 弹窗底部 -->
            <div class="dialog-footer">
              <button class="dialog-btn secondary" @click="handleCancel">取消</button>
              <button 
                class="dialog-btn primary" 
                :disabled="auditType === 'reject' && !rejectReason.trim()"
                @click="handleConfirm"
              >
                {{ loading ? '提交中...' : '确认' }}
              </button>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  item: any
  auditType: 'approve' | 'reject'
  visible: boolean
}

interface Emits {
  (e: 'confirm', data: { itemId: number; status: number; rejectReason?: string }): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const rejectReason = ref('')
const loading = ref(false)

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    rejectReason.value = ''
    loading.value = false
  }
})

// 处理确认
const handleConfirm = async () => {
  if (props.auditType === 'reject' && !rejectReason.value.trim()) {
    return
  }

  loading.value = true
  
  const auditData = {
    itemId: props.item.id,
    status: props.auditType === 'approve' ? 2 : 5,
    rejectReason: props.auditType === 'reject' ? rejectReason.value.trim() : ''
  }

  emit('confirm', auditData)
  loading.value = false
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.audit-dialog-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.audit-dialog {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
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

.item-info-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.item-details {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.detail-row {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  color: #666;
  min-width: 80px;
}

.detail-value {
  color: #333;
  flex: 1;
}

.reject-reason-section {
  margin-bottom: 20px;
}

.input-group {
  margin-bottom: 12px;
}

.input-label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.reason-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  background: #fafafa;
  transition: all 0.3s ease;
}

.reason-textarea:focus {
  outline: none;
  border-color: #007bff;
  background: #fff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.char-counter {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.audit-tips {
  background: #f0f9ff;
  border: 1px solid #b3e0ff;
  border-radius: 6px;
  padding: 12px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #0066cc;
  margin-bottom: 8px;
}

.tip-item:last-child {
  margin-bottom: 0;
}

.tip-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
}

.dialog-btn {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.dialog-btn.secondary {
  background: #fff;
  border-color: #ddd;
  color: #666;
}

.dialog-btn.secondary:hover {
  background: #f8f9fa;
  border-color: #ccc;
}

.dialog-btn.primary {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

.dialog-btn.primary:hover:not(:disabled) {
  background: #0056b3;
  border-color: #0056b3;
}

.dialog-btn.primary:disabled {
  background: #ccc;
  border-color: #ccc;
  cursor: not-allowed;
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
@media (max-width: 480px) {
  .audit-dialog-mask {
    padding: 16px;
  }
  
  .dialog-header,
  .dialog-content,
  .dialog-footer {
    padding: 16px;
  }
  
  .dialog-title {
    font-size: 16px;
  }
}
</style>