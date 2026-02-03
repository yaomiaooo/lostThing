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
              <!-- 左侧图片 -->
              <div class="left-image">
                <img
                  v-if="images.length > 0"
                  :src="images[0].url"
                  @load="onImageLoad"
                />
                <div v-else class="no-image">暂无图片</div>
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
                  <span>{{ item.happenTime }}</span>
                </div>

                <div class="info-block">
                  <span class="label">特征描述：</span>
                  <p>{{ item.feature }}</p>
                </div>

                <div class="info-line">
                  <span class="label">联系人：</span>
                  <span>{{ item.contactName }} {{ item.contactPhone }}</span>
                </div>

                <div v-if="item.rewardAmount > 0" class="reward">
                  悬赏：￥{{ item.rewardAmount }}
                </div>
              </div>
            </div>

            <!-- loading 占位（关键：防止空卡片） -->
            <div v-else class="loading">
              加载中…
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const props = defineProps<{
  visible: boolean
  itemId: number | null
}>()

const emit = defineEmits(['close'])

const ready = ref(false)
const item = ref<any>({})
const location = ref<any>(null)
const images = ref<any[]>([])

const close = () => {
  emit('close')
}

const loadDetail = async () => {
  if (!props.itemId) return
  ready.value = false

  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: props.itemId }
    })

    const data = res.data.data
    item.value = data.item
    location.value = data.location
    images.value = data.images || []

    ready.value = true
  } catch (e) {
    console.error(e)
  }
}

watch(
  () => props.itemId,
  () => {
    if (props.visible) loadDetail()
  }
)

watch(
  () => props.visible,
  (v) => {
    if (v && props.itemId) loadDetail()
  }
)

// ESC 关闭
const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') close()
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})

const onImageLoad = () => {
  // 图片加载完成后卡片已存在，不会闪
}
</script>

<style scoped>
/* 遮罩 */
.detail-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 卡片主体 */
.detail-card {
  position: relative;
  height: 520px;              /* 高度固定 */
  max-width: 90vw;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  right: 14px;
  top: 10px;
  font-size: 22px;
  cursor: pointer;
  z-index: 10;
}

/* 内容 */
.card-content {
  display: flex;
  height: 100%;
}

/* 左图 */
.left-image {
  height: 100%;
  background: #f6f6f6;
}

.left-image img {
  height: 100%;
  width: auto;                /* 宽度随图片 */
  display: block;
}

.no-image {
  width: 300px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

/* 右侧信息 */
.right-info {
  width: 360px;
  padding: 20px;
  overflow-y: auto;
}

.title {
  margin-bottom: 12px;
}

.info-line {
  margin-bottom: 8px;
  font-size: 14px;
}

.info-block {
  margin-bottom: 12px;
}

.label {
  color: #666;
  margin-right: 6px;
}

.reward {
  margin-top: 10px;
  color: #e4393c;
  font-weight: bold;
}

/* loading */
.loading {
  width: 500px;
  height: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

/* 动画 */
.mask-fade-enter-active,
.mask-fade-leave-active {
  transition: opacity 0.25s;
}
.mask-fade-enter-from,
.mask-fade-leave-to {
  opacity: 0;
}

.card-pop-enter-active,
.card-pop-leave-active {
  transition: all 0.3s ease;
}
.card-pop-enter-from {
  transform: scale(0.96);
  opacity: 0;
}
.card-pop-leave-to {
  transform: scale(0.96);
  opacity: 0;
}
</style>
