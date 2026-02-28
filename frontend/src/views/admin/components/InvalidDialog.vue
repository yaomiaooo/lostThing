<template>
  <teleport to="body">
    <transition name="mask-fade">
      <div v-if="visible" class="invalid-dialog-mask" @click.self="handleCancel">
        <transition name="dialog-pop">
          <div class="invalid-dialog">
            <!-- 弹窗头部 -->
            <div class="dialog-header">
              <h3 class="dialog-title">
                {{ batchMode ? '批量标记无效' : '标记物品无效' }}
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
              <div v-if="!batchMode" class="item-info-section">
                <h4 class="section-title">物品信息</h4>
                <div class="item-details">
                  <div class="detail-row">
                    <span class="detail-label">物品名称：</span>
                    <span class="detail-value">{{ item.name }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">当前状态：</span>
                    <span class="detail-value">{{ getStatusText(item.currentStatus) }}</span>
                  </div>
                </div>
              </div>
              
              <div v-else class="batch-info">
                <div class="batch-count">
                  <span class="count-icon">❌</span>
                  <span>共 {{ selectedItems.length }} 个物品将被标记为无效</span>
                </div>
              </div>

              <!-- 标记无效原因 -->
              <div class="invalid-reason-section">
                <h4 class="section-title">标记无效原因</h4>
                <div class="input-group">
                  <label for="invalidReason" class="input-label">请填写标记无效的原因：</label>
                  <textarea
                    id="invalidReason"
                    v-model="invalidReason"
                    class="reason-textarea"
                    placeholder="例如：信息虚假、重复发布、联系方式无效等..."
                    rows="4"
                    maxlength="200"
                  ></textarea>
                  <div class="char-counter">{{ invalidReason.length }}/200</div>
                </div>
              </div>

              <!-- 标记无效提示 -->
              <div class="invalid-tips">
                <div class="tip-item">
                  <span class="tip-icon">💡</span>
                  <span>标记无效后，物品将不再显示在列表中</span>
                </div>
                <div class="tip-item">
                  <span class="tip-icon">⚠️</span>
                  <span>请确保标记无效操作准确无误</span>
                </div>
              </div>
            </div>

            <!-- 弹窗底部 -->
            <div class="dialog-footer">
              <button class="dialog-btn secondary" @click="handleCancel">取消</button>
              <button 
                class="dialog-btn primary" 
                :disabled="!invalidReason.trim()"
                @click="handleConfirm"
              >
                {{ loading ? '提交中...' : '确认标记无效' }}
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
  item?: any
  batchMode?: boolean
  selectedItems?: number[]
  visible: boolean
}

interface Emits {
  (e: 'confirm', data: { itemId?: number; invalidReason: string }): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  batchMode: false,
  selectedItems: () => []
})
const emit = defineEmits<Emits>()

const invalidReason = ref('')
const loading = ref(false)

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

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    invalidReason.value = ''
    loading.value = false
  }
})

// 处理确认
const handleConfirm = async () => {
  if (!invalidReason.value.trim()) {
    return
  }

  loading.value = true
  
  const invalidData = {
    itemId: props.batchMode ? undefined : props.item?.id,
    invalidReason: invalidReason.value.trim()
  }

  emit('confirm', invalidData)
  loading.value = false
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.invalid-dialog-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.invalid-dialog {
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
  margin-bottom: 20px;
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

.batch-info {
  margin-bottom: 20px;
}

.batch-count {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fff5f5;
  border: 1px solid #fc8181;
  border-radius: 6px;
  color: #e53e3e;
}

.count-icon {
  font-size: 18px;
}

.invalid-reason-section {
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

.invalid-tips {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 6px;
  padding: 12px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #c53030;
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
  background: #e53e3e;
  border-color: #e53e3e;
  color: white;
}

.dialog-btn.primary:hover:not(:disabled) {
  background: #c53030;
  border-color: #c53030;
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
  .invalid-dialog-mask {
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