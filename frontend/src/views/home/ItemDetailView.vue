<template>
  <!-- 详情卡片遮罩层 -->
  <transition name="modal-fade">
    <div 
      v-if="visible" 
      class="item-detail-modal"
      @click.self="handleClose"
    >
      <!-- 详情卡片 -->
      <transition name="card-slide">
        <div 
          v-if="showContent" 
          class="detail-card"
          :class="{ loading: isLoading }"
        >
          <!-- 加载状态 -->
          <div v-if="isLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p class="loading-text">加载中...</p>
          </div>

          <!-- 内容区域 -->
          <div v-else class="card-content">
            <!-- 头部：关闭按钮和标题 -->
            <div class="card-header">
              <div class="card-title">
                <span class="item-type-tag" :class="itemDetail.itemCategory === 1 ? 'lost-tag' : 'found-tag'">
                  {{ itemDetail.itemCategory === 1 ? '失物' : '招领' }}
                </span>
                <h2 class="item-name">{{ itemDetail.name }}</h2>
              </div>
              <button class="close-btn" @click="handleClose">
                <span class="close-icon">×</span>
              </button>
            </div>

            <!-- 图片区域 -->
            <div v-if="itemImages.length > 0" class="image-section">
              <div class="image-gallery">
                <div 
                  v-for="(image, index) in itemImages" 
                  :key="index"
                  class="image-item"
                  @click="showImagePreview(index)"
                >
                  <img :src="image.url" :alt="'物品图片' + (index + 1)" class="gallery-image" />
                  <div class="image-overlay">
                    <span class="image-index">{{ index + 1 }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 物品信息 -->
            <div class="info-section">
              <div class="info-grid">
                <!-- 基础信息 -->
                <div class="info-group">
                  <h3 class="info-title">基本信息</h3>
                  <div class="info-list">
                    <div class="info-item">
                      <span class="info-label">物品类型：</span>
                      <span class="info-value">{{ getCategoryName(itemDetail.itemType) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">地点：</span>
                      <span class="info-value">{{ itemDetail.locationName || '未知地点' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">{{ itemDetail.itemCategory === 1 ? '丢失时间' : '发现时间' }}：</span>
                      <span class="info-value">{{ formatTime(itemDetail.happenTime) }}</span>
                    </div>
                    <div v-if="itemDetail.itemCategory === 1 && itemDetail.rewardAmount > 0" class="info-item">
                      <span class="info-label">悬赏金额：</span>
                      <span class="info-value reward-amount">¥{{ itemDetail.rewardAmount }}</span>
                    </div>
                    <div v-if="itemDetail.pickupLocation" class="info-item">
                      <span class="info-label">领取地点：</span>
                      <span class="info-value">{{ itemDetail.pickupLocation }}</span>
                    </div>
                  </div>
                </div>

                <!-- 特征描述 -->
                <div class="info-group">
                  <h3 class="info-title">特征描述</h3>
                  <div class="feature-content">
                    <p class="feature-text">{{ itemDetail.feature }}</p>
                  </div>
                </div>

                <!-- 悬赏说明 -->
                <div v-if="itemDetail.rewardDesc" class="info-group">
                  <h3 class="info-title">悬赏说明</h3>
                  <div class="reward-desc">
                    <p>{{ itemDetail.rewardDesc }}</p>
                  </div>
                </div>

                <!-- 联系人信息 -->
                <div class="info-group">
                  <h3 class="info-title">联系人信息</h3>
                  <div class="contact-info">
                    <div class="contact-item">
                      <span class="contact-label">姓名：</span>
                      <span class="contact-value">{{ itemDetail.contactName }}</span>
                    </div>
                    <div class="contact-item">
                      <span class="contact-label">电话：</span>
                      <span class="contact-value">{{ itemDetail.contactPhone }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-section">
              <button 
                v-if="itemDetail.itemCategory === 2" 
                class="action-btn claim-btn"
                @click="handleClaim"
              >
                认领物品
              </button>
              <button 
                v-else-if="itemDetail.itemCategory === 1" 
                class="action-btn contact-btn"
                @click="handleContact"
              >
                联系发布者
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- 图片预览模态框 -->
      <transition name="image-preview">
        <div v-if="showImagePreviewModal" class="image-preview-modal" @click.self="hideImagePreview">
          <div class="preview-container">
            <button class="preview-close-btn" @click="hideImagePreview">×</button>
            <img :src="currentPreviewImage" class="preview-image" />
            <div class="preview-nav">
              <button 
                class="nav-btn prev-btn" 
                :disabled="currentImageIndex === 0"
                @click="prevImage"
              >
                ‹
              </button>
              <span class="preview-counter">{{ currentImageIndex + 1 }} / {{ itemImages.length }}</span>
              <button 
                class="nav-btn next-btn" 
                :disabled="currentImageIndex === itemImages.length - 1"
                @click="nextImage"
              >
                ›
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import axios from 'axios'

// Props
interface Props {
  visible: boolean
  itemId?: number
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  itemId: undefined
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'close': []
  'claim': [itemId: number]
  'contact': [item: any]
}>()

// 响应式数据
const itemDetail = ref<any>({})
const itemImages = ref<any[]>([])
const isLoading = ref(false)
const showContent = ref(false)
const showImagePreviewModal = ref(false)
const currentImageIndex = ref(0)

// 计算属性
const currentPreviewImage = computed(() => {
  return itemImages.value[currentImageIndex.value]?.url || ''
})

// 监听visible变化
watch(() => props.visible, async (newVal) => {
  if (newVal) {
    showContent.value = false
    await nextTick()
    await loadItemDetail()
    showContent.value = true
  } else {
    showContent.value = false
  }
})

// 监听itemId变化
watch(() => props.itemId, (newVal) => {
  if (newVal && props.visible) {
    loadItemDetail()
  }
})

// 加载物品详情
async function loadItemDetail() {
  if (!props.itemId) return

  isLoading.value = true
  try {
    const response = await axios.get(`/api/item/detail?itemId=${props.itemId}`)
    if (response.data.code === 200) {
      itemDetail.value = response.data.data
      await loadItemImages()
    }
  } catch (error) {
    console.error('加载物品详情失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 加载物品图片
async function loadItemImages() {
  if (!props.itemId) return

  try {
    const response = await axios.get(`/api/item/image/${props.itemId}`)
    if (response.data && Array.isArray(response.data)) {
      itemImages.value = response.data.map((img: any, index: number) => ({
        ...img,
        url: `data:image/jpeg;base64,${img.imageData}` // 假设返回的是base64数据
      }))
    }
  } catch (error) {
    console.error('加载物品图片失败:', error)
    // 使用默认图片
    itemImages.value = [
      { url: '/home/avatar.png', id: 1 }
    ]
  }
}

// 关闭处理
function handleClose() {
  emit('update:visible', false)
  emit('close')
}

// 图片预览
function showImagePreview(index: number) {
  currentImageIndex.value = index
  showImagePreviewModal.value = true
}

function hideImagePreview() {
  showImagePreviewModal.value = false
}

function prevImage() {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  }
}

function nextImage() {
  if (currentImageIndex.value < itemImages.value.length - 1) {
    currentImageIndex.value++
  }
}

// 认领物品
function handleClaim() {
  emit('claim', props.itemId!)
  handleClose()
}

// 联系发布者
function handleContact() {
  emit('contact', itemDetail.value)
  handleClose()
}

// 工具函数
function formatTime(timeStr: string) {
  if (!timeStr) return '未知时间'
  return timeStr.replace('T', ' ').substring(0, 16)
}

function getCategoryName(categoryId: number) {
  const categories = {
    1: '证件',
    2: '电子设备',
    3: '文具',
    4: '衣物',
    5: '书籍',
    6: '其他'
  }
  return categories[categoryId as keyof typeof categories] || '未知类型'
}
</script>

<style scoped>
/* 模态框动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.card-slide-enter-active,
.card-slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.card-slide-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.card-slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.image-preview-enter-active,
.image-preview-leave-active {
  transition: opacity 0.3s ease;
}

.image-preview-enter-from,
.image-preview-leave-to {
  opacity: 0;
}

/* 模态框遮罩 */
.item-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

/* 详情卡片 */
.detail-card {
  background: white;
  border-radius: 16px;
  width: 90vw;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #999;
}

/* 卡片内容 */
.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 24px 0;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 20px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-type-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.lost-tag {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.found-tag {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.item-name {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.4;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s ease;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #666;
}

/* 图片区域 */
.image-section {
  padding: 0 24px;
  margin-top: 20px;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 6px;
  max-width: 400px;
  margin: 0 auto;
}

.image-item {
  position: relative;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
  transition: transform 0.2s ease;
  border: 1px solid #f0f0f0;
}

.image-item:hover {
  transform: scale(1.03);
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.image-index {
  color: white;
  font-size: 16px;
  font-weight: 600;
}

/* 信息区域 */
.info-section {
  flex: 1;
  padding: 20px 24px;
  overflow-y: auto;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-group {
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.info-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-size: 14px;
  color: #666;
  min-width: 80px;
}

.info-value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
}

.reward-amount {
  color: #ff4d4f;
  font-weight: 600;
}

.feature-content,
.reward-desc {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.contact-label {
  font-size: 14px;
  color: #666;
  min-width: 40px;
}

.contact-value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
}

/* 操作按钮 */
.action-section {
  padding: 20px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.action-btn {
  width: 100%;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.claim-btn {
  background: #52c41a;
  color: white;
}

.claim-btn:hover {
  background: #73d13d;
}

.contact-btn {
  background: #1890ff;
  color: white;
}

.contact-btn:hover {
  background: #40a9ff;
}

/* 图片预览模态框 */
.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.preview-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.preview-close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
}

.preview-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
}

.preview-nav {
  position: absolute;
  bottom: -60px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.preview-counter {
  color: white;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-card {
    width: 95vw;
    max-height: 95vh;
    border-radius: 12px;
  }

  .card-header {
    padding: 16px 16px 0;
    padding-bottom: 16px;
  }

  .item-name {
    font-size: 18px;
  }

  .image-section,
  .info-section,
  .action-section {
    padding: 16px;
  }

  .info-group {
    padding: 12px;
  }

  .image-gallery {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .detail-card {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
    max-height: none;
  }

  .card-header {
    padding: 12px 12px 0;
    padding-bottom: 12px;
  }

  .item-name {
    font-size: 16px;
  }

  .image-section,
  .info-section,
  .action-section {
    padding: 12px;
  }
}
</style>