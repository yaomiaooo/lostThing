<template>
  <div class="publish-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局：左侧导航 + 右侧主内容 -->
    <div class="layout-container">
      <!-- 左侧导航栏 -->
      <aside class="left-nav">
        <!-- 用户信息区域 -->
        <div class="user-info-container">
          <div class="user-avatar-container">
            <img class="user-avatar" src="/home/avatar.png" />
            <div class="user-avatar-border"></div>
          </div>
          <div class="user-text">
            <div class="user-nickname">{{ user.realName }}</div>
            <div class="user-subtitle">发布物品</div>
          </div>
        </div>

        <!-- 左侧上半区：核心导航 -->
        <div class="nav-top-group">
          <button 
            v-for="nav in navItems" 
            :key="nav.name"
            class="left-nav-btn"
            :class="{ active: nav.active }"
            @click="nav.handler"
          >
            <span class="nav-icon">
              <img :src="nav.icon" :alt="nav.name" class="nav-svg" />
            </span>
            <span class="nav-text">{{ nav.name }}</span>
          </button>
        </div>

        <!-- 左侧中间：发布提示 -->
        <div class="left-notice-card bubble">
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
        </div>

        <!-- 左侧下半区：操作按钮 -->
        <div class="nav-bottom-group">
          <button 
            class="left-action-btn logout-btn"
            @click="logout"
          >
            <span class="btn-text">退出登录</span>
          </button>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 发布表单卡片 -->
        <div class="publish-form-card bubble">
          <div class="form-header">
            <h2 class="form-title">发布物品信息</h2>
            <div class="form-subtitle">请仔细填写以下信息，确保准确无误</div>
          </div>

          <!-- 表单内容 -->
          <form @submit.prevent="submitForm" class="form-content">
            <!-- 发布类型 -->
            <div class="form-section">
              <div class="section-header">
                <h3 class="section-title">发布类型</h3>
                <span class="required-mark">*</span>
              </div>
              <div class="form-row">
                <div class="type-options">
                  <button
                    v-for="type in publishTypes"
                    :key="type.value"
                    type="button"
                    class="type-option"
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

            <!-- 物品分类 -->
            <div class="form-section">
            <div class="section-header">
                <h3 class="section-title">物品分类</h3>
                <span class="required-mark">*</span>
            </div>
            <div class="form-row">
                <div class="cascader-group">
                <!-- 一级分类 -->
                <div class="cascader-level">
                    <label class="cascader-label">一级分类</label>
                    <select 
                    v-model="selectedFirstCategory"
                    class="cascader-select"
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
                <div class="cascader-level">
                    <label class="cascader-label">二级分类</label>
                    <select 
                    v-model="selectedSecondCategory"
                    class="cascader-select"
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
            <div class="form-section">
              <div class="section-header">
                <h3 class="section-title">物品名称</h3>
                <span class="required-mark">*</span>
              </div>
              <div class="form-row">
                <input
                  v-model="formData.name"
                  type="text"
                  class="form-input"
                  :class="{ error: formErrors.name }"
                  placeholder="请输入物品名称，如：黑色蓝牙耳机"
                  :disabled="submitting"
                  maxlength="50"
                />
                <div v-if="formErrors.name" class="error-message">
                  {{ formErrors.name }}
                </div>
                <div class="input-hint">不超过50个字符</div>
              </div>
            </div>

            <!-- 地点信息 -->
            <div class="form-section">
              <div class="section-header">
                <h3 class="section-title">地点信息</h3>
                <span class="required-mark">*</span>
              </div>
              <div class="form-row">
                <div class="cascader-group">
                  <!-- 校区 -->
                  <div class="cascader-level">
                    <label class="cascader-label">校区</label>
                    <select 
                      v-model="selectedCampus"
                      class="cascader-select"
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
                  <div class="cascader-level">
                    <label class="cascader-label">区域</label>
                    <select 
                      v-model="selectedArea"
                      class="cascader-select"
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
                  <div class="cascader-level">
                    <label class="cascader-label">具体地点</label>
                    <select 
                      v-model="selectedLocation"
                      class="cascader-select"
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
                <div class="form-row">
                  <label class="form-label">具体位置补充</label>
                  <input
                    v-model="formData.locationDetail"
                    type="text"
                    class="form-input"
                    :class="{ error: formErrors.locationDetail }"
                    placeholder="如：三楼自习区、操场跑道内侧、A楼门口"
                    :disabled="submitting"
                    maxlength="255"
                  />
                  <div v-if="formErrors.locationDetail" class="error-message">
                    {{ formErrors.locationDetail }}
                  </div>
                  <div class="input-hint">补充具体位置信息，不超过255个字符</div>
                </div>
              </div>
            </div>

            <!-- 时间信息 -->
            <div class="form-section">
              <div class="section-header">
                <h3 class="section-title">{{ formData.itemCategory === 1 ? '丢失时间' : '发现时间' }}</h3>
                <span class="required-mark">*</span>
              </div>
              <div class="form-row">
                <input
                  v-model="formData.happenTime"
                  type="datetime-local"
                  class="form-input datetime-input"
                  :class="{ error: formErrors.happenTime }"
                  :disabled="submitting"
                />
                <div v-if="formErrors.happenTime" class="error-message">
                  {{ formErrors.happenTime }}
                </div>
              </div>
            </div>

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
                  rows="4"
                  maxlength="1000"
                ></textarea>
                <div v-if="formErrors.feature" class="error-message">
                  {{ formErrors.feature }}
                </div>
                <div class="input-hint">请详细描述，不少于2个字符，不超过1000字符</div>
              </div>
            </div>

            <!-- 图片上传 -->
            <div class="form-section">
              <div class="section-header">
                <h3 class="section-title">上传图片</h3>
                <span class="optional-mark">（可选）</span>
              </div>
              <div class="form-row">
                <div class="image-uploader">
                  <!-- 上传区域 -->
                  <div 
                    class="upload-area"
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
                    <p class="upload-hint">最多5张，每张不超过5MB</p>
                    <p class="upload-hint">支持 JPG、PNG 格式</p>
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
                  <div v-if="images.length > 0" class="image-preview-container">
                    <div class="preview-header">
                      <span class="preview-title">已上传图片（{{ images.length }}/5）</span>
                      <span class="preview-hint">拖动图片可调整顺序</span>
                    </div>
                    <div class="image-preview">
                      <div 
                        v-for="(image, index) in images"
                        :key="index"
                        class="preview-item"
                        draggable="true"
                        @dragstart="handleDragStart(index)"
                        @dragover.prevent
                        @drop="handleDropSort(index)"
                      >
                        <img :src="image.previewUrl" class="preview-image" />
                        <div class="preview-overlay">
                          <button 
                            type="button"
                            class="delete-btn"
                            @click.stop="removeImage(index)"
                            :disabled="submitting"
                          >
                            ×
                          </button>
                          <div class="sort-handle" title="拖动排序">≡</div>
                        </div>
                        <div class="preview-index">{{ index + 1 }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="formErrors.images" class="error-message">
                  {{ formErrors.images }}
                </div>
              </div>
            </div>

            <!-- 悬赏信息（仅失物） -->
            <div v-if="formData.itemCategory === 1" class="form-section">
              <div class="section-header">
                <h3 class="section-title">悬赏信息</h3>
                <span class="optional-mark">（可选）</span>
              </div>
              <div class="form-row">
                <div class="reward-group">
                  <div class="reward-input-group">
                    <label class="reward-label">悬赏金额</label>
                    <div class="reward-amount-input">
                      <span class="currency-symbol">¥</span>
                      <input
                        v-model="formData.rewardAmount"
                        type="number"
                        class="form-input reward-input"
                        :class="{ error: formErrors.rewardAmount }"
                        placeholder="0.00"
                        :disabled="submitting"
                        min="0"
                        max="999999.99"
                        step="0.01"
                      />
                    </div>
                    <div class="input-hint">单位：元，可不填</div>
                  </div>
                  
                  <div class="reward-input-group">
                    <label class="reward-label">悬赏说明</label>
                    <input
                      v-model="formData.rewardDesc"
                      type="text"
                      class="form-input"
                      :class="{ error: formErrors.rewardDesc }"
                      placeholder="如：找到必有重谢、提供线索也有奖励"
                      :disabled="submitting"
                      maxlength="200"
                    />
                    <div class="input-hint">不超过200个字符</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 领取地点（仅招领） -->
            <div v-if="formData.itemCategory === 2" class="form-section">
              <div class="section-header">
                <h3 class="section-title">领取地点说明</h3>
                <span class="optional-mark">（可选）</span>
              </div>
              <div class="form-row">
                <input
                  v-model="formData.pickupLocation"
                  type="text"
                  class="form-input"
                  :class="{ error: formErrors.pickupLocation }"
                  placeholder="如：保卫处值班室、宿管办公室、图书馆服务台"
                  :disabled="submitting"
                  maxlength="255"
                />
                <div v-if="formErrors.pickupLocation" class="error-message">
                  {{ formErrors.pickupLocation }}
                </div>
                <div class="input-hint">告知失主在哪里领取物品</div>
              </div>
            </div>

            <!-- 联系人信息 -->
            <div class="form-section">
              <div class="section-header">
                <h3 class="section-title">联系人信息</h3>
                <span class="required-mark">*</span>
              </div>
              <div class="form-row">
                <div class="contact-group">
                  <div class="contact-input-group">
                    <label class="contact-label">联系人姓名</label>
                    <input
                      v-model="formData.contactName"
                      type="text"
                      class="form-input"
                      :class="{ error: formErrors.contactName }"
                      :disabled="submitting"
                      maxlength="20"
                    />
                    <div v-if="formErrors.contactName" class="error-message">
                      {{ formErrors.contactName }}
                    </div>
                  </div>
                  
                  <div class="contact-input-group">
                    <label class="contact-label">联系电话</label>
                    <input
                      v-model="formData.contactPhone"
                      type="tel"
                      class="form-input"
                      :class="{ error: formErrors.contactPhone }"
                      :disabled="submitting"
                      placeholder="11位手机号码"
                      maxlength="11"
                    />
                    <div v-if="formErrors.contactPhone" class="error-message">
                      {{ formErrors.contactPhone }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 表单操作按钮 -->
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
                  提交中...
                </span>
                <span v-else>发布信息</span>
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
          <h3 class="modal-title">发布成功！</h3>
        </div>
        <div class="modal-body">
          <p>您的物品信息已成功提交，等待管理员审核。</p>
          <p>审核通过后将在首页显示。</p>
          <p>您可以在"我的"页面查看审核进度。</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn view-btn" @click="goToDetail">查看详情</button>
          <button class="modal-btn back-btn" @click="goBack">返回首页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import type { AxiosProgressEvent } from 'axios'

const router = useRouter()

/* ================= 用户信息 ================= */
const user = ref({
  id: 0,
  username: '',
  realName: '加载中...',
  phone: '',
  role: 0,
  status: 0
})

/* ================= 导航栏 ================= */
const navItems = reactive([
  {
    name: '发现',
    icon: '/home/发现.svg',
    active: false,
    handler: () => router.push('/')
  },
  {
    name: '发布',
    icon: '/home/发布.svg',
    active: true,
    handler: () => {}
  },
  {
    name: '消息',
    icon: '/home/消息.svg',
    active: false,
    handler: () => router.push('/messages')
  },
  {
    name: '我的',
    icon: '/home/我的.svg',
    active: false,
    handler: () => router.push('/my-posts')
  },
  {
    name: '设置',
    icon: '/home/设置.svg',
    active: false,
    handler: () => router.push('/settings')
  }
])

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
const categoryTree = ref<any[]>([]) // 存储原始的树形结构
const selectedFirstCategory = ref<number>(0)
const selectedSecondCategory = ref<number>(0)

// 计算一级分类（直接取根节点）
const firstCategories = computed(() => {
  return categoryTree.value
})

// 计算二级分类（根据选择的一级分类，取它的children）
const secondCategories = computed(() => {
  if (!selectedFirstCategory.value) return []
  const selectedFirst = categoryTree.value.find(cat => cat.id === selectedFirstCategory.value)
  return selectedFirst?.children || []
})

/* ================= 地点选择器 ================= */
const locationTree = ref<any[]>([]) // 存储原始的树形结构
const selectedCampus = ref<number>(0)
const selectedArea = ref<number>(0)
const selectedLocation = ref<number>(0)

// 计算校区（直接取根节点）
const campuses = computed(() => {
  return locationTree.value
})

// 计算区域（根据选择的校区，取它的children）
const areas = computed(() => {
  if (!selectedCampus.value) return []
  const selectedCampusNode = locationTree.value.find(loc => loc.id === selectedCampus.value)
  return selectedCampusNode?.children || []
})

// 计算具体地点（根据选择的区域，取它的children）
const locations = computed(() => {
  if (!selectedArea.value) return []
  // 在所有校区中查找选择的区域
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
const images = ref<Array<{ file: File; previewUrl: string }>>([])
const dragOver = ref(false)
const draggedImageIndex = ref<number | null>(null)

/* ================= 表单状态 ================= */
const submitting = ref(false)
const showSuccessModal = ref(false)
const publishedItemId = ref<number | null>(null)

/* ================= 工具函数 ================= */
function getDefaultDateTime(): string {
  const now = new Date()
  // 格式化为 YYYY-MM-DDTHH:mm
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

/* ================= 生命周期 ================= */
onMounted(() => {
  loadUser()
  loadCategoryTree()
  loadLocationTree()
})

/* ================= 数据加载 ================= */
async function loadUser() {
  try {
    const res = await axios.get('/api/user/info')
    if (res.data.code === 0) {
      user.value = res.data.data
      // 自动填充联系人信息
      formData.contactName = user.value.realName
      formData.contactPhone = user.value.phone
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    // 不设置模拟数据，保持为空
  }
}

async function loadCategoryTree() {
  try {
    const res = await axios.get('/api/item/category/tree')
    console.log('分类树接口返回:', res.data)
    
    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      categoryTree.value = res.data.data
      console.log('分类树加载成功:', categoryTree.value)
    } else {
      console.error('分类树接口返回的数据格式不正确')
      categoryTree.value = []
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
      console.log('地点树加载成功:', locationTree.value)
    } else {
      console.error('地点树接口返回的数据格式不正确')
      locationTree.value = []
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
  // 重置一些字段
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
  target.value = '' // 重置input
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
  // 检查数量限制
  const remainingSlots = 5 - images.value.length
  if (remainingSlots <= 0) {
    formErrors.images = '最多只能上传5张图片'
    return
  }
  
  const validFiles = fileList.slice(0, remainingSlots)
  
  validFiles.forEach(file => {
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      formErrors.images = '只能上传图片文件'
      return
    }
    
    // 检查文件大小（5MB）
    if (file.size > 5 * 1024 * 1024) {
      formErrors.images = '图片大小不能超过5MB'
      return
    }
    
    // 创建预览URL
    const previewUrl = URL.createObjectURL(file)
    images.value.push({ file, previewUrl })
  })
  
  clearFormError('images')
}

function removeImage(index: number) {
  if (submitting.value) return
  // 释放预览URL
  URL.revokeObjectURL(images.value[index].previewUrl)
  images.value.splice(index, 1)
  clearFormError('images')
}

function handleDragStart(index: number) {
  if (submitting.value) return
  draggedImageIndex.value = index
}

function handleDropSort(dropIndex: number) {
  if (draggedImageIndex.value === null || draggedImageIndex.value === dropIndex) return
  
  // 交换图片位置
  const temp = images.value[draggedImageIndex.value]
  images.value.splice(draggedImageIndex.value, 1)
  images.value.splice(dropIndex, 0, temp)
  
  draggedImageIndex.value = null
}

/* ================= 表单验证 ================= */
function validateForm(): boolean {
  let isValid = true
  
  // 清空所有错误信息
  Object.keys(formErrors).forEach(key => {
    formErrors[key as keyof typeof formErrors] = ''
  })
  
  // 验证发布类型
  if (!formData.itemCategory) {
    formErrors.itemCategory = '请选择发布类型'
    isValid = false
  }
  
  // 验证物品分类
  if (!formData.itemType) {
    formErrors.itemType = '请选择物品分类'
    isValid = false
  }
  
  // 验证物品名称
  if (!formData.name.trim()) {
    formErrors.name = '请输入物品名称'
    isValid = false
  } else if (formData.name.trim().length > 50) {
    formErrors.name = '物品名称不能超过50个字符'
    isValid = false
  }
  
  // 验证地点
  if (!formData.locationId) {
    formErrors.locationId = '请选择地点'
    isValid = false
  }
  
  if (formData.locationDetail && formData.locationDetail.length > 255) {
    formErrors.locationDetail = '具体位置不能超过255个字符'
    isValid = false
  }
  
  // 验证时间
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
  
  // 验证特征描述
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
  
  // 验证悬赏金额
  if (formData.rewardAmount) {
    if (formData.rewardAmount < 0) {
      formErrors.rewardAmount = '悬赏金额不能为负数'
      isValid = false
    } else if (formData.rewardAmount > 999999.99) {
      formErrors.rewardAmount = '悬赏金额不能超过999999.99'
      isValid = false
    }
  }
  
  // 验证悬赏说明
  if (formData.rewardDesc && formData.rewardDesc.length > 200) {
    formErrors.rewardDesc = '悬赏说明不能超过200个字符'
    isValid = false
  }
  
  // 验证领取地点
  if (formData.pickupLocation && formData.pickupLocation.length > 255) {
    formErrors.pickupLocation = '领取地点不能超过255个字符'
    isValid = false
  }
  
  // 验证联系人姓名
  if (!formData.contactName.trim()) {
    formErrors.contactName = '请输入联系人姓名'
    isValid = false
  } else if (formData.contactName.trim().length > 20) {
    formErrors.contactName = '联系人姓名不能超过20个字符'
    isValid = false
  }
  
  // 验证联系电话
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
  
  // 验证表单
  if (!validateForm()) {
    // 滚动到第一个错误位置
    const firstError = Object.keys(formErrors).find(key => formErrors[key as keyof typeof formErrors])
    if (firstError) {
      const errorElement = document.querySelector(`.error-message`)
      errorElement?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    return
  }
  
  submitting.value = true
  
  try {
    // 准备提交数据
    const submitData = {
      ...formData,
      happenTime: formatDateTime(formData.happenTime),
      rewardAmount: formData.rewardAmount || 0,
      rewardDesc: formData.rewardDesc || '',
      pickupLocation: formData.pickupLocation || '',
      locationDetail: formData.locationDetail || ''
    }
    
    // 第一步：发布物品信息
    console.log('提交物品信息:', submitData)
    const itemRes = await axios.post('/api/item', submitData)
    
    if (itemRes.data.code === 200) {
      const itemId = itemRes.data.data.itemId
      publishedItemId.value = itemId
      
      // 第二步：如果有图片，上传图片
      if (images.value.length > 0) {
        await uploadImages(itemId)
      }
      
      // 显示成功提示
      showSuccessModal.value = true
    } else {
      throw new Error(itemRes.data.msg || '发布失败')
    }
  } catch (error: any) {
    console.error('发布失败:', error)
    alert(`发布失败: ${error.message || '网络错误'}`)
  } finally {
    submitting.value = false
  }
}

function formatDateTime(datetimeLocal: string): string {
  // 将 YYYY-MM-DDTHH:mm 格式转换为 YYYY-MM-DD HH:mm:00
  return datetimeLocal.replace('T', ' ') + ':00'
}

/* ================= 图片上传 ================= */
async function uploadImages(itemId: number) {
  const uploadPromises = images.value.map(async (image, index) => {
    // 使用 uploadFormData 作为变量名，避免与组件中的 formData 冲突
    const uploadFormData = new FormData()
    uploadFormData.append('itemId', itemId.toString())
    uploadFormData.append('imageType', formData.itemCategory.toString())
    uploadFormData.append('sort', (index + 1).toString())
    uploadFormData.append('file', image.file)
    
    try {
      await axios.post('/api/item/image/upload', uploadFormData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      console.log(`图片${index + 1}上传成功`)
    } catch (error) {
      console.error(`图片${index + 1}上传失败:`, error)
      // 图片上传失败不影响主流程
    }
  })
  
  // 并行上传所有图片
  await Promise.all(uploadPromises)
}

/* ================= 导航操作 ================= */
function goBack() {
  router.push('/')
}

async function logout() {
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
/* 复用首页样式，这里只做微小调整 */
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
  max-width: 1000px;
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

/* 表单内容 */
.form-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-section {
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
  padding-bottom: 30px;
}

.form-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.section-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 22px;
  color: #a67c52;
  font-weight: 600;
  margin: 0;
}

.required-mark {
  color: #ff4d4f;
  font-size: 18px;
}

.optional-mark {
  color: rgba(166, 124, 82, 0.5);
  font-size: 16px;
  font-style: italic;
}

.form-row {
  margin-bottom: 15px;
}

.form-row:last-child {
  margin-bottom: 0;
}

/* 发布类型选项 */
.type-options {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.type-option {
  flex: 1;
  min-width: 200px;
  max-height: 100px;
  padding: 25px 20px;
  border: 2px solid rgba(166, 124, 82, 0.3);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.type-option:hover:not(.active):not(.disabled) {
  border-color: rgba(243, 129, 129, 0.5);
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.type-option.active {
  border-color: #f38181;
  background: linear-gradient(135deg, rgba(243, 129, 129, 0.1), rgba(247, 125, 95, 0.1));
  box-shadow: 0 4px 20px rgba(243, 129, 129, 0.2);
}

.type-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.type-icon {
  font-size: 36px;
  margin-bottom: 5px;
}

.type-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  font-weight: 600;
  color: #a67c52;
}

.type-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
}

/* 级联选择器 */
.cascader-group {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.cascader-level {
  flex: 1;
  min-width: 200px;
}

.cascader-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin-bottom: 8px;
  font-weight: 500;
}

.cascader-select {
  width: 100%;
  padding: 12px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
}

.cascader-select:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

.cascader-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 表单输入框 */
.form-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  transition: all 0.3s ease;
  outline: none;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: rgba(166, 124, 82, 0.5);
}

.form-input:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.15);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-input.error {
  border-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.05);
}

.datetime-input {
  max-width: 300px;
}

/* 文本域 */
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  transition: all 0.3s ease;
  outline: none;
  resize: vertical;
  min-height: 120px;
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

/* 图片上传区域 */
.image-uploader {
  position: relative;
}

.upload-area {
  border: 2px dashed rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  padding: 40px 20px;
  background: rgba(255, 255, 255, 0.2);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.upload-area:hover:not(.disabled) {
  border-color: rgba(243, 129, 129, 0.6);
  background: rgba(255, 255, 255, 0.3);
}

.upload-area.drag-over {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.upload-area.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-icon {
  margin-bottom: 15px;
}

.upload-svg {
  width: 60px;
  height: 60px;
  object-fit: contain;
  filter: brightness(0.8);
}

.upload-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 18px;
  color: #a67c52;
  margin-bottom: 8px;
  font-weight: 500;
}

.upload-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.6);
  margin: 5px 0;
}

.file-input {
  display: none;
}

/* 图片预览区 */
.image-preview-container {
  margin-top: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.preview-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 500;
}

.preview-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.6);
}

.image-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.preview-item {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  cursor: move;
}

.preview-item:hover .preview-overlay {
  opacity: 1;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-overlay {
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

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: #ff4d4f;
  color: white;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.delete-btn:hover:not(:disabled) {
  background: #ff7875;
  transform: scale(1.1);
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sort-handle {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: move;
}

.preview-index {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(243, 129, 129, 0.8);
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

/* 悬赏信息组 */
.reward-group,
.contact-group {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.reward-input-group,
.contact-input-group {
  flex: 1;
  min-width: 200px;
}

.reward-label,
.contact-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin-bottom: 8px;
  font-weight: 500;
}

.reward-amount-input {
  position: relative;
}

.currency-symbol {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 500;
}

.reward-input {
  padding-left: 32px;
}

/* 输入提示 */
.input-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.5);
  margin-top: 8px;
}

/* 错误信息 */
.error-message {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #ff4d4f;
  margin-top: 8px;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  margin-top: 40px;
  padding-top: 30px;
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
  min-width: 120px;
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

/* 平板端适配（769px-1024px） */
@media (min-width: 769px) and (max-width: 1024px) {
  .left-nav {
    width: 260px;
  }
  
  .main-content {
    margin-left: 260px;
    max-width: calc(100vw - 260px);
    padding: 20px;
  }
  
  .publish-form-card {
    padding: 30px;
  }
  
  .type-options {
    flex-direction: column;
  }
  
  .type-option {
    min-width: 100%;
  }
  
  .cascader-group {
    flex-direction: column;
  }
  
  .cascader-level {
    min-width: 100%;
  }
  
  .reward-group,
  .contact-group {
    flex-direction: column;
  }
  
  .reward-input-group,
  .contact-input-group {
    min-width: 100%;
  }
}

/* 移动端（768px以下） */
@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }

  /* 左侧导航移至底部，横向布局 */
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
    padding-bottom: 90px; /* 给底部导航留空间 */
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
  
  .section-title {
    font-size: 18px;
  }
  
  .type-options {
    flex-direction: column;
  }
  
  .type-option {
    min-width: 100%;
    padding: 20px 15px;
  }
  
  .cascader-group {
    flex-direction: column;
  }
  
  .cascader-level {
    min-width: 100%;
  }
  
  .cascader-select,
  .form-input,
  .form-textarea {
    font-size: 14px;
    padding: 10px 12px;
  }
  
  .reward-group,
  .contact-group {
    flex-direction: column;
  }
  
  .reward-input-group,
  .contact-input-group {
    min-width: 100%;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .action-btn {
    width: 100%;
    padding: 12px 20px;
  }
  
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
  
  .form-content {
    gap: 20px;
  }
  
  .form-section {
    padding-bottom: 20px;
  }
  
  .type-icon {
    font-size: 28px;
  }
  
  .type-label {
    font-size: 16px;
  }
  
  .type-desc {
    font-size: 12px;
  }
  
  .preview-item {
    width: 120px;
    height: 120px;
  }
}
</style>