<template>
  <teleport to="body">
    <transition name="mask-fade">
      <div v-if="visible" class="archive-dialog-mask" @click.self="handleCancel">
        <transition name="dialog-pop">
          <div class="archive-dialog">
            <!-- 弹窗头部 -->
            <div class="dialog-header">
              <h3 class="dialog-title">
                {{ batchMode ? '批量归档物品' : '归档物品' }}
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
                    <span class="detail-label">发布时长：</span>
                    <span class="detail-value">{{ item.daysSinceCreate }} 天</span>
                  </div>
                </div>
              </div>
              
              <div v-else class="batch-info">
                <div class="batch-count">
                  <span class="count-icon">📁</span>
                  <span>共 {{ selectedItems.length }} 个物品将被归档</span>
                </div>
              </div>

              <!-- 归档类型 -->
              <div class="archive-type-section">
                <h4 class="section-title">归档类型</h4>
                <div class="type-options">
                  <label 
                    v-for="type in archiveTypes" 
                    :key="type.value"
                    class="type-option"
                  >
                    <input 
                      type="radio" 
                      v-model="archiveType" 
                      :value="type.value"
                      class="type-radio"
                    >
                    <span class="type-label">{{ type.label }}</span>
                  </label>
                </div>
              </div>

              <!-- 归档描述 -->
              <div class="archive-desc-section">
                <h4 class="section-title">归档描述</h4>
                <div class="input-group">
                  <label for="archiveDesc" class="input-label">归档说明：</label>
                  <textarea
                    id="archiveDesc"
                    v-model="archiveDesc"
                    class="desc-textarea"
                    placeholder="请填写归档的具体原因和处理方式..."
                    rows="4"
                    maxlength="200"
                  ></textarea>
                  <div class="char-counter">{{ archiveDesc.length }}/200</div>
                </div>
              </div>

              <!-- 归档提示 -->
              <div class="archive-tips">
                <div class="tip-item">
                  <span class="tip-icon">💡</span>
                  <span>归档后物品将不再显示在常规列表中</span>
                </div>
                <div class="tip-item">
                  <span class="tip-icon">⚠️</span>
                  <span>请确保归档操作准确无误</span>
                </div>
              </div>
            </div>

            <!-- 弹窗底部 -->
            <div class="dialog-footer">
              <button class="dialog-btn secondary" @click="handleCancel">取消</button>
              <button 
                class="dialog-btn primary" 
                :disabled="!archiveDesc.trim()"
                @click="handleConfirm"
              >
                {{ loading ? '提交中...' : '确认归档' }}
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
  (e: 'confirm', data: { itemId?: number; archiveDesc: string; archiveType: string }): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  batchMode: false,
  selectedItems: () => []
})
const emit = defineEmits<Emits>()

const archiveType = ref('移交保卫处')
const archiveDesc = ref('')
const loading = ref(false)

const archiveTypes = [
  { value: '移交保卫处', label: '移交保卫处保管' },
  { value: '移交失物招领中心', label: '移交失物招领中心' },
  { value: '其他处理方式', label: '其他处理方式' }
]

// 监听可见性变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    archiveDesc.value = ''
    archiveType.value = '移交保卫处'
    loading.value = false
  }
})

// 处理确认
const handleConfirm = async () => {
  if (!archiveDesc.value.trim()) {
    return
  }

  loading.value = true
  
  const archiveData = {
    itemId: props.batchMode ? undefined : props.item?.id,
    archiveDesc: archiveDesc.value.trim(),
    archiveType: archiveType.value
  }

  emit('confirm', archiveData)
  loading.value = false
}

// 处理取消
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.archive-dialog-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.archive-dialog {
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
  background: #fffaf0;
  border: 1px solid #f6ad55;
  border-radius: 6px;
  color: #dd6b20;
}

.count-icon {
  font-size: 18px;
}

.archive-type-section {
  margin-bottom: 20px;
}

.type-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-option:hover {
  border-color: #007bff;
}

.type-radio {
  margin: 0;
}

.type-label {
  font-size: 14px;
  color: #333;
}

.archive-desc-section {
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

.desc-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  background: #fafafa;
  transition: all 0.3s ease;
}

.desc-textarea:focus {
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

.archive-tips {
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
  background: #dd6b20;
  border-color: #dd6b20;
  color: white;
}

.dialog-btn.primary:hover:not(:disabled) {
  background: #c05621;
  border-color: #c05621;
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
  .archive-dialog-mask {
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