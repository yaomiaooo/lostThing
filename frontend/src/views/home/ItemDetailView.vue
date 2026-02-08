<template>
  <teleport to="body">
    <transition name="mask-fade">
      <div v-if="visible" class="detail-mask" @click.self="close">
        <transition name="card-pop">
          <div 
            class="detail-card" 
            :class="{ 
              'single-image': images.length === 1,
              'no-image': images.length === 0
            }"
            :style="cardStyle"
          >


            <!-- 内容区 -->
            <div v-if="ready" class="card-content">
              <!-- 左侧图片区域 -->
              <div 
                v-if="images.length > 0" 
                class="carousel-container" 
                ref="carouselContainer"
                :class="{ 'single-image-mode': images.length === 1 }"
                @mouseenter="handleMouseEnter"
                @mouseleave="handleMouseLeave"
              >
                <!-- 图片容器 -->
                <div 
                  v-if="images.length === 1"
                  class="single-image-wrapper"
                  :style="singleImageStyle"
                >
                  <img
                    :src="getImageUrl(images[0])"
                    :alt="`物品图片`"
                    @load="onSingleImageLoad"
                    @error="() => handleImageError(0)"
                    loading="lazy"
                    ref="singleImageRef"
                  />
                </div>
                
                <div 
                  v-else
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
                      :style="getMultiImageStyle(index)"
                      @load="(e) => onMultiImageLoad(e, index)"
                      @error="() => handleImageError(index)"
                      loading="lazy"
                    />
                    <div v-else class="image-placeholder">
                      <div class="loading-spinner"></div>
                    </div>
                  </div>
                </div>

                <!-- 左右箭头（仅在多张图片时显示） -->
                <template v-if="images.length > 1">
                  <button 
                    class="arrow-btn arrow-left" 
                    :class="{ 
                      'arrow-hidden': currentIndex === 0,
                      'nav-visible': isHovering
                    }"
                    @click="prevImage"
                    aria-label="上一张"
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24">
                      <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
                    </svg>
                  </button>
                  <button 
                    class="arrow-btn arrow-right" 
                    :class="{ 
                      'arrow-hidden': currentIndex === images.length - 1,
                      'nav-visible': isHovering
                    }"
                    @click="nextImage"
                    aria-label="下一张"
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24">
                      <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
                    </svg>
                  </button>
                </template>

                <!-- 文字指示器（右上角） -->
                <div v-if="images.length > 1" class="text-indicator" :class="{ 'nav-visible': isHovering }">
                  <div class="indicator-text">
                    {{ currentIndex + 1 }} / {{ images.length }}
                  </div>
                </div>
                
                <!-- 点选择器（底部） -->
                <div v-if="images.length > 1" class="dots-indicator" :class="{ 'nav-visible': isHovering }">
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
              <div 
                class="right-info"
                :class="{ 'full-width': images.length === 0 }"
              >
                <!-- 标题 -->
                <h2 class="title">{{ item.name }}</h2>

                <!-- 类型标签 -->
                <div class="info-line">
                  <span class="label">类型：</span>
                  <span class="category-tag" :class="item.itemCategory === 1 ? 'lost' : 'found'">
                    {{ item.itemCategory === 1 ? '失物信息' : '招领信息' }}
                  </span>
                </div>

                <!-- 物品分类（补充） -->
                <div class="info-line">
                  <span class="label">分类：</span>
                  <span>{{ getItemCategoryText() }}</span>
                </div>

                <!-- 校区 -->
                <div class="info-line">
                  <span class="label">校区：</span>
                  <span>{{ getCampusName(item.locationId) }}</span>
                </div>

                <!-- 丢失/拾取地点 -->
                <div class="info-line">
                  <span class="label">{{ item.itemCategory === 1 ? '丢失地点' : '拾取地点' }}：</span>
                  <span>{{ location?.name }} {{ item.locationDetail || '' }}</span>
                </div>

                <!-- 时间 -->
                <div class="info-line">
                  <span class="label">{{ item.itemCategory === 1 ? '丢失时间' : '拾取时间' }}：</span>
                  <span>{{ formatTime(item.happenTime) }}</span>
                </div>

                <!-- 领取地点（仅招领） -->
                <div v-if="item.itemCategory === 2 && item.pickupLocation" class="info-line">
                  <span class="label">领取地点：</span>
                  <span>{{ item.pickupLocation }}</span>
                </div>

                <!-- 特征描述 -->
                <div class="info-block">
                  <span class="label">特征描述：</span>
                  <div class="feature-text-wrapper">
                    <p 
                      class="feature-text" 
                      :class="{ 'text-collapsed': isFeatureCollapsed && featureTextLength > 100 }"
                    >
                      {{ item.feature }}
                    </p>
                    <span 
                      v-if="featureTextLength > 100" 
                      class="toggle-text" 
                      @click="isFeatureCollapsed = !isFeatureCollapsed"
                    >
                      {{ isFeatureCollapsed ? '展开' : '收起' }}
                    </span>
                  </div>
                </div>

                <!-- 发布时间 -->
                <div class="info-line text-muted">
                  <span class="label">发布时间：</span>
                  <span>{{ formatTime(item.createTime) }}</span>
                </div>

                <!-- 联系人 -->
                <div class="info-line">
                  <span class="label">联系人：</span>
                  <span class="contact-info">{{ item.contactName }}</span>
                </div>

                <!-- 联系电话（隐私保护） -->
                <div class="info-line">
                  <span class="label">联系电话：</span>
                  <span class="contact-phone">
                    {{ showFullPhone ? item.contactPhone : maskPhone(item.contactPhone) }}
                    <button 
                      v-if="!showFullPhone" 
                      class="show-phone-btn" 
                      @click="showFullPhone = true"
                    >
                      查看完整号码
                    </button>
                  </span>
                </div>

                <!-- 悬赏信息（仅失物） -->
                <div v-if="item.itemCategory === 1 && item.rewardAmount > 0" class="reward">
                  <span class="label">悬赏金额：</span>
                  <span class="reward-amount">￥{{ item.rewardAmount.toFixed(2) }}</span>
                  <span v-if="item.rewardDesc" class="reward-desc">（{{ item.rewardDesc }}）</span>
                </div>

                <!-- 驳回/归档说明（状态相关） -->
                <div v-if="item.currentStatus === 5 && item.rejectReason" class="status-desc reject-desc">
                  <span class="label">驳回原因：</span>
                  <span>{{ item.rejectReason }}</span>
                </div>
                <div v-if="item.currentStatus === 7 && item.archiveDesc" class="status-desc archive-desc">
                  <span class="label">归档说明：</span>
                  <span>{{ item.archiveDesc }}</span>
                </div>

                <!-- 操作按钮区域（从我的发布页面打开时显示） -->
                <div v-if="props.showActions" class="action-buttons">
                  <div class="action-buttons-container">
                    <!-- 待审核状态：修改、删除 -->
                    <template v-if="item.currentStatus === 1">
                      <button class="action-btn edit-btn" @click="handleEdit">
                        修改
                      </button>
                      <button class="action-btn delete-btn" @click="handleDelete">
                        删除
                      </button>
                    </template>

                    <!-- 已通过状态：取消发布 -->
                    <template v-else-if="item.currentStatus === 2">
                      <button class="action-btn cancel-btn" @click="handleCancel">
                        取消发布
                      </button>
                    </template>

                    <!-- 已驳回状态：修改、删除 -->
                    <template v-else-if="item.currentStatus === 5">
                      <button class="action-btn edit-btn" @click="handleEdit">
                        重新编辑
                      </button>
                      <button class="action-btn delete-btn" @click="handleDelete">
                        删除
                      </button>
                    </template>

                    <!-- 已取消状态：删除 -->
                    <template v-else-if="item.currentStatus === 6">
                      <button class="action-btn delete-btn" @click="handleDelete">
                        删除
                      </button>
                    </template>
                  </div>
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
import type { CSSProperties } from 'vue'
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
  rejectReason?: string
  archiveDesc?: string
}

interface LocationData {
  id: number
  name: string
  parentId: number
}

interface ImageSize {
  width: number
  height: number
  aspectRatio: number
  loaded: boolean
}

const props = defineProps<{
  visible: boolean
  itemId: number | null
  showActions?: boolean // 是否显示操作按钮（从我的发布页面打开时）
}>()

const emit = defineEmits(['close', 'edit', 'delete', 'cancel'])

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

// 图片尺寸信息
const imageSizes = ref<ImageSize[]>([])
const maxImageWidth = ref(0)
const carouselHeight = ref(500) // 固定高度

// 单张图片相关
const singleImageRef = ref<HTMLImageElement | null>(null)
const singleImageSize = ref<{width: number, height: number} | null>(null)

// DOM引用
const carouselContainer = ref<HTMLElement | null>(null)
const carouselTrack = ref<HTMLElement | null>(null)

// 新增：隐私保护和文本折叠
const showFullPhone = ref(false)
const isFeatureCollapsed = ref(true)
const featureTextLength = computed(() => item.value.feature?.length || 0)

// 新增：鼠标悬停控制导航元素显示
const isHovering = ref(false)

// 计算属性
const trackStyle = computed(() => {
  if (images.value.length <= 1) {
    return { transform: 'translateX(0%)', transition: 'none' }
  }
  
  const offset = -(currentIndex.value * 100) + (dragOffset.value / (carouselContainer.value?.offsetWidth || 1)) * 100
  return {
    transform: `translateX(${offset}%)`,
    transition: isTransitionEnabled.value ? 'transform 0.3s ease' : 'none'
  }
})

// 卡片样式
const cardStyle = computed(() => {
  if (images.value.length === 1 && singleImageSize.value) {
    const aspectRatio = singleImageSize.value.width / singleImageSize.value.height
    const imageWidth = Math.min(carouselHeight.value * aspectRatio, window.innerWidth * 0.8 - 400)
    
    return {
      width: `${imageWidth + 400}px`, // 图片宽度 + 右侧信息栏宽度
      maxWidth: '90vw'
    }
  }
  return {
    width: '900px',
    maxWidth: '90vw'
  }
})

// 单张图片容器样式
const singleImageStyle = computed(() => {
  if (!singleImageSize.value) return {}
  
  const aspectRatio = singleImageSize.value.width / singleImageSize.value.height
  const width = Math.min(carouselHeight.value * aspectRatio, window.innerWidth * 0.8 - 400)
  
  return {
    width: `${width}px`,
    height: `${carouselHeight.value}px`
  }
})

// 获取多张图片样式
const getMultiImageStyle = (index: number): CSSProperties => {
  const size = getImageSize(index)
  
  if (size.width > 0 && maxImageWidth.value > 0) {
    const scale = maxImageWidth.value / size.width
    const scaledHeight = size.height * scale
    
    return {
      width: `${maxImageWidth.value}px`,
      height: `${scaledHeight}px`,
      objectFit: 'contain' as const
    }
  }
  
  return {
    width: '100%',
    height: '100%',
    objectFit: 'contain' as const
  }
}

// 获取图片尺寸信息
const getImageSize = (index: number): ImageSize => {
  if (index < 0 || index >= imageSizes.value.length) {
    return { width: 0, height: 0, aspectRatio: 1, loaded: false }
  }
  return imageSizes.value[index]
}

// 图片懒加载策略
const shouldLoadImage = (index: number) => {
  if (loadedImages.value.has(index)) return true
  
  const distance = Math.abs(index - currentIndex.value)
  return distance <= 1
}

const getImageUrl = (img: ImageItem) => {
  if (img.url && img.url.startsWith('data:image')) {
    return img.url
  }
  if (img.id) {
    return `/api/item/image/${img.id}`
  }
  return img.url || ''
}

// 计算最宽图片宽度
const calculateMaxImageWidth = () => {
  if (images.value.length <= 1) return
  
  let maxWidth = 0
  imageSizes.value.forEach(size => {
    if (size.width > maxWidth) {
      maxWidth = size.width
    }
  })
  
  const containerWidth = carouselContainer.value?.offsetWidth || 500
  maxImageWidth.value = Math.min(maxWidth, containerWidth * 0.9)
}

// 单张图片加载完成
const onSingleImageLoad = (e: Event) => {
  const img = e.target as HTMLImageElement
  singleImageSize.value = {
    width: img.naturalWidth,
    height: img.naturalHeight
  }
}

// 多张图片加载完成
const onMultiImageLoad = (e: Event, index: number) => {
  const img = e.target as HTMLImageElement
  loadedImages.value.add(index)
  
  if (index < imageSizes.value.length) {
    imageSizes.value[index] = {
      width: img.naturalWidth,
      height: img.naturalHeight,
      aspectRatio: img.naturalWidth / img.naturalHeight,
      loaded: true
    }
  } else {
    imageSizes.value[index] = {
      width: img.naturalWidth,
      height: img.naturalHeight,
      aspectRatio: img.naturalWidth / img.naturalHeight,
      loaded: true
    }
  }
  
  if (loadedImages.value.size === images.value.length) {
    calculateMaxImageWidth()
  }
}

// 鼠标悬停事件处理
const handleMouseEnter = () => {
  isHovering.value = true
}

const handleMouseLeave = () => {
  isHovering.value = false
}

// 触摸事件处理
const handleTouchStart = (e: TouchEvent) => {
  if (images.value.length <= 1) return
  
  isDragging.value = true
  isTransitionEnabled.value = false
  startX.value = e.touches[0].clientX
  currentX.value = startX.value
  dragOffset.value = 0
}

const handleTouchMove = (e: TouchEvent) => {
  if (!isDragging.value || images.value.length <= 1) return
  
  e.preventDefault()
  currentX.value = e.touches[0].clientX
  dragOffset.value = currentX.value - startX.value
  
  const containerWidth = carouselContainer.value?.offsetWidth || 1
  const maxOffset = containerWidth * 0.3
  dragOffset.value = Math.max(-maxOffset, Math.min(maxOffset, dragOffset.value))
}

const handleTouchEnd = () => {
  if (!isDragging.value || images.value.length <= 1) return
  
  isDragging.value = false
  isTransitionEnabled.value = true
  
  const containerWidth = carouselContainer.value?.offsetWidth || 1
  const threshold = containerWidth * 0.15
  
  if (Math.abs(dragOffset.value) > threshold) {
    if (dragOffset.value > 0) {
      prevImage()
    } else {
      nextImage()
    }
  }
  
  setTimeout(() => {
    dragOffset.value = 0
  }, 300)
}

// 鼠标事件处理（桌面端）
const handleMouseDown = (e: MouseEvent) => {
  if (images.value.length <= 1) return
  
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
    
    const containerWidth = carouselContainer.value?.offsetWidth || 1
    const maxOffset = containerWidth * 0.3
    dragOffset.value = Math.max(-maxOffset, Math.min(maxOffset, dragOffset.value))
  }
  
  const handleMouseUp = () => {
    if (!isDragging.value) return
    
    isDragging.value = false
    isTransitionEnabled.value = true
    
    const containerWidth = carouselContainer.value?.offsetWidth || 1
    const threshold = containerWidth * 0.15
    
    if (Math.abs(dragOffset.value) > threshold) {
      if (dragOffset.value > 0) {
        prevImage()
      } else {
        nextImage()
      }
    }
    
    dragOffset.value = 0
    
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 图片切换方法
const nextImage = () => {
  if (images.value.length <= 1) return
  
  if (currentIndex.value < images.value.length - 1) {
    currentIndex.value++
    preloadAdjacentImages()
  }
}

const prevImage = () => {
  if (images.value.length <= 1) return
  
  if (currentIndex.value > 0) {
    currentIndex.value--
    preloadAdjacentImages()
  }
}

const goToImage = (index: number) => {
  if (index < 0 || index >= images.value.length) return
  
  currentIndex.value = index
  preloadAdjacentImages()
}

// 预加载相邻图片
const preloadAdjacentImages = () => {
  if (images.value.length === 0) return
  
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

// 新增：手机号脱敏
const maskPhone = (phone: string) => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 操作按钮事件处理
const handleEdit = () => {
  emit('edit', item.value)
}

const handleDelete = () => {
  emit('delete', item.value)
}

const handleCancel = () => {
  emit('cancel', item.value)
}

// 新增：校区信息
function getCampusName(locationId: number): string {
  const campusCode = Math.floor(locationId / 10000)
  switch (campusCode) {
    case 1:
      return '朝晖校区'
    case 2:
      return '屏峰校区'
    case 3:
      return '莫干山校区'
    default:
      return '未知校区'
  }
}

// // 新增：获取状态文本
// const getStatusText = () => {
//   const statusMap = {
//     1: '待审核',
//     2: '已通过',
//     3: '已匹配',
//     4: '已认领',
//     5: '已驳回',
//     6: '已取消',
//     7: '已归档',
//     8: '无效'
//   }
//   return statusMap[item.value.currentStatus] || '未知状态'
// }

// // 新增：获取状态样式类
// const getStatusClass = () => {
//   const statusClassMap = {
//     1: 'status-pending',
//     2: 'status-success',
//     3: 'status-matched',
//     4: 'status-claimed',
//     5: 'status-rejected',
//     6: 'status-canceled',
//     7: 'status-archived',
//     8: 'status-invalid'
//   }
//   return statusClassMap[item.value.currentStatus] || 'status-default'
// }

// 新增：分类数据
const categoryTree = ref<any[]>([])

// 新增：获取分类树数据
const loadCategoryTree = async () => {
  try {
    const response = await fetch('/api/item/category/tree')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200) {
        categoryTree.value = result.data
      }
    }
  } catch (error) {
    console.error('获取分类树失败:', error)
  }
}

// 新增：根据分类ID获取分类名称
const getCategoryNameById = (categoryId: number) => {
  if (!categoryTree.value.length) return '未知分类'
  
  // 递归查找分类
  const findCategory = (categories: any[], id: number): string | null => {
    for (const category of categories) {
      if (category.id === id) {
        return category.name
      }
      if (category.children && category.children.length > 0) {
        const found = findCategory(category.children, id)
        if (found) return found
      }
    }
    return null
  }
  
  return findCategory(categoryTree.value, categoryId) || '未知分类'
}

// 修改：获取物品分类文本，使用后端数据
const getItemCategoryText = () => {
  if (!item.value || !item.value.itemType) return '未知分类'
  return getCategoryNameById(item.value.itemType)
}

const close = () => {
  // 重置隐私状态
  showFullPhone.value = false
  isFeatureCollapsed.value = true
  emit('close')
}

// 加载详情数据
const loadDetail = async () => {
  if (!props.itemId) return
  ready.value = false
  currentIndex.value = 0
  loadedImages.value.clear()
  imageSizes.value = []
  maxImageWidth.value = 0
  dragOffset.value = 0
  singleImageSize.value = null
  showFullPhone.value = false
  isFeatureCollapsed.value = true
  
  // 加载分类树数据
  await loadCategoryTree()

  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: props.itemId }
    })

    const data = res.data.data
    item.value = data.item || data
    location.value = data.location || null
    
    if (Array.isArray(data.images)) {
      images.value = data.images
    } else {
      images.value = []
    }
    
    imageSizes.value = new Array(images.value.length).fill(null).map(() => ({
      width: 0,
      height: 0,
      aspectRatio: 1,
      loaded: false
    }))

    ready.value = true
    
    await nextTick()
    
    if (images.value.length > 0) {
      preloadAdjacentImages()
    }
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
      currentIndex.value = 0
      dragOffset.value = 0
      isDragging.value = false
      singleImageSize.value = null
      showFullPhone.value = false
      isFeatureCollapsed.value = true
    }
  }
)

// ESC 关闭和键盘切换
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowLeft' && images.value.length > 1) prevImage()
  if (e.key === 'ArrowRight' && images.value.length > 1) nextImage()
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
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* 无图片模式 */
.detail-card.no-image {
  width: 500px;
}

/* 关闭按钮已删除，点击空白区域关闭 */

/* 内容区域 */
.card-content {
  display: flex;
  height: 100%;
  width: 100%;
}

/* 左侧轮播图区域 */
.carousel-container {
  position: relative;
  height: 100%;
  overflow: hidden;
  background: #ffffff;
  user-select: none;
  touch-action: pan-y pinch-zoom;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 单张图片模式 */
.carousel-container.single-image-mode {
  background: transparent;
}

.single-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
}

.single-image-wrapper img {
  max-width: 100%;
  max-height: 100%;
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.carousel-track {
  display: flex;
  height: 500px; /* 固定高度 */
  will-change: transform;
  align-items: center;
  justify-content: flex-start;
}

.carousel-slide {
  flex: 0 0 100%;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-width: 100%;
}

.carousel-slide img {
  max-width: 100%;
  max-height: 100%;
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
  z-index: 10;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  opacity: 0;
  visibility: hidden;
}

.arrow-btn:hover:not(.arrow-hidden) {
  background: rgba(0, 0, 0, 0.8);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.arrow-btn.nav-visible {
  opacity: 1;
  visibility: visible;
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

/* 文字指示器（右上角） */
.text-indicator {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.text-indicator.nav-visible {
  opacity: 1;
  visibility: visible;
}

/* 点选择器（底部） */
.dots-indicator {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 10;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.dots-indicator.nav-visible {
  opacity: 1;
  visibility: visible;
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
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 右侧信息区域 */
.right-info {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  min-width: 300px;
  max-width: 400px;
}

/* 无图片时信息栏全宽 */
.right-info.full-width {
  width: 100%;
  max-width: none;
}

/* 标题 */
  .title {
    margin-bottom: 24px;
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1.4;
  }

/* 分类标签 */
.category-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.category-tag.lost {
  background: #fff1f0;
  color: #ff4d4f;
}

.category-tag.found {
  background: #f0fff4;
  color: #52c41a;
}

.info-line {
  margin-bottom: 16px;
  font-size: 15px;
  line-height: 1.6;
  display: flex;
  align-items: flex-start;
}

/* 浅色调文本 */
.text-muted {
  color: #8c8c8c;
  font-size: 14px;
}

.label {
  color: #666;
  margin-right: 8px;
  min-width: 70px;
  font-weight: 500;
}

.info-block {
  margin-bottom: 24px;
}

/* 特征描述优化 */
.feature-text-wrapper {
  position: relative;
}

.feature-text {
  margin: 8px 0 0 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  line-height: 1.7;
  color: #444;
  transition: max-height 0.3s ease;
  max-height: 500px;
}

.feature-text.text-collapsed {
  max-height: 100px;
  overflow: hidden;
  position: relative;
}

.feature-text.text-collapsed::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(to top, #f8f9fa, transparent);
}

.toggle-text {
  display: inline-block;
  margin-top: 8px;
  color: #1890ff;
  cursor: pointer;
  font-size: 14px;
}

.toggle-text:hover {
  color: #40a9ff;
  text-decoration: underline;
}

.contact-info {
  font-weight: 500;
  color: #2c3e50;
}

/* 联系电话样式 */
.contact-phone {
  display: flex;
  align-items: center;
  gap: 8px;
}

.show-phone-btn {
  background: #f0f9ff;
  color: #1890ff;
  border: none;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.show-phone-btn:hover {
  background: #e6f7ff;
  color: #40a9ff;
}

/* 悬赏样式优化 */
.reward {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #fff9e6 0%, #ffe58f 100%);
  border-radius: 8px;
  border-left: 4px solid #faad14;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
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
  margin-left: 4px;
}

/* 状态说明（驳回/归档） */
.status-desc {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
}

.reject-desc {
  background: #fff2f0;
  color: #f5222d;
  border-left: 4px solid #ff4d4f;
}

.archive-desc {
  background: #f9f0ff;
  color: #9254de;
  border-left: 4px solid #9254de;
}

/* 操作按钮区域样式 */
.action-buttons {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.2);
}

.action-buttons-container {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.3);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.2);
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.edit-btn {
  background: linear-gradient(to right, #4caf50, #45a049);
  color: white;
}

.edit-btn:hover {
  background: linear-gradient(to right, #45a049, #4caf50);
}

.delete-btn {
  background: linear-gradient(to right, #f44336, #d32f2f);
  color: white;
}

.delete-btn:hover {
  background: linear-gradient(to right, #d32f2f, #f44336);
}

.cancel-btn {
  background: linear-gradient(to right, #ff9800, #f57c00);
  color: white;
}

.cancel-btn:hover {
  background: linear-gradient(to right, #f57c00, #ff9800);
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
@media (max-width: 1024px) {
  .detail-card {
    height: 500px;
  }
  
  .carousel-track {
    height: 400px;
  }
  
  .carousel-slide {
    height: 400px;
  }
  
  .right-info {
    padding: 24px;
  }
  
  .single-image-wrapper {
    height: 400px;
  }
}

@media (max-width: 768px) {
  .detail-card {
    flex-direction: column;
    height: 90vh;
    width: 95vw !important;
    max-width: 95vw;
    border-radius: 12px;
  }
  
  .carousel-container {
    width: 100%;
    height: 45vh;
  }
  
  .carousel-track {
    height: 40vh;
  }
  
  .carousel-slide {
    height: 40vh;
  }
  
  .right-info {
    padding: 20px;
    overflow-y: auto;
    max-height: 45vh;
    max-width: 100%;
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
  
  .dots-indicator {
    bottom: 12px;
  }
  
  .title {
    font-size: 20px;
    margin-bottom: 20px;
    padding-bottom: 0;
    border-bottom: none;
  }
  
  .single-image-wrapper {
    height: 40vh;
    width: 100% !important;
  }
}

@media (max-width: 480px) {
  .detail-card {
    height: 100vh;
    max-width: 100vw !important;
    border-radius: 0;
  }
  
  .carousel-container {
    height: 50vh;
  }
  
  .carousel-track {
    height: 45vh;
  }
  
  .carousel-slide {
    height: 45vh;
  }
  
  .right-info {
    max-height: 50vh;
  }
  
  /* 关闭按钮和状态标签已删除 */
  
  .single-image-wrapper {
    height: 45vh;
  }
}
</style>