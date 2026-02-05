<template>
  <teleport to="body">
    <transition name="mask-fade">
      <div v-if="visible" class="detail-mask" @click.self="close">
        <transition name="card-pop">
          <div class="detail-card">
            <!-- 关闭按钮 -->
            <div class="close-btn" @click="close">×</div>

            <!-- 内容区 -->
            <div v-if="ready" class="card-content">
              <!-- 左侧图片轮播区域 -->
              <div class="carousel-container" ref="carouselContainer">
                <!-- 图片容器 -->
                <div 
                  class="carousel-track" 
                  ref="carouselTrack"
                  :style="trackStyle"
                  @touchstart="handleTouchStart"
                  @touchmove="handleTouchMove"
                  @touchend="handleTouchEnd"
                  @mousedown="handleMouseDown"
                >
                  <div 
                    v-for="(img, index) in images" 
                    :key="img.id || `img-${index}`" 
                    class="carousel-slide"
                  >
                    <!-- 图片懒加载 -->
                    <img
                      v-if="shouldLoadImage(index)"
                      :src="getImageUrl(img)"
                      :alt="`物品图片 ${index + 1}`"
                      @load="() => onImageLoad(index)"
                      @error="() => handleImageError(index)"
                      loading="lazy"
                    />
                    <div v-else class="image-placeholder">
                      <div class="loading-spinner"></div>
                    </div>
                  </div>
                </div>

                <!-- 左右箭头（仅在多张图片时显示） -->
                <template v-if="images && images.length > 1">
                  <button 
                    class="arrow-btn arrow-left" 
                    :class="{ 'arrow-hidden': currentIndex === 0 }"
                    @click="prevImage"
                    aria-label="上一张"
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24">
                      <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
                    </svg>
                  </button>
                  <button 
                    class="arrow-btn arrow-right" 
                    :class="{ 'arrow-hidden': currentIndex === images.length - 1 }"
                    @click="nextImage"
                    aria-label="下一张"
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24">
                      <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
                    </svg>
                  </button>
                </template>

                <!-- 文字指示器（右上角） -->
                <div v-if="images && images.length > 1" class="text-indicator">
                  <div class="indicator-text">
                    {{ currentIndex + 1 }} / {{ images.length }}
                  </div>
                </div>
                
                <!-- 点选择器（底部） -->
                <div v-if="images && images.length > 1" class="dots-indicator">
                  <div class="indicator-dots">
                    <div 
                      v-for="(img, index) in images" 
                      :key="index" 
                      class="dot" 
                      :class="{ 'dot-active': index === currentIndex }"
                      @click="goToImage(index)"
                      :aria-label="`查看第 ${index + 1} 张图片`"
                    ></div>
                  </div>
                </div>
              </div>

              <!-- 右侧信息 -->
              <div class="right-info">
                <h2 class="title">{{ item.name }}</h2>

                <div class="info-line">
                  <span class="label">类型：</span>
                  <span>{{ item.itemCategory === 1 ? '失物' : '招领' }}</span>
                </div>

                <div class="info-line">
                  <span class="label">地点：</span>
                  <span>{{ location?.name }} {{ item.locationDetail }}</span>
                </div>

                <div class="info-line">
                  <span class="label">时间：</span>
                  <span>{{ formatTime(item.happenTime) }}</span>
                </div>

                <div class="info-block">
                  <span class="label">特征描述：</span>
                  <p class="feature-text">{{ item.feature }}</p>
                </div>

                <div class="info-line">
                  <span class="label">联系人：</span>
                  <span class="contact-info">{{ item.contactName }} {{ item.contactPhone }}</span>
                </div>

                <div v-if="item.rewardAmount > 0" class="reward">
                  <span class="label">悬赏：</span>
                  <span class="reward-amount">￥{{ item.rewardAmount }}</span>
                  <span v-if="item.rewardDesc" class="reward-desc">（{{ item.rewardDesc }}）</span>
                </div>
              </div>
            </div>

            <!-- loading 占位 -->
            <div v-else class="loading">
              <div class="loading-spinner large"></div>
              <div class="loading-text">加载中…</div>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import axios from 'axios'

interface ImageItem {
  id?: number
  url: string
  itemId?: number
  imageType?: number
  sort?: number
  createTime?: string
}

interface ItemData {
  id: number
  userId: number
  name: string
  itemType: number
  itemCategory: number
  locationId: number
  happenTime: string
  feature: string
  rewardAmount: number
  rewardDesc?: string
  contactName: string
  contactPhone: string
  currentStatus: number
  createTime: string
  locationDetail?: string
  pickupLocation?: string
}

interface LocationData {
  id: number
  name: string
  parentId: number
}

const props = defineProps<{
  visible: boolean
  itemId: number | null
}>()

const emit = defineEmits(['close'])

// 状态管理
const ready = ref(false)
const item = ref<ItemData>({} as ItemData)
const location = ref<LocationData | null>(null)
const images = ref<ImageItem[]>([])

// 轮播图状态
const currentIndex = ref(0)
const isDragging = ref(false)
const startX = ref(0)
const currentX = ref(0)
const dragOffset = ref(0)
const isTransitionEnabled = ref(true)
const loadedImages = ref<Set<number>>(new Set())

// DOM引用
const carouselContainer = ref<HTMLElement | null>(null)
const carouselTrack = ref<HTMLElement | null>(null)

// 计算属性 - 修复：检查 images 是否存在
const trackStyle = computed(() => {
  if (!images.value || images.value.length === 0) {
    return { transform: 'translateX(0%)', transition: 'none' }
  }
  
  const offset = -(currentIndex.value * 100) + (dragOffset.value / (carouselContainer.value?.offsetWidth || 1)) * 100
  return {
    transform: `translateX(${offset}%)`,
    transition: isTransitionEnabled.value ? 'transform 0.3s ease' : 'none'
  }
})

// 图片懒加载策略：预加载当前、前一张、后一张
const shouldLoadImage = (index: number) => {
  // 已经加载过的
  if (loadedImages.value.has(index)) return true
  
  // 当前图片、前一张、后一张
  const distance = Math.abs(index - currentIndex.value)
  return distance <= 1
}

const getImageUrl = (img: ImageItem) => {
  // 处理图片URL
  if (img.url && img.url.startsWith('data:image')) {
    return img.url
  }
  // 如果图片有ID，使用图片ID获取，否则尝试使用itemId
  if (img.id) {
    return `/api/item/image/${img.id}`
  }
  return img.url || ''
}

// 触摸事件处理
const handleTouchStart = (e: TouchEvent) => {
  if (!images.value || images.value.length <= 1) return
  
  isDragging.value = true
  isTransitionEnabled.value = false
  startX.value = e.touches[0].clientX
  currentX.value = startX.value
  dragOffset.value = 0
}

const handleTouchMove = (e: TouchEvent) => {
  if (!isDragging.value || !images.value || images.value.length <= 1) return
  
  e.preventDefault()
  currentX.value = e.touches[0].clientX
  dragOffset.value = currentX.value - startX.value
  
  // 限制拖拽范围
  const containerWidth = carouselContainer.value?.offsetWidth || 1
  const maxOffset = containerWidth * 0.3
  dragOffset.value = Math.max(-maxOffset, Math.min(maxOffset, dragOffset.value))
}

const handleTouchEnd = () => {
  if (!isDragging.value || !images.value || images.value.length <= 1) return
  
  isDragging.value = false
  isTransitionEnabled.value = true
  
  const containerWidth = carouselContainer.value?.offsetWidth || 1
  const threshold = containerWidth * 0.15 // 降低阈值，更容易触发切换
  
  if (Math.abs(dragOffset.value) > threshold) {
    if (dragOffset.value > 0) {
      // 向右滑动，显示前一张
      prevImage()
    } else {
      // 向左滑动，显示下一张
      nextImage()
    }
  }
  
  // 重置拖拽偏移
  setTimeout(() => {
    dragOffset.value = 0
  }, 300)
}

// 鼠标事件处理（桌面端）
const handleMouseDown = (e: MouseEvent) => {
  if (!images.value || images.value.length <= 1) return
  
  // 检查是否点击了箭头按钮
  const target = e.target as HTMLElement
  if (target.closest('.arrow-btn')) {
    return
  }
  
  isDragging.value = true
  isTransitionEnabled.value = false
  startX.value = e.clientX
  currentX.value = startX.value
  dragOffset.value = 0
  
  const handleMouseMove = (moveEvent: MouseEvent) => {
    if (!isDragging.value) return
    
    currentX.value = moveEvent.clientX
    dragOffset.value = currentX.value - startX.value
    
    // 限制拖拽范围
    const containerWidth = carouselContainer.value?.offsetWidth || 1
    const maxOffset = containerWidth * 0.3
    dragOffset.value = Math.max(-maxOffset, Math.min(maxOffset, dragOffset.value))
  }
  
  const handleMouseUp = () => {
    if (!isDragging.value) return
    
    isDragging.value = false
    isTransitionEnabled.value = true
    
    const containerWidth = carouselContainer.value?.offsetWidth || 1
    const threshold = containerWidth * 0.15 // 降低阈值，更容易触发切换
    
    if (Math.abs(dragOffset.value) > threshold) {
      if (dragOffset.value > 0) {
        prevImage()
      } else {
        nextImage()
      }
    }
    
    dragOffset.value = 0
    
    // 清理事件监听
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 图片切换方法
const nextImage = () => {
  if (!images.value || images.value.length === 0) return
  
  if (currentIndex.value < images.value.length - 1) {
    currentIndex.value++
    // 预加载下一张图片
    preloadAdjacentImages()
  }
}

const prevImage = () => {
  if (!images.value || images.value.length === 0) return
  
  if (currentIndex.value > 0) {
    currentIndex.value--
    // 预加载上一张图片
    preloadAdjacentImages()
  }
}

const goToImage = (index: number) => {
  if (!images.value || index < 0 || index >= images.value.length) return
  
  currentIndex.value = index
  // 预加载相邻图片
  preloadAdjacentImages()
}

// 预加载相邻图片
const preloadAdjacentImages = () => {
  if (!images.value || images.value.length === 0) return
  
  const indicesToLoad = [
    currentIndex.value - 1,
    currentIndex.value,
    currentIndex.value + 1
  ].filter(index => index >= 0 && index < images.value.length)
  
  indicesToLoad.forEach(index => {
    if (!loadedImages.value.has(index) && images.value[index]) {
      const img = new Image()
      img.src = getImageUrl(images.value[index])
      img.onload = () => {
        loadedImages.value.add(index)
      }
    }
  })
}

// 图片加载完成处理
const onImageLoad = (index: number) => {
  loadedImages.value.add(index)
}

const handleImageError = (index: number) => {
  console.error(`图片 ${index + 1} 加载失败`)
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return timeStr
  }
}

const close = () => {
  emit('close')
}

// 加载详情数据
const loadDetail = async () => {
  if (!props.itemId) return
  ready.value = false
  currentIndex.value = 0
  loadedImages.value.clear()
  dragOffset.value = 0

  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: props.itemId }
    })

    const data = res.data.data
    item.value = data.item || data
    location.value = data.location || null
    
    // 确保 images 是数组
    if (Array.isArray(data.images)) {
      images.value = data.images
    } else {
      images.value = []
    }
    
    console.log('加载的图片数据:', images.value)
    
    // 预加载第一张图片
    if (images.value.length > 0) {
      preloadAdjacentImages()
    }

    ready.value = true
    
    // 等待 DOM 更新后，重新计算容器宽度
    await nextTick()
  } catch (e) {
    console.error('加载详情失败:', e)
    ready.value = true
    images.value = []
  }
}

// 监听变化
watch(
  () => props.itemId,
  () => {
    if (props.visible) loadDetail()
  }
)

watch(
  () => props.visible,
  (v) => {
    if (v && props.itemId) {
      loadDetail()
    } else {
      // 关闭时重置状态
      currentIndex.value = 0
      dragOffset.value = 0
      isDragging.value = false
    }
  }
)

// ESC 关闭和键盘切换
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowLeft' && images.value && images.value.length > 1) prevImage()
  if (e.key === 'ArrowRight' && images.value && images.value.length > 1) nextImage()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
/* 遮罩 */
.detail-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

/* 卡片主体 */
.detail-card {
  position: relative;
  height: 580px;
  max-width: 95vw;
  width: 900px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  right: 20px;
  top: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  cursor: pointer;
  z-index: 10;
  transition: all 0.2s;
  border: none;
  color: #333;
}

.close-btn:hover {
  background: #fff;
  transform: scale(1.1);
}

/* 内容区域 */
.card-content {
  display: flex;
  height: 100%;
  width: 100%;
}

/* 左侧轮播图区域 */
.carousel-container {
  position: relative;
  width: 500px;
  height: 100%;
  overflow: hidden;
  background: #f8f9fa;
  user-select: none;
  touch-action: pan-y pinch-zoom;
}

.carousel-track {
  display: flex;
  height: 100%;
  will-change: transform;
}

.carousel-slide {
  flex: 0 0 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-width: 100%;
}

.carousel-slide img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #409eff;
  animation: spin 1s ease-in-out infinite;
}

.loading-spinner.large {
  width: 60px;
  height: 60px;
  border-width: 4px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.image-error {
  color: #999;
  font-size: 14px;
  padding: 20px;
}

/* 左右箭头按钮 */
.arrow-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.arrow-btn:hover:not(.arrow-hidden) {
  background: rgba(0, 0, 0, 0.8);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.arrow-btn svg {
  fill: #fff;
  width: 20px;
  height: 20px;
}

.arrow-left {
  left: 16px;
}

.arrow-right {
  right: 16px;
}

.arrow-hidden {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
}

/* 轮播指示器 */
/* 文字指示器（右上角） */
.text-indicator {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
}

/* 点选择器（底部） */
.dots-indicator {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 2;
}

.indicator-dots {
  display: flex;
  gap: 10px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: scale(1.3);
}

.dot-active {
  background: #fff;
  transform: scale(1.4);
}

.indicator-text {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.6);
  padding: 6px 12px;
  border-radius: 16px;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-family: "Comic Sans MS", cursive;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 右侧信息区域 */
.right-info {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  min-width: 300px;
}

.title {
  margin: 0 0 24px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.4;
}

.info-line {
  margin-bottom: 16px;
  font-size: 15px;
  line-height: 1.6;
  display: flex;
  align-items: flex-start;
}

.label {
  color: #666;
  margin-right: 8px;
  min-width: 60px;
  font-weight: 500;
}

.info-block {
  margin-bottom: 24px;
}

.feature-text {
  margin: 8px 0 0 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  line-height: 1.7;
  color: #444;
}

.contact-info {
  font-weight: 500;
  color: #2c3e50;
}

.reward {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #fff9e6 0%, #ffe58f 100%);
  border-radius: 8px;
  border-left: 4px solid #faad14;
}

.reward-amount {
  font-size: 18px;
  font-weight: 700;
  color: #fa8c16;
  margin: 0 8px;
}

.reward-desc {
  color: #8c8c8c;
  font-size: 14px;
}

/* loading 占位 */
.loading {
  width: 500px;
  height: 580px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.loading-text {
  margin-top: 20px;
  font-size: 16px;
}

/* 动画 */
.mask-fade-enter-active,
.mask-fade-leave-active {
  transition: opacity 0.3s ease;
}

.mask-fade-enter-from,
.mask-fade-leave-to {
  opacity: 0;
}

.card-pop-enter-active,
.card-pop-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-pop-enter-from {
  transform: scale(0.9);
  opacity: 0;
}

.card-pop-leave-to {
  transform: scale(0.9);
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-card {
    flex-direction: column;
    height: 90vh;
    width: 95vw;
    max-width: 95vw;
    border-radius: 12px;
  }
  
  .carousel-container {
    width: 100%;
    height: 45vh;
  }
  
  .right-info {
    padding: 20px;
    overflow-y: auto;
    max-height: 45vh;
  }
  
  .arrow-btn {
    width: 40px;
    height: 40px;
  }
  
  .arrow-left {
    left: 8px;
  }
  
  .arrow-right {
    right: 8px;
  }
  
  .carousel-indicator {
    bottom: 16px;
  }
  
  .title {
    font-size: 20px;
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .detail-card {
    height: 100vh;
    max-width: 100vw;
    border-radius: 0;
  }
  
  .carousel-container {
    height: 50vh;
  }
  
  .right-info {
    max-height: 50vh;
  }
  
  .close-btn {
    right: 12px;
    top: 12px;
    width: 28px;
    height: 28px;
    font-size: 20px;
  }
}
</style>