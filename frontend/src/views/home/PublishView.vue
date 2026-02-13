<template>
  <div class="publish-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏组件 -->
    <Navigation 
      subtitle="欢迎回来^_^"
      active-nav="发布"
      :custom-content="true"
      @logout="handleLogout"
    >
      <template #custom-content>
        <div class="notice-content">
          <div class="notice-title">📝 发布须知</div>
          <div class="notice-desc">
            1. 请如实填写物品信息<br>
            2. 上传清晰照片有助于匹配<br>
            3. 失物可设置悬赏金额<br>
            4. 招领请说明领取地点<br>
            5. 信息审核通过后显示
          </div>
        </div>
        <div class="notice-time">{{ currentDate }}</div>
      </template>
    </Navigation>

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 发布表单卡片 -->
        <div class="publish-form-card bubble">
          <div class="form-header">
            <h2 class="form-title">{{ isEditMode ? '编辑物品信息' : '发布物品信息' }}</h2>
            <div class="form-subtitle">{{ isEditMode ? '请修改物品信息，确保准确无误' : '请仔细填写以下信息，确保准确无误' }}</div>
          </div>

          <!-- 表单内容 - 优化双栏布局 -->
          <form @submit.prevent="submitForm" class="form-content">
            <!-- 左栏：基础信息 -->
            <div class="form-left-column">
              <!-- 发布类型 -->
              <div class="form-section">
                <div class="section-header">
                  <h3 class="section-title">发布类型</h3>
                  <span class="required-mark">*</span>
                </div>
                <div class="form-row">
                  <div class="horizontal-options">
                    <button
                      v-for="type in publishTypes"
                      :key="type.value"
                      type="button"
                      class="type-option horizontal-option"
                      :class="{ 
                        active: formData.itemCategory === type.value,
                        disabled: submitting
                      }"
                      @click="changePublishType(type.value)"
                    >
                      <span class="type-label">{{ type.label }}</span>
                      <span class="type-desc">{{ type.desc }}</span>
                    </button>
                  </div>
                  <div v-if="formErrors.itemCategory" class="error-message">
                    {{ formErrors.itemCategory }}
                  </div>
                </div>
              </div>

              <!-- 物品分类与名称水平排列 -->
              <div class="horizontal-group">
                <!-- 物品分类 -->
                <div class="form-section compact-section">
                  <div class="section-header">
                    <h3 class="section-title">物品分类</h3>
                    <span class="required-mark">*</span>
                  </div>
                  <div class="form-row">
                    <div class="compact-cascader">
                      <!-- 一级分类 -->
                      <div class="compact-level">
                        <label class="compact-label">一级分类</label>
                        <select 
                          v-model="selectedFirstCategory"
                          class="compact-select"
                          :disabled="submitting || !categoryTree.length"
                          @change="onFirstCategoryChange"
                        >
                          <option 
                            v-for="cat in firstCategories" 
                            :key="cat.id"
                            :value="cat.id"
                          >
                            {{ cat.name }}
                          </option>
                        </select>
                      </div>

                      <!-- 二级分类 -->
                      <div class="compact-level">
                        <label class="compact-label">二级分类</label>
                        <select 
                          v-model="selectedSecondCategory"
                          class="compact-select"
                          :disabled="submitting || !selectedFirstCategory"
                          @change="onSecondCategoryChange"
                        >
                          <option 
                            v-for="cat in secondCategories" 
                            :key="cat.id"
                            :value="cat.id"
                          >
                            {{ cat.name }}
                          </option>
                        </select>
                      </div>
                    </div>
                    <div v-if="formErrors.itemType" class="error-message">
                      {{ formErrors.itemType }}
                    </div>
                  </div>
                </div>

                <!-- 物品名称 -->
                <div class="form-section compact-section">
                  <div class="section-header">
                    <h3 class="section-title">物品名称</h3>
                    <span class="required-mark">*</span>
                  </div>
                  <div class="form-row">
                    <input
                      v-model="formData.name"
                      type="text"
                      class="form-input compact-input"
                      :class="{ error: formErrors.name }"
                      placeholder="如：黑色蓝牙耳机"
                      :disabled="submitting"
                      maxlength="50"
                    />
                    <div v-if="formErrors.name" class="error-message">
                      {{ formErrors.name }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- 地点信息 -->
              <div class="form-section">
                <div class="section-header">
                  <h3 class="section-title">地点信息</h3>
                  <span class="required-mark">*</span>
                </div>
                <div class="form-row">
                  <div class="location-cascader">
                    <!-- 校区 -->
                    <div class="compact-level">
                      <label class="compact-label">校区</label>
                      <select 
                        v-model="selectedCampus"
                        class="compact-select"
                        :disabled="submitting || !locationTree.length"
                        @change="onCampusChange"
                      >
                        <option 
                          v-for="campus in campuses" 
                          :key="campus.id"
                          :value="campus.id"
                        >
                          {{ campus.name }}
                        </option>
                      </select>
                    </div>

                    <!-- 区域 -->
                    <div class="compact-level">
                      <label class="compact-label">区域</label>
                      <select 
                        v-model="selectedArea"
                        class="compact-select"
                        :disabled="submitting || !selectedCampus"
                        @change="onAreaChange"
                      >
                        <option 
                          v-for="area in areas" 
                          :key="area.id"
                          :value="area.id"
                        >
                          {{ area.name }}
                        </option>
                      </select>
                    </div>

                    <!-- 具体地点 -->
                    <div class="compact-level">
                      <label class="compact-label">具体地点</label>
                      <select 
                        v-model="selectedLocation"
                        class="compact-select"
                        :disabled="submitting || !selectedArea"
                        @change="onLocationChange"
                      >
                        <option 
                          v-for="location in locations" 
                          :key="location.id"
                          :value="location.id"
                        >
                          {{ location.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  
                  <!-- 具体地点补充 -->
                  <div class="compact-level">
                    <label class="compact-label">位置补充</label>
                    <input
                      v-model="formData.locationDetail"
                      type="text"
                      class="compact-input"
                      :class="{ error: formErrors.locationDetail }"
                      placeholder="如：三楼自习区、操场跑道内侧"
                      :disabled="submitting"
                      maxlength="255"
                    />
                  </div>
                  
                  <div v-if="formErrors.locationDetail" class="error-message">
                    {{ formErrors.locationDetail }}
                  </div>
                </div>
              </div>

              <!-- 时间与悬赏信息水平排列 -->
              <div class="horizontal-group">
                <!-- 时间信息 -->
                <div class="form-section compact-section">
                  <div class="section-header">
                    <h3 class="section-title">{{ formData.itemCategory === 1 ? '丢失时间' : '发现时间' }}</h3>
                    <span class="required-mark">*</span>
                  </div>
                  <div class="form-row">
                    <input
                      v-model="formData.happenTime"
                      type="datetime-local"
                      class="form-input compact-input datetime-input"
                      :class="{ error: formErrors.happenTime }"
                      :disabled="submitting"
                    />
                    <div v-if="formErrors.happenTime" class="error-message">
                      {{ formErrors.happenTime }}
                    </div>
                  </div>
                </div>

                <!-- 悬赏金额（仅失物） -->
                <div v-if="formData.itemCategory === 1" class="form-section compact-section">
                  <div class="section-header">
                    <h3 class="section-title">悬赏金额</h3>
                    <span class="optional-mark">（元）</span>
                  </div>
                  <div class="form-row">
                    <div class="reward-amount-input">
                      <div class="currency-input">
                        <span class="currency-symbol">¥</span>
                        <input
                          v-model="formData.rewardAmount"
                          type="number"
                          class="form-input compact-input reward-input"
                          :class="{ error: formErrors.rewardAmount }"
                          placeholder="0.00"
                          :disabled="submitting"
                          min="0"
                          max="999999.99"
                          step="0.01"
                        />
                      </div>
                      <div v-if="formErrors.rewardAmount" class="error-message">
                        {{ formErrors.rewardAmount }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 领取地点（仅招领） -->
                <div v-if="formData.itemCategory === 2" class="form-section compact-section">
                  <div class="section-header">
                    <h3 class="section-title">领取地点</h3>
                    <span class="optional-mark">（可选）</span>
                  </div>
                  <div class="form-row">
                    <input
                      v-model="formData.pickupLocation"
                      type="text"
                      class="form-input compact-input"
                      :class="{ error: formErrors.pickupLocation }"
                      placeholder="如：保卫处值班室"
                      :disabled="submitting"
                      maxlength="255"
                    />
                    <div v-if="formErrors.pickupLocation" class="error-message">
                      {{ formErrors.pickupLocation }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右栏：详细信息 -->
            <div class="form-right-column">
              <!-- 特征描述 -->
              <div class="form-section">
                <div class="section-header">
                  <h3 class="section-title">特征描述</h3>
                  <span class="required-mark">*</span>
                </div>
                <div class="form-row">
                  <textarea
                    v-model="formData.feature"
                    class="form-textarea"
                    :class="{ error: formErrors.feature }"
                    placeholder="请详细描述物品特征，如：颜色、大小、品牌、磨损情况、特殊标记等"
                    :disabled="submitting"
                    rows="6"
                    maxlength="1000"
                  ></textarea>
                  <div class="textarea-footer">
                    <div v-if="formErrors.feature" class="error-message">
                      {{ formErrors.feature }}
                    </div>
                    <div class="char-counter">{{ formData.feature.length }}/1000</div>
                  </div>
                </div>
              </div>

              <!-- 图片上传 -->
              <div class="form-section">
                <div class="section-header">
                  <h3 class="section-title">上传图片</h3>
                  <span class="optional-mark">（最多5张）</span>
                </div>
                <div class="form-row">
                  <div class="compact-uploader">
                    <!-- 上传区域 -->
                    <div 
                      class="upload-area compact-upload-area"
                      :class="{ disabled: submitting, 'drag-over': dragOver }"
                      @click="triggerFileInput"
                      @dragover.prevent="handleDragOver"
                      @dragleave.prevent="handleDragLeave"
                      @drop.prevent="handleDrop"
                    >
                      <div class="upload-icon">
                        <img src="/home/上传.svg" alt="上传" class="upload-svg" />
                      </div>
                      <p class="upload-text">点击或拖拽上传图片</p>
                      <p class="upload-hint">每张不超过5MB</p>
                    </div>
                    <input
                      ref="fileInput"
                      type="file"
                      multiple
                      accept="image/*"
                      class="file-input"
                      @change="handleFileSelect"
                      :disabled="submitting"
                    />

                    <!-- 图片预览区 -->
                    <div v-if="images.length > 0" class="compact-preview">
                      <div class="preview-header">
                        <span class="preview-title">已上传 {{ images.length }}/5</span>
                        <button 
                          type="button"
                          class="clear-all-btn"
                          @click="clearAllImages"
                          :disabled="submitting"
                        >
                          清空
                        </button>
                      </div>
                      <div class="image-grid">
                        <div 
                          v-for="(image, index) in images"
                          :key="index"
                          class="grid-item"
                          draggable="true"
                          @dragstart="handleDragStart(index)"
                          @dragover.prevent
                          @drop="handleDropSort(index)"
                        >
                          <img :src="image.previewUrl" class="grid-image" />
                          <div class="grid-overlay">
                            <button 
                              type="button"
                              class="grid-delete-btn"
                              @click.stop="removeImage(index)"
                              :disabled="submitting"
                            >
                              ×
                            </button>
                            <div class="grid-sort" title="拖动排序">↕</div>
                          </div>
                          <div class="grid-index">{{ index + 1 }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-if="formErrors.images" class="error-message">
                    {{ formErrors.images }}
                  </div>
                </div>
              </div>

              <!-- 悬赏说明与联系人水平排列 -->
              <div class="horizontal-group">
                <!-- 悬赏说明（仅失物） -->
                <div v-if="formData.itemCategory === 1" class="form-section compact-section">
                  <div class="section-header">
                    <h3 class="section-title">悬赏说明</h3>
                    <span class="optional-mark">（可选）</span>
                  </div>
                  <div class="form-row">
                    <input
                      v-model="formData.rewardDesc"
                      type="text"
                      class="form-input compact-input"
                      :class="{ error: formErrors.rewardDesc }"
                      placeholder="如：找到必有重谢"
                      :disabled="submitting"
                      maxlength="200"
                    />
                    <div v-if="formErrors.rewardDesc" class="error-message">
                      {{ formErrors.rewardDesc }}
                    </div>
                  </div>
                </div>

                <!-- 联系人信息 -->
                <div class="form-section compact-section">
                  <div class="section-header">
                    <h3 class="section-title">联系人</h3>
                    <span class="required-mark">*</span>
                  </div>
                  <div class="form-row">
                    <div class="compact-contact">
                      <div class="contact-field">
                        <label class="compact-label">姓名</label>
                        <input
                          v-model="formData.contactName"
                          type="text"
                          class="compact-input"
                          :class="{ error: formErrors.contactName }"
                          :disabled="submitting"
                          maxlength="20"
                        />
                      </div>
                      <div class="contact-field">
                        <label class="compact-label">电话</label>
                        <input
                          v-model="formData.contactPhone"
                          type="tel"
                          class="compact-input"
                          :class="{ error: formErrors.contactPhone }"
                          :disabled="submitting"
                          placeholder="11位手机号"
                          maxlength="11"
                        />
                      </div>
                    </div>
                    <div v-if="formErrors.contactName" class="error-message">
                      {{ formErrors.contactName }}
                    </div>
                    <div v-if="formErrors.contactPhone" class="error-message">
                      {{ formErrors.contactPhone }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 表单操作按钮（全宽） -->
            <div class="form-actions">
              <button
                type="button"
                class="action-btn cancel-btn"
                @click="goBack"
                :disabled="submitting"
              >
                取消
              </button>
              <button
                type="submit"
                class="action-btn submit-btn"
                :class="{ submitting: submitting }"
                :disabled="submitting"
              >
                <span v-if="submitting" class="loading-text">
                  <span class="loading-spinner"></span>
                  {{ isEditMode ? '更新中...' : '提交中...' }}
                </span>
                <span v-else>{{ isEditMode ? '更新信息' : '发布信息' }}</span>
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>

    <!-- 成功提示模态框 -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content bubble">
        <div class="modal-header">
          <div class="modal-icon">✅</div>
          <h3 class="modal-title">{{ isEditMode ? '更新成功！' : '发布成功！' }}</h3>
        </div>
        <div class="modal-body">
          <p>{{ isEditMode ? '您的物品信息已成功更新。' : '您的物品信息已成功提交，等待管理员审核。' }}</p>
          <p v-if="!isEditMode">审核通过后将在首页显示。</p>
          <p>您可以在"我的"页面查看审核进度。</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn view-btn" @click="goToDetail">查看详情</button>
          <button class="modal-btn back-btn" @click="goBack">{{ isEditMode ? '返回我的' : '返回首页' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, onBeforeMount, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import Navigation from './navigation.vue'

const router = useRouter()
const route = useRoute()

/* ================= 用户信息 ================= */
const user = ref({
  id: 0,
  username: '',
  realName: '加载中...',
  phone: '',
  role: 0,
  status: 0
})



/* ================= 表单数据 ================= */
const formData = reactive({
  itemCategory: 1, // 1-失物，2-招领
  itemType: 0, // 分类ID
  name: '',
  locationId: 0,
  locationDetail: '',
  pickupLocation: '',
  happenTime: getDefaultDateTime(),
  feature: '',
  rewardAmount: 0,
  rewardDesc: '',
  contactName: '',
  contactPhone: ''
})

// 表单错误信息
const formErrors = reactive({
  itemCategory: '',
  itemType: '',
  name: '',
  locationId: '',
  locationDetail: '',
  pickupLocation: '',
  happenTime: '',
  feature: '',
  rewardAmount: '',
  rewardDesc: '',
  contactName: '',
  contactPhone: '',
  images: ''
})

/* ================= 发布类型选项 ================= */
const publishTypes = [
  {
    value: 1,
    label: '失物',
    desc: '寻找丢失物品',
  },
  {
    value: 2,
    label: '招领',
    desc: '寻找失主',
  }
]

/* ================= 分类选择器 ================= */
const categoryTree = ref<any[]>([])
const selectedFirstCategory = ref<number>(0)
const selectedSecondCategory = ref<number>(0)

const firstCategories = computed(() => {
  return categoryTree.value
})

const secondCategories = computed(() => {
  if (!selectedFirstCategory.value) return []
  const selectedFirst = categoryTree.value.find(cat => cat.id === selectedFirstCategory.value)
  return selectedFirst?.children || []
})

/* ================= 地点选择器 ================= */
const locationTree = ref<any[]>([])
const selectedCampus = ref<number>(0)
const selectedArea = ref<number>(0)
const selectedLocation = ref<number>(0)

const campuses = computed(() => {
  return locationTree.value
})

const areas = computed(() => {
  if (!selectedCampus.value) return []
  const selectedCampusNode = locationTree.value.find(loc => loc.id === selectedCampus.value)
  return selectedCampusNode?.children || []
})

const locations = computed(() => {
  if (!selectedArea.value) return []
  for (const campus of locationTree.value) {
    if (campus.children) {
      const selectedAreaNode = campus.children.find((area: any) => area.id === selectedArea.value)
      if (selectedAreaNode) {
        return selectedAreaNode.children || []
      }
    }
  }
  return []
})

/* ================= 图片上传 ================= */
const fileInput = ref<HTMLInputElement>()
const images = ref<Array<{ 
  file?: File;  // 新上传的文件
  previewUrl: string;  // 图片预览URL
  isOriginal?: boolean; // 是否为原始图片
  originalId?: number; // 原始图片ID
}>>([])
const dragOver = ref(false)
const draggedImageIndex = ref<number | null>(null)

/* ================= 编辑模式状态 ================= */
const isEditMode = ref(false)
const editingItemId = ref<number | null>(null)

/* ================= 表单状态 ================= */
const submitting = ref(false)
const showSuccessModal = ref(false)
const publishedItemId = ref<number | null>(null)

/* ================= 加载状态 ================= */
const loadingData = ref(false)

/* ================= 工具函数 ================= */
function getDefaultDateTime(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const currentDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

/* ================= URL参数解析 ================= */
onBeforeMount(() => {
  // 解析URL参数，判断是否为编辑模式
  const editParam = route.query.edit
  const itemIdParam = route.query.itemId
  
  if (editParam === 'true' && itemIdParam) {
    isEditMode.value = true
    editingItemId.value = parseInt(itemIdParam as string)
    console.log('编辑模式，物品ID:', editingItemId.value)
  }
})

/* ================= 生命周期 ================= */
onMounted(() => {
  loadUser()
  loadCategoryTree()
  loadLocationTree()
  
  // 添加对分类树和地点树加载完成的监听
  watch([() => categoryTree.value.length, () => locationTree.value.length], 
    ([categoryLoaded, locationLoaded]) => {
      console.log('分类树和地点树加载状态:', { categoryLoaded, locationLoaded })
      // 如果是编辑模式且两个树都已加载，则加载物品数据
      if (isEditMode.value && editingItemId.value && categoryLoaded > 0 && locationLoaded > 0) {
        console.log('开始加载物品数据...')
        loadItemData(editingItemId.value)
      }
    },
    { immediate: true }
  )
})

/* ================= 物品数据加载 ================= */
async function loadItemData(itemId: number) {
  if (loadingData.value) return
  
  loadingData.value = true
  console.log('加载物品数据，ID:', itemId)
  
  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: itemId }
    })
    
    console.log('物品详情接口返回:', res.data)
    
    if (res.data.code === 200) {
      const itemData = res.data.data.item || res.data.data
      
      console.log('物品数据:', itemData)
      
      // 等待分类和地点数据加载完成后再填充表单
      await nextTick() // 等待DOM更新
      
      // 填充表单数据
      fillFormData(itemData)
      
      // 加载物品图片
      if (res.data.data.images && res.data.data.images.length > 0) {
        console.log('加载物品图片:', res.data.data.images)
        await loadItemImages(res.data.data.images)
      }
    } else {
      console.error('获取物品详情失败:', res.data.msg)
      alert('加载物品数据失败，请重试')
    }
  } catch (error) {
    console.error('加载物品数据失败:', error)
    alert('加载物品数据失败，请检查网络连接')
  } finally {
    loadingData.value = false
  }
}

/* ================= 表单数据填充 ================= */
function fillFormData(itemData: any) {
  console.log('填充表单数据:', itemData)
  
  // 基础表单数据
  formData.itemCategory = itemData.itemCategory
  formData.itemType = itemData.itemType
  formData.name = itemData.name
  formData.locationId = itemData.locationId
  formData.locationDetail = itemData.locationDetail || ''
  formData.pickupLocation = itemData.pickupLocation || ''
  
  // 格式化时间（兼容datetime-local格式）
  if (itemData.happenTime) {
    let timeStr = itemData.happenTime
    if (timeStr.includes(' ')) {
      timeStr = timeStr.replace(' ', 'T')
    }
    // 确保格式为 YYYY-MM-DDTHH:mm
    if (timeStr.includes(':')) {
      const parts = timeStr.split(':')
      if (parts.length >= 2) {
        timeStr = `${parts[0]}:${parts[1]}`
      }
    }
    formData.happenTime = timeStr.substring(0, 16)
  }
  
  formData.feature = itemData.feature
  formData.rewardAmount = itemData.rewardAmount || 0
  formData.rewardDesc = itemData.rewardDesc || ''
  formData.contactName = itemData.contactName
  formData.contactPhone = itemData.contactPhone
  
  console.log('填充后的表单数据:', formData)
  
  // 设置分类选择器
  setupCategorySelectors(itemData.itemType)
  
  // 设置地点选择器
  setupLocationSelectors(itemData.locationId)
}

/* ================= 分类选择器设置 ================= */
function setupCategorySelectors(itemType: number) {
  console.log('设置分类选择器，itemType:', itemType)
  
  // 等待分类树加载完成后再设置
  if (categoryTree.value.length === 0) {
    console.warn('分类树尚未加载完成')
    return
  }
  
  // 查找对应的分类
  for (const firstCat of categoryTree.value) {
    if (firstCat.children) {
      for (const secondCat of firstCat.children) {
        if (secondCat.id === itemType) {
          console.log('找到分类:', firstCat.id, secondCat.id)
          selectedFirstCategory.value = firstCat.id
          selectedSecondCategory.value = secondCat.id
          formData.itemType = secondCat.id
          return
        }
      }
    }
  }
  
  console.warn('未找到对应的分类:', itemType)
}

/* ================= 地点选择器设置 ================= */
function setupLocationSelectors(locationId: number) {
  console.log('设置地点选择器，locationId:', locationId)
  
  // 等待地点树加载完成后再设置
  if (locationTree.value.length === 0) {
    console.warn('地点树尚未加载完成')
    return
  }
  
  // 查找对应的地点层级
  for (const campus of locationTree.value) {
    if (campus.children) {
      for (const area of campus.children) {
        if (area.children) {
          for (const location of area.children) {
            if (location.id === locationId) {
              console.log('找到地点:', campus.id, area.id, location.id)
              selectedCampus.value = campus.id
              selectedArea.value = area.id
              selectedLocation.value = location.id
              formData.locationId = location.id
              return
            }
          }
        }
      }
    }
  }
  
  console.warn('未找到对应的地点:', locationId)
}

/* ================= 物品图片加载 ================= */
async function loadItemImages(imageList: Array<{ id: number; url: string }>) {
  console.log('加载物品图片:', imageList)
  
  try {
    images.value = [] // 清空当前图片数组
    
    // 对于每个图片，我们直接使用图片的URL作为预览，并保存图片ID
    for (const image of imageList) {
      images.value.push({
        previewUrl: image.url,
        isOriginal: true,
        originalId: image.id
      })
    }
    
    console.log('图片加载完成:', images.value)
  } catch (error) {
    console.error('加载物品图片失败:', error)
  }
}

/* ================= 数据加载 ================= */
async function loadUser() {
  try {
    const res = await axios.get('/api/user/info')
    if (res.data.code === 0) {
      user.value = res.data.data
      // 如果表单中的联系人信息为空，用用户信息填充
      if (!formData.contactName) {
        formData.contactName = user.value.realName
      }
      if (!formData.contactPhone) {
        formData.contactPhone = user.value.phone
      }
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    // 使用模拟数据
    user.value = {
      id: 1,
      username: 'testuser',
      realName: '测试用户',
      phone: '13800138000',
      role: 1,
      status: 1
    }
  }
}

async function loadCategoryTree() {
  try {
    const res = await axios.get('/api/item/category/tree')
    console.log('分类树接口返回:', res.data)
    
    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      categoryTree.value = res.data.data
      console.log('分类树加载完成，数量:', categoryTree.value.length)
    } else {
      console.error('分类树接口返回的数据格式不正确:', res.data)
      // 使用默认数据
      categoryTree.value = [
        {
          id: 1,
          name: '证件',
          children: [
            { id: 101, name: '校园卡' },
            { id: 102, name: '身份证' },
            { id: 103, name: '学生证' },
            { id: 104, name: '银行卡' }
          ]
        },
        {
          id: 2,
          name: '电子设备',
          children: [
            { id: 201, name: '手机' },
            { id: 202, name: '耳机' },
            { id: 203, name: '平板电脑' },
            { id: 204, name: '充电宝' },
            { id: 205, name: '电脑' }
          ]
        },
        {
          id: 3,
          name: '日用品',
          children: [
            { id: 301, name: '水杯' },
            { id: 302, name: '雨伞' },
            { id: 303, name: '衣物' },
            { id: 304, name: '钥匙' }
          ]
        },
        {
          id: 4,
          name: '学习用品',
          children: [
            { id: 401, name: '书本' },
            { id: 402, name: '笔记本' },
            { id: 403, name: '文具' }
          ]
        },
        {
          id: 5,
          name: '其他',
          children: [
            { id: 501, name: '其他物品' }
          ]
        }
      ]
    }
  } catch (error) {
    console.error('加载分类树失败:', error)
    categoryTree.value = []
  }
}

async function loadLocationTree() {
  try {
    const res = await axios.get('/api/item/location/tree')
    console.log('地点树接口返回:', res.data)
    
    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      locationTree.value = res.data.data
      console.log('地点树加载完成，数量:', locationTree.value.length)
    } else {
      console.error('地点树接口返回的数据格式不正确:', res.data)
      // 使用默认数据
      locationTree.value = [
        {
          id: 1,
          name: '朝晖校区',
          children: [
            {
              id: 101,
              name: '教学楼',
              children: [
                { id: 10101, name: '文荟楼' },
                { id: 10102, name: '文萃楼' },
                { id: 10103, name: '文荟楼' }
              ]
            },
            {
              id: 102,
              name: '图书馆',
              children: [
                { id: 10201, name: '朝晖图书馆' }
              ]
            }
          ]
        },
        {
          id: 2,
          name: '屏峰校区',
          children: [
            {
              id: 201,
              name: '教学楼',
              children: [
                { id: 20101, name: '健行楼 A 楼' },
                { id: 20102, name: '健行楼 B 楼' },
                { id: 20103, name: '广知楼' }
              ]
            },
            {
              id: 202,
              name: '图书馆',
              children: [
                { id: 20201, name: '屏峰图书馆' }
              ]
            }
          ]
        }
      ]
    }
  } catch (error) {
    console.error('加载地点树失败:', error)
    locationTree.value = []
  }
}

/* ================= 表单交互 ================= */
function changePublishType(type: number) {
  if (submitting.value) return
  formData.itemCategory = type
  formData.rewardAmount = 0
  formData.rewardDesc = ''
  formData.pickupLocation = ''
  clearFormError('itemCategory')
}

function onFirstCategoryChange() {
  selectedSecondCategory.value = 0
  formData.itemType = 0
  clearFormError('itemType')
}

function onSecondCategoryChange() {
  if (selectedSecondCategory.value) {
    formData.itemType = selectedSecondCategory.value
  }
  clearFormError('itemType')
}

function onCampusChange() {
  selectedArea.value = 0
  selectedLocation.value = 0
  formData.locationId = 0
  clearFormError('locationId')
}

function onAreaChange() {
  selectedLocation.value = 0
  formData.locationId = 0
  clearFormError('locationId')
}

function onLocationChange() {
  if (selectedLocation.value) {
    formData.locationId = selectedLocation.value
  }
  clearFormError('locationId')
}

/* ================= 图片上传处理 ================= */
function triggerFileInput() {
  if (submitting.value) return
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return
  
  handleFiles(Array.from(files))
  target.value = ''
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
  if (submitting.value) return
  dragOver.value = true
}

function handleDragLeave(event: DragEvent) {
  event.preventDefault()
  dragOver.value = false
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  if (submitting.value) return
  dragOver.value = false
  
  const files = event.dataTransfer?.files
  if (files) {
    handleFiles(Array.from(files))
  }
}

function handleFiles(fileList: File[]) {
  const remainingSlots = 5 - images.value.length
  if (remainingSlots <= 0) {
    formErrors.images = '最多只能上传5张图片'
    return
  }
  
  const validFiles = fileList.slice(0, remainingSlots)
  
  validFiles.forEach(file => {
    if (!file.type.startsWith('image/')) {
      formErrors.images = '只能上传图片文件'
      return
    }
    
    if (file.size > 5 * 1024 * 1024) {
      formErrors.images = '图片大小不能超过5MB'
      return
    }
    
    const previewUrl = URL.createObjectURL(file)
    images.value.push({ 
      file: file, 
      previewUrl: previewUrl,
      isOriginal: false
    })
  })
  
  clearFormError('images')
}

function removeImage(index: number) {
  if (submitting.value) return
  
  // 释放新图片的URL
  if (!images.value[index].isOriginal) {
    URL.revokeObjectURL(images.value[index].previewUrl)
  }
  
  images.value.splice(index, 1)
  clearFormError('images')
}

function clearAllImages() {
  if (submitting.value) return
  images.value.forEach(image => {
    // 只释放新上传图片的URL
    if (!image.isOriginal) {
      URL.revokeObjectURL(image.previewUrl)
    }
  })
  images.value = []
  clearFormError('images')
}

function handleDragStart(index: number) {
  if (submitting.value) return
  draggedImageIndex.value = index
}

function handleDropSort(dropIndex: number) {
  if (draggedImageIndex.value === null || draggedImageIndex.value === dropIndex) return
  
  const temp = images.value[draggedImageIndex.value]
  images.value.splice(draggedImageIndex.value, 1)
  images.value.splice(dropIndex, 0, temp)
  
  draggedImageIndex.value = null
}

/* ================= 表单验证 ================= */
function validateForm(): boolean {
  let isValid = true
  
  Object.keys(formErrors).forEach(key => {
    formErrors[key as keyof typeof formErrors] = ''
  })
  
  if (!formData.itemCategory) {
    formErrors.itemCategory = '请选择发布类型'
    isValid = false
  }
  
  if (!formData.itemType) {
    formErrors.itemType = '请选择物品分类'
    isValid = false
  }
  
  if (!formData.name.trim()) {
    formErrors.name = '请输入物品名称'
    isValid = false
  } else if (formData.name.trim().length > 50) {
    formErrors.name = '物品名称不能超过50个字符'
    isValid = false
  }
  
  if (!formData.locationId) {
    formErrors.locationId = '请选择地点'
    isValid = false
  }
  
  if (formData.locationDetail && formData.locationDetail.length > 255) {
    formErrors.locationDetail = '具体位置不能超过255个字符'
    isValid = false
  }
  
  if (!formData.happenTime) {
    formErrors.happenTime = '请选择时间'
    isValid = false
  } else {
    const selectedTime = new Date(formData.happenTime).getTime()
    const now = new Date().getTime()
    if (selectedTime > now) {
      formErrors.happenTime = '时间不能晚于当前时间'
      isValid = false
    }
  }
  
  if (!formData.feature.trim()) {
    formErrors.feature = '请输入特征描述'
    isValid = false
  } else if (formData.feature.trim().length < 2) {
    formErrors.feature = '特征描述至少需要2个字符'
    isValid = false
  } else if (formData.feature.trim().length > 1000) {
    formErrors.feature = '特征描述不能超过1000个字符'
    isValid = false
  }
  
  if (formData.rewardAmount) {
    if (formData.rewardAmount < 0) {
      formErrors.rewardAmount = '悬赏金额不能为负数'
      isValid = false
    } else if (formData.rewardAmount > 999999.99) {
      formErrors.rewardAmount = '悬赏金额不能超过999999.99'
      isValid = false
    }
  }
  
  if (formData.rewardDesc && formData.rewardDesc.length > 200) {
    formErrors.rewardDesc = '悬赏说明不能超过200个字符'
    isValid = false
  }
  
  if (formData.pickupLocation && formData.pickupLocation.length > 255) {
    formErrors.pickupLocation = '领取地点不能超过255个字符'
    isValid = false
  }
  
  if (!formData.contactName.trim()) {
    formErrors.contactName = '请输入联系人姓名'
    isValid = false
  } else if (formData.contactName.trim().length > 20) {
    formErrors.contactName = '联系人姓名不能超过20个字符'
    isValid = false
  }
  
  if (!formData.contactPhone.trim()) {
    formErrors.contactPhone = '请输入联系电话'
    isValid = false
  } else if (!/^1[3-9]\d{9}$/.test(formData.contactPhone.trim())) {
    formErrors.contactPhone = '请输入有效的手机号码'
    isValid = false
  }
  
  return isValid
}

function clearFormError(field: keyof typeof formErrors) {
  formErrors[field] = ''
}

/* ================= 表单提交 ================= */
async function submitForm() {
  if (submitting.value) return
  
  if (!validateForm()) {
    const firstError = Object.keys(formErrors).find(key => formErrors[key as keyof typeof formErrors])
    if (firstError) {
      const errorElement = document.querySelector(`.error-message`)
      errorElement?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    return
  }
  
  submitting.value = true
  
  try {
    const submitData = {
      ...formData,
      happenTime: formatDateTime(formData.happenTime),
      rewardAmount: formData.rewardAmount || 0,
      rewardDesc: formData.rewardDesc || '',
      pickupLocation: formData.pickupLocation || '',
      locationDetail: formData.locationDetail || ''
    }
    
    console.log('提交的数据:', submitData)
    
    let itemId: number
    
    if (isEditMode.value && editingItemId.value) {
      // 编辑模式：调用更新接口
      console.log('调用更新接口，itemId:', editingItemId.value)
      const updateRes = await axios.put(`/api/item/${editingItemId.value}`, submitData)
      
      console.log('更新接口返回:', updateRes.data)
      
      if (updateRes.data.code === 200) {
        itemId = editingItemId.value
        publishedItemId.value = itemId
        
        // 调用图片更新接口（删除所有旧图片，上传所有新图片）
        if (images.value.length > 0) {
          await updateItemImages(itemId)
        } else {
          // 如果没有图片，调用空更新以删除所有旧图片
          await updateItemImagesEmpty(itemId)
        }
        
        showSuccessModal.value = true
      } else {
        throw new Error(updateRes.data.msg || '更新失败')
      }
    } else {
      // 发布模式：调用创建接口
      console.log('调用创建接口')
      const itemRes = await axios.post('/api/item', submitData)
      
      console.log('创建接口返回:', itemRes.data)
      
      if (itemRes.data.code === 200) {
        itemId = itemRes.data.data.itemId
        publishedItemId.value = itemId
        
        if (images.value.length > 0) {
          await uploadImages(itemId)
        }
        
        showSuccessModal.value = true
      } else {
        throw new Error(itemRes.data.msg || '发布失败')
      }
    }
  } catch (error: any) {
    console.error(isEditMode.value ? '更新失败:' : '发布失败:', error)
    alert(`${isEditMode.value ? '更新' : '发布'}失败: ${error.message || '网络错误'}`)
  } finally {
    submitting.value = false
  }
}

function formatDateTime(datetimeLocal: string): string {
  return datetimeLocal.replace('T', ' ')+':00'
}

/* ================= 图片处理函数 ================= */

// 发布模式：上传图片
async function uploadImages(itemId: number) {
  console.log('发布模式：上传图片，itemId:', itemId)
  
  for (let i = 0; i < images.value.length; i++) {
    const image = images.value[i]
    
    // 只上传有file对象的图片
    if (!image.file) {
      console.warn(`图片 ${i} 没有file对象，跳过`)
      continue
    }
    
    try {
      const uploadFormData = new FormData()
      uploadFormData.append('itemId', itemId.toString())
      uploadFormData.append('imageType', formData.itemCategory.toString())
      uploadFormData.append('sort', (i + 1).toString())
      uploadFormData.append('file', image.file)
      
      console.log(`上传图片 ${i + 1}`)
      await axios.post('/api/item/image/upload', uploadFormData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    } catch (error) {
      console.error(`图片${i + 1}上传失败:`, error)
    }
  }
}

// 编辑模式：调用新的图片更新接口
async function updateItemImages(itemId: number) {
  console.log('编辑模式：调用图片更新接口，itemId:', itemId)
  
  try {
    const formData = new FormData()
    
    // 将所有图片添加到formData中
    for (let i = 0; i < images.value.length; i++) {
      const image = images.value[i]
      
      if (image.file) {
        // 新上传的图片，直接添加
        formData.append('images', image.file)
      } else if (image.isOriginal && image.previewUrl) {
        // 原始图片，需要从URL获取并转换为File对象
        try {
          console.log(`处理原始图片: ${image.previewUrl}`)
          const response = await fetch(image.previewUrl)
          if (response.ok) {
            const blob = await response.blob()
            const file = new File([blob], `image_${image.originalId || i}.jpg`, { type: blob.type })
            formData.append('images', file)
          } else {
            console.error(`无法获取原始图片: ${image.previewUrl}`, response.status)
          }
        } catch (error) {
          console.error(`获取原始图片失败 ${i}:`, error)
        }
      }
    }
    
    // 调用图片更新接口
    const response = await axios.post(`/api/item/${itemId}/images/update`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    console.log('图片更新接口返回:', response.data)
    
    if (response.data.code !== 200) {
      throw new Error(response.data.msg || '图片更新失败')
    }
  } catch (error) {
    console.error('图片更新失败:', error)
    throw error
  }
}

// 编辑模式：清空所有图片（当用户删除所有图片时调用）
async function updateItemImagesEmpty(itemId: number) {
  console.log('清空物品的所有图片，itemId:', itemId)
  
  try {
    // 创建一个空的FormData
    const formData = new FormData()
    
    // 调用图片更新接口（没有图片，会删除所有旧图片）
    const response = await axios.post(`/api/item/${itemId}/images/update`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    console.log('清空图片接口返回:', response.data)
    
    if (response.data.code !== 200) {
      throw new Error(response.data.msg || '清空图片失败')
    }
  } catch (error) {
    console.error('清空图片失败:', error)
    throw error
  }
}

/* ================= 导航操作 ================= */
function goBack() {
  if (isEditMode.value) {
    // 编辑模式下返回"我的"页面
    router.push('/my-posts')
  } else {
    router.push('/')
  }
}

// 退出登录处理
const handleLogout = async () => {
  try {
    const userId = user.value.id
    if (userId) {
      await axios.post('/api/user/logout', { userId })
    }
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    localStorage.clear()
    router.push('/login')
  }
}

function goToDetail() {
  if (publishedItemId.value) {
    router.push(`/item/detail?itemId=${publishedItemId.value}`)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
/* 基础布局 */
.publish-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
}

/* 背景容器 */
.background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

/* 纯色背景层 */
.solid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #f8f3d4;
  pointer-events: none;
}

/* 整体布局：左侧导航 + 右侧主内容 */
.layout-container {
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 100vh;
  display: flex;
}

/* ================= 左侧导航栏 ================= */
.left-nav {
  width: 288px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: transparent;
  padding: 24px;
  display: flex;
  flex-direction: column;
  z-index: 10;
  box-sizing: border-box;
}

.user-info-container {
  border-radius: 12.8px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-container {
  position: relative;
  width: 48px;
  height: 48px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-border {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border: 2px solid rgba(243, 129, 129, 0.5);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.user-text {
  display: flex;
  flex-direction: column;
}

.user-nickname {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 20px;
  font-weight: 600;
  color: #a67c52;
  margin-bottom: 6.4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 192px;
}

.user-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 17.6px;
  color: rgba(166, 124, 82, 0.7);
}

.nav-top-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.left-nav-btn {
  background: transparent;
  border: none;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 16px;
  cursor: pointer;
  padding: 14.4px 10px;
  border-radius: 12.8px;
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  color: #a67c52;
  font-size: 16px;
  font-weight: 500;
  width: 100%;
  text-align: left;
}

.left-nav-btn.active {
  background: rgba(243, 129, 129, 0.15);
  font-weight: 600;
}

.left-nav-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.left-nav-btn .nav-icon {
  font-size: 25.6px;
  min-width: 32px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-svg {
  width: 25.6px;
  height: 25.6px;
  object-fit: contain;
  filter: brightness(0.8);
}

.left-nav-btn .nav-text {
  font-size: 20px;
}

/* 左侧中间：发布提示 */
.left-notice-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 14.4px;
  padding: 16px;
  margin: 15px 0;
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  display: flex;
  flex-direction: column;
  width: 85%;
  max-height: 300px;
  min-height: 120px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(166, 124, 82, 0.15) transparent;
  box-sizing: border-box;
}

.left-notice-card .notice-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin-bottom: 10px;
  font-weight: 600;
  text-align: center;
  flex-shrink: 0;
}

.left-notice-card .notice-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.5;
  text-align: left;
  margin-bottom: 10px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 5px;
  word-wrap: break-word;
}

.left-notice-card .notice-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  text-align: right;
  flex-shrink: 0;
  margin-top: 5px;
}

/* 左侧下半区：操作按钮组 */
.nav-bottom-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.left-action-btn {
  height: 54.4px;
  padding: 0 25.6px;
  border-radius: 12.8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border: 1.6px solid transparent;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  color: white;
  width: 100%;
}

.left-action-btn:hover {
  transform: translateX(5px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.back-btn {
  background: linear-gradient(to right, #a67c52, #8b6b3c);
}

.logout-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  width: 75%;
}

/* ================= 右侧主内容区 ================= */
.main-content {
  flex: 1;
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

/* 发布表单卡片 */
.publish-form-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 40px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  max-width: 1400px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 40px;
  text-align: center;
}

.form-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 32px;
  color: #a67c52;
  margin-bottom: 10px;
  font-weight: 700;
}

.form-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: rgba(166, 124, 82, 0.7);
}

/* 表单内容 - 优化双栏布局 */
.form-content {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
}

/* 左右两栏基本样式 */
.form-left-column,
.form-right-column {
  flex: 1;
  min-width: 450px;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* 水平分组容器 */
.horizontal-group {
  display: flex;
  gap: 20px;
  width: 100%;
}

.horizontal-group .compact-section {
  flex: 1;
  min-width: 0; /* 防止子元素溢出 */
}

/* 表单部分通用样式 */
.form-section {
  border-radius: 12px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(166, 124, 82, 0.1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.form-section:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.25);
}

.compact-section {
  padding: 18px;
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.section-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
}

.required-mark {
  color: #ff4d4f;
  font-size: 18px;
}

.optional-mark {
  color: rgba(166, 124, 82, 0.5);
  font-size: 14px;
  font-style: italic;
  white-space: nowrap;
}

.form-row {
  margin-bottom: 12px;
}

.form-row:last-child {
  margin-bottom: 0;
}

/* 发布类型选项 - 水平布局 */
.horizontal-options {
  display: flex;
  gap: 15px;
  width: 100%;
}

.horizontal-option {
  flex: 1;
  padding: 18px 15px;
  border: 2px solid rgba(166, 124, 82, 0.3);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 100px;
}

.horizontal-option:hover:not(.active):not(.disabled) {
  border-color: rgba(243, 129, 129, 0.5);
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.horizontal-option.active {
  border-color: #f38181;
  background: linear-gradient(135deg, rgba(243, 129, 129, 0.1), rgba(247, 125, 95, 0.1));
  box-shadow: 0 4px 20px rgba(243, 129, 129, 0.2);
}

.horizontal-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.type-icon {
  font-size: 28px;
  margin-bottom: 5px;
}

.type-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  color: #a67c52;
}

.type-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  text-align: center;
  line-height: 1.3;
}

/* 紧凑型级联选择器 */
.compact-cascader {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.location-cascader {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.compact-level {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.compact-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.compact-select {
  width: 100%;
  padding: 10px 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
  min-height: 42px;
  box-sizing: border-box;
}

.compact-select:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

.compact-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 紧凑型输入框 */
.compact-input {
  width: 100%;
  padding: 10px 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  transition: all 0.3s ease;
  outline: none;
  min-height: 42px;
  box-sizing: border-box;
}

.compact-input::placeholder {
  color: rgba(166, 124, 82, 0.5);
  font-size: 13px;
}

.compact-input:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

.compact-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.compact-input.error {
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.05);
}

.datetime-input {
  width: 100%;
  font-size: 14px;
}

/* 文本域 */
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  transition: all 0.3s ease;
  outline: none;
  resize: vertical;
  min-height: 160px;
  box-sizing: border-box;
}

.form-textarea::placeholder {
  color: rgba(166, 124, 82, 0.5);
}

.form-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

.form-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-textarea.error {
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.05);
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.char-counter {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.6);
  font-style: italic;
}

/* 悬赏金额输入 */
.currency-input {
  position: relative;
}

.currency-symbol {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 500;
}

.reward-input {
  padding-left: 28px;
}

/* 紧凑型图片上传 */
.compact-uploader {
  position: relative;
}

.compact-upload-area {
  border: 2px dashed rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  padding: 25px 15px;
  background: rgba(255, 255, 255, 0.2);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 15px;
}

.compact-upload-area:hover:not(.disabled) {
  border-color: rgba(243, 129, 129, 0.6);
  background: rgba(255, 255, 255, 0.3);
}

.compact-upload-area.drag-over {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.compact-upload-area.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.compact-upload-area .upload-icon {
  margin-bottom: 10px;
}

.compact-upload-area .upload-svg {
  width: 40px;
  height: 40px;
  object-fit: contain;
  filter: brightness(0.8);
}

.compact-upload-area .upload-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  margin-bottom: 6px;
  font-weight: 500;
}

.compact-upload-area .upload-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.6);
  margin: 3px 0;
}

.file-input {
  display: none;
}

/* 紧凑型图片预览 */
.compact-preview {
  margin-top: 15px;
}

.compact-preview .preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.compact-preview .preview-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 500;
}

.clear-all-btn {
  padding: 5px 10px;
  border-radius: 6px;
  background: rgba(166, 124, 82, 0.1);
  border: 1px solid rgba(166, 124, 82, 0.3);
  color: #a67c52;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-all-btn:hover:not(:disabled) {
  background: rgba(166, 124, 82, 0.2);
  border-color: rgba(166, 124, 82, 0.5);
}

.clear-all-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.grid-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  cursor: move;
}

.grid-item:hover .grid-overlay {
  opacity: 1;
}

.grid-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.grid-delete-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: none;
  background: #ff4d4f;
  color: white;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.grid-delete-btn:hover:not(:disabled) {
  background: #ff7875;
  transform: scale(1.1);
}

.grid-delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.grid-sort {
  position: absolute;
  top: 5px;
  left: 5px;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: move;
}

.grid-index {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(243, 129, 129, 0.8);
  color: white;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

/* 联系人信息紧凑布局 */
.compact-contact {
  display: flex;
  gap: 12px;
  width: 100%;
}

.contact-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

/* 错误信息 */
.error-message {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #ff4d4f;
  margin-top: 6px;
  line-height: 1.3;
}

/* 表单操作按钮 */
.form-actions {
  flex: 1 0 100%;
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  margin-top: 20px;
  padding-top: 25px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.action-btn {
  padding: 14px 40px;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 140px;
}

.cancel-btn {
  background: transparent;
  border: 2px solid rgba(166, 124, 82, 0.4);
  color: #a67c52;
}

.cancel-btn:hover:not(:disabled) {
  border-color: rgba(166, 124, 82, 0.7);
  background: rgba(166, 124, 82, 0.1);
}

.submit-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(247, 125, 95, 0.4);
  background: linear-gradient(to right, #f77d5f, #f38181);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn.submitting {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 10px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 成功提示模态框 */
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
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 40px;
  max-width: 500px;
  width: 90%;
  text-align: center;
  border: 2px solid rgba(166, 124, 82, 0.2);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  margin-bottom: 25px;
}

.modal-icon {
  font-size: 64px;
  margin-bottom: 15px;
}

.modal-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 28px;
  color: #a67c52;
  margin: 0;
  font-weight: 700;
}

.modal-body {
  margin-bottom: 30px;
}

.modal-body p {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.8);
  line-height: 1.6;
  margin: 10px 0;
}

.modal-footer {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.modal-btn {
  padding: 12px 30px;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  min-width: 120px;
}

.view-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.view-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(247, 125, 95, 0.3);
}

.back-btn {
  background: rgba(166, 124, 82, 0.1);
  border: 2px solid rgba(166, 124, 82, 0.4);
  color: #a67c52;
}

.back-btn:hover {
  border-color: rgba(166, 124, 82, 0.7);
  background: rgba(166, 124, 82, 0.2);
}

/* ================= 响应式设计 ================= */

/* 大屏幕适配（1400px以上） */
@media (min-width: 1401px) {
  .publish-form-card {
    max-width: 1600px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 500px;
  }
  
  .location-cascader {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .image-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

/* 中等屏幕适配（992px-1400px） */
@media (min-width: 992px) and (max-width: 1400px) {
  .main-content {
    margin-left: 260px;
    max-width: calc(100vw - 260px);
    padding: 20px;
  }
  
  .publish-form-card {
    padding: 30px;
    max-width: 1200px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 400px;
  }
  
  .location-cascader {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .image-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 平板端适配（769px-991px） */
@media (min-width: 769px) and (max-width: 991px) {
  .left-nav {
    width: 240px;
  }
  
  .main-content {
    margin-left: 240px;
    max-width: calc(100vw - 240px);
    padding: 15px;
  }
  
  .publish-form-card {
    padding: 25px;
    max-width: 100%;
  }
  
  .form-content {
    flex-direction: column;
    gap: 25px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 100%;
  }
  
  .horizontal-group {
    flex-wrap: wrap;
  }
  
  .horizontal-group .compact-section {
    flex: 1 0 calc(50% - 10px);
  }
  
  .location-cascader {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .image-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .compact-contact {
    flex-direction: column;
    gap: 15px;
  }
}

/* 移动端（768px以下） */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  /* 左侧导航移至底部 */
  .left-nav {
    width: 100%;
    height: auto;
    position: fixed;
    bottom: 0;
    left: 0;
    top: auto;
    border-right: none;
    border-top: 2px solid rgba(166, 124, 82, 0.2);
    padding: 10px 15px;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    gap: 0;
    z-index: 100;
  }

  /* 移动端隐藏用户信息、公告栏 */
  .user-info-container,
  .left-notice-card {
    display: none;
  }

  /* 导航组调整为横向 */
  .nav-top-group {
    flex-direction: row;
    flex: 1;
    margin-top: 0;
    justify-content: space-around;
  }

  .left-nav-btn {
    flex-direction: column;
    padding: 10px 5px;
    gap: 4px;
    width: auto;
    min-width: 60px;
  }

  .left-nav-btn .nav-icon {
    font-size: 22px;
    min-width: auto;
  }
  
  .left-nav-btn .nav-svg {
    width: 22px;
    height: 22px;
  }

  .left-nav-btn .nav-text {
    font-size: 10px;
    text-align: center;
  }

  /* 底部操作按钮组 */
  .nav-bottom-group {
    flex-direction: row;
    margin-top: 0;
    margin-left: 10px;
  }

  .left-action-btn {
    height: 40px;
    padding: 0 15px;
    font-size: 14px;
    min-width: 80px;
  }

  /* 右侧主内容区 */
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 90px;
  }
  
  .publish-form-card {
    padding: 20px;
  }
  
  .form-title {
    font-size: 24px;
  }
  
  .form-subtitle {
    font-size: 16px;
  }
  
  /* 移动端改为单栏布局 */
  .form-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .form-left-column,
  .form-right-column {
    min-width: 100%;
  }
  
  .form-section {
    padding: 18px;
  }
  
  .compact-section {
    padding: 16px;
  }
  
  .section-title {
    font-size: 16px;
  }
  
  /* 水平选项组 */
  .horizontal-group {
    flex-direction: column;
    gap: 15px;
  }
  
  .horizontal-group .compact-section {
    flex: 1 0 100%;
  }
  
  .horizontal-options {
    flex-direction: column;
  }
  
  .horizontal-option {
    min-height: 80px;
  }
  
  /* 级联选择器 */
  .compact-cascader {
    flex-direction: column;
    gap: 15px;
  }
  
  .location-cascader {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .compact-select,
  .compact-input {
    font-size: 14px;
    padding: 10px 12px;
    min-height: 44px;
  }
  
  /* 文本域 */
  .form-textarea {
    min-height: 140px;
    font-size: 14px;
  }
  
  /* 图片网格 */
  .image-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  /* 联系人布局 */
  .compact-contact {
    flex-direction: column;
    gap: 15px;
  }
  
  /* 表单操作按钮 */
  .form-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .action-btn {
    width: 100%;
    padding: 12px 20px;
    font-size: 16px;
  }
  
  /* 模态框 */
  .modal-content {
    padding: 25px 20px;
    width: 95%;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-btn {
    width: 100%;
  }
}

/* 小屏幕手机（480px以下） */
@media (max-width: 480px) {
  .main-content {
    padding: 15px 10px;
    padding-bottom: 80px;
  }
  
  .publish-form-card {
    padding: 15px;
  }
  
  .form-header {
    margin-bottom: 25px;
  }
  
  .form-title {
    font-size: 20px;
  }
  
  .form-subtitle {
    font-size: 14px;
  }
  
  .form-content {
    gap: 15px;
  }
  
  .form-section {
    padding: 15px;
  }
  
  .compact-section {
    padding: 12px;
  }
  
  .section-title {
    font-size: 15px;
  }
  
  .horizontal-option {
    padding: 15px 10px;
    min-height: 70px;
  }
  
  .type-icon {
    font-size: 24px;
  }
  
  .type-label {
    font-size: 14px;
  }
  
  .type-desc {
    font-size: 12px;
  }
  
  .compact-upload-area {
    padding: 20px 10px;
  }
  
  .image-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .grid-item {
    aspect-ratio: 1;
  }
  
  .form-actions {
    margin-top: 15px;
    padding-top: 20px;
  }
}
</style>