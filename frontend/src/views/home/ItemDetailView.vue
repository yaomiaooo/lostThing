<template>
  <Transition name="overlay-fade">
    <div
      v-if="visible"
      class="overlay"
      @click.self="handleClose"
    >
      <Transition name="card-zoom">
        <div
          v-if="loaded"
          class="detail-card"
        >
          <!-- 关闭按钮 -->
          <button class="close-btn" @click="handleClose">×</button>

          <!-- 加载中 -->
          <div v-if="loading" class="loading">
            加载中…
          </div>

          <!-- 内容区 -->
          <div v-else class="content">
            <h2 class="title">{{ detail.name }}</h2>

            <div class="meta">
              <span class="tag">
                {{ detail.itemType === 1 ? '失物' : '招领' }}
              </span>
              <span class="tag gray">
                {{ detail.itemCategory === 1 ? '个人物品' : '其他' }}
              </span>
            </div>

            <div class="info">
              <div class="row">
                <label>发生时间</label>
                <span>{{ detail.happenTime }}</span>
              </div>
              <div class="row">
                <label>特征描述</label>
                <span>{{ detail.feature || '无' }}</span>
              </div>
              <div class="row">
                <label>悬赏金额</label>
                <span>{{ detail.rewardAmount ? `¥${detail.rewardAmount}` : '无' }}</span>
              </div>
              <div class="row">
                <label>悬赏说明</label>
                <span>{{ detail.rewardDesc || '无' }}</span>
              </div>
              <div class="row">
                <label>联系人</label>
                <span>{{ detail.contactName }}</span>
              </div>
              <div class="row">
                <label>联系电话</label>
                <span>{{ detail.contactPhone }}</span>
              </div>
            </div>

            <!-- 操作区 -->
            <div class="actions">
              <button class="primary" @click="handleClaim">
                我要认领
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

/* ========== Props & Emits ========== */
const props = defineProps<{
  itemId: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

/* ========== 状态 ========== */
const visible = ref(true)
const loading = ref(true)
const loaded = ref(false)

const detail = ref<any>({})

/* ========== 生命周期 ========== */
onMounted(() => {
  fetchDetail()
})

watch(
  () => props.itemId,
  () => {
    fetchDetail()
  }
)

/* ========== 方法 ========== */
const fetchDetail = async () => {
  loading.value = true
  loaded.value = false

  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: props.itemId }
    })

    if (res.data.code === 200) {
      detail.value = res.data.data
      loaded.value = true
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  visible.value = false
  setTimeout(() => {
    emit('close')
  }, 200)
}

const handleClaim = async () => {
  await axios.post('/api/item/claim', {
    itemId: props.itemId,
    proofFeature: ''
  })
  alert('认领申请已提交')
}
</script>

<style scoped>
/* ========== 遮罩层 ========== */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ========== 卡片 ========== */
.detail-card {
  width: 90%;
  max-width: 560px;
  max-height: 85vh;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  overflow-y: auto;
  position: relative;
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 12px;
  right: 16px;
  font-size: 22px;
  border: none;
  background: none;
  cursor: pointer;
}

/* 内容 */
.title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
}

.meta {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  background: #3b82f6;
  color: #fff;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.tag.gray {
  background: #9ca3af;
}

.info .row {
  display: flex;
  margin-bottom: 10px;
}

.info label {
  width: 90px;
  color: #6b7280;
}

.actions {
  margin-top: 20px;
  text-align: right;
}

.primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  cursor: pointer;
}

/* ========== 动画 ========== */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

.card-zoom-enter-active,
.card-zoom-leave-active {
  transition: all 0.25s ease;
}

.card-zoom-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.card-zoom-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}
</style>
