<!-- src/views/system-admin/pages/SystemConfigView.vue -->
<template>
  <div class="system-config-page">
    <!-- 背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航 -->
      <SysAdminNavigation 
        subtitle="系统配置"
        active-nav="系统配置"
        @logout="handleLogout"
      />

      <!-- 右侧主内容 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">系统配置</h1>
          <p class="page-subtitle">管理物品类型分类、校区地点等基础数据（支持拖拽、双击编辑、右键菜单）</p>
        </section>

        <!-- 配置标签页和工具栏 -->
        <section class="config-tabs">
          <div class="tab-toolbar-container">
            <div class="tab-buttons">
              <button 
                v-for="tab in tabs" 
                :key="tab.key"
                class="tab-btn"
                :class="{ active: currentTab === tab.key }"
                @click="switchTab(tab.key)"
              >
                <span class="tab-text">{{ tab.label }}</span>
              </button>
            </div>
            
            <!-- 工具栏（移动到标签页右边） -->
            <div class="tree-toolbar">
              <button class="tool-btn" @click="expandAll" title="展开全部">
                <span class="tool-text">展开</span>
              </button>
              <button class="tool-btn" @click="collapseAll" title="收起全部">
                <span class="tool-text">收起</span>
              </button>
              <div class="toolbar-divider"></div>
              <button class="tool-btn primary" @click="addRootNode" title="新增根节点 (Ctrl+R)">
                <span class="tool-text">根节点</span>
              </button>
              <div class="toolbar-divider"></div>
              <span class="shortcut-hint">快捷键: 双击编辑 | 右键菜单 | Enter保存</span>
            </div>
          </div>
        </section>

        <!-- 树形编辑器区域 -->
        <section class="tree-editor-section">

          <!-- 树形结构容器 -->
          <div class="tree-container" @click.self="clearSelection">
            <!-- 加载状态 -->
            <div v-if="loading" class="tree-loading">
              <div class="loading-spinner"></div>
              <span>加载中...</span>
            </div>

            <!-- 空状态 -->
            <div v-else-if="treeData.length === 0" class="tree-empty">
              <div class="empty-title">暂无数据</div>
              <div class="empty-desc">点击上方"根节点"按钮或按 Ctrl+R 创建第一个节点</div>
              <button class="empty-action" @click="addRootNode">创建根节点</button>
            </div>

            <!-- 树节点列表 -->
            <div v-else class="tree-nodes">
              <tree-node
                v-for="node in treeData"
                :key="node.id"
                :node="node"
                :level="0"
                :selected-id="selectedNodeId"
                :editing-id="editingNodeId"
                @select="selectNode"
                @edit="startEdit"
                @save="saveEdit"
                @cancel="cancelEdit"
                @add-child="addChildNode"
                @add-sibling="addSiblingNode"
                @delete="confirmDelete"
                @toggle="toggleExpand"
              />
            </div>
          </div>

          <!-- 属性面板（简化版，仅保留后端支持的字段） -->
          <div class="property-panel" v-if="selectedNode">
            <div class="panel-header">
              <h3 class="panel-title">节点属性</h3>
              <button class="panel-close" @click="clearSelection">×</button>
            </div>
            <div class="panel-body">
              <div class="prop-group">
                <label class="prop-label">节点名称</label>
                <input 
                  type="text" 
                  v-model="selectedNode.name" 
                  class="prop-input"
                  @blur="updateNodeProperty"
                />
              </div>
              <div class="prop-group">
                <label class="prop-label">排序</label>
                <input 
                  type="number" 
                  v-model.number="selectedNode.sortOrder" 
                  class="prop-input"
                  min="0"
                  @blur="updateNodeProperty"
                />
              </div>
              <div class="prop-group">
                <label class="prop-label">状态</label>
                <div class="status-toggle">
                  <label class="switch">
                    <input 
                      type="checkbox" 
                      v-model="selectedNode.status"
                      :true-value="1"
                      :false-value="0"
                      @change="updateNodeProperty"
                    >
                    <span class="slider"></span>
                  </label>
                  <span class="status-text">{{ selectedNode.status === 1 ? '启用' : '禁用' }}</span>
                </div>
              </div>
              <div class="prop-meta">
                <div class="meta-item">
                  <span class="meta-label">ID:</span>
                  <span class="meta-value">{{ selectedNode.id }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">层级:</span>
                  <span class="meta-value">{{ selectedNode.level + 1 }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">子节点:</span>
                  <span class="meta-value">{{ selectedNode.children?.length || 0 }}</span>
                </div>
                <!-- 物品数量暂时隐藏，因后端不返回，可保留占位 -->
                <!-- <div class="meta-item">
                  <span class="meta-label">关联物品:</span>
                  <span class="meta-value">{{ selectedNode.itemCount || 0 }}</span>
                </div> -->
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 右键菜单（不变） -->
    <div 
      v-if="contextMenu.show" 
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @click.stop
    >
      <div class="menu-item" @click="handleMenuAddChild">
        <span class="menu-text">添加子节点</span>
        <span class="menu-shortcut">Insert</span>
      </div>
      <div class="menu-item" @click="handleMenuAddSibling">
        <span class="menu-text">添加同级节点</span>
        <span class="menu-shortcut">Enter</span>
      </div>
      <div class="menu-divider"></div>
      <div class="menu-item" @click="handleMenuEdit">
        <span class="menu-text">编辑名称</span>
        <span class="menu-shortcut">F2</span>
      </div>
      <div class="menu-divider"></div>
      <div 
        class="menu-item danger" 
        @click="handleMenuDelete"
        :class="{ disabled: (selectedNode?.itemCount || 0) > 0 }"
      >
        <span class="menu-text">删除节点</span>
        <span class="menu-shortcut">Delete</span>
      </div>
    </div>

    <!-- 删除确认弹窗（不变） -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">确认删除</h3>
          <button class="modal-close" @click="closeDeleteModal">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-content">
            <p class="confirm-text">确定要删除「{{ deletingNode?.name }}」吗？</p>
            <p class="confirm-hint" v-if="deletingNode?.children?.length">
              该节点包含 {{ deletingNode.children.length }} 个子节点，将一并删除
            </p>
            <p class="confirm-hint" v-if="(deletingNode?.itemCount || 0) > 0" style="color: #f44336;">
              该节点有关联物品，无法删除
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeDeleteModal">取消</button>
          <button 
            class="modal-btn delete-btn" 
            @click="executeDelete"
            :disabled="(deletingNode?.itemCount || 0) > 0 || submitting"
          >
            <span v-if="submitting" class="loading-spinner-small"></span>
            <span v-else>确认删除</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SysAdminNavigation from '../components/SysAdminNavigation.vue'
import TreeNode from '../components/TreeNode.vue'

const router = useRouter()

/* ================= 标签页配置 ================= */
const tabs = [
  { key: 'category', label: '物品类型' },
  { key: 'location', label: '地点管理' }
]
const currentTab = ref('category')

/* ================= 树形数据 ================= */
const loading = ref(false)
const treeData = ref<any[]>([])
const selectedNodeId = ref<number | null>(null)
const editingNodeId = ref<number | null>(null)
const editingValue = ref('')

/* ================= 右键菜单 ================= */
const contextMenu = reactive({
  show: false,
  x: 0,
  y: 0,
  targetNode: null as any
})

/* ================= 删除弹窗 ================= */
const showDeleteModal = ref(false)
const deletingNode = ref<any>(null)
const submitting = ref(false)

/* ================= 预设图标和颜色（用于装饰） ================= */
const commonIcons = []
const presetColors = ['#f38181', '#f77d5f', '#ff9a9e', '#fad0c4', '#a1c4fd', '#c2e9fb', '#84fab0', '#8fd3f4', '#d4fc79', '#96e6a1', '#a8edea', '#fed6e3', '#d299c2', '#fef9d7', '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']

/* ================= 计算属性 ================= */
const selectedNode = computed(() => {
  if (!selectedNodeId.value) return null
  return findNodeById(treeData.value, selectedNodeId.value)
})

/* ================= 工具函数 ================= */
const findNodeById = (nodes: any[], id: number): any | null => {
  for (const node of nodes) {
    if (node.id === id) return node
    if (node.children?.length) {
      const found = findNodeById(node.children, id)
      if (found) return found
    }
  }
  return null
}

const findParentNode = (nodes: any[], targetId: number, parent: any = null): any | null => {
  for (const node of nodes) {
    if (node.id === targetId) return parent
    if (node.children?.length) {
      const found = findParentNode(node.children, targetId, node)
      if (found) return found
    }
  }
  return null
}

const generateId = () => {
  return Date.now() + Math.floor(Math.random() * 1000)
}

// 为节点补充前端需要的装饰字段
const enrichNode = (node: any, level: number = 0) => {
  node.level = level
  // 移除图标和颜色装饰
  node.icon = ''
  node.color = ''
  node.description = node.description || ''
  node.itemCount = node.itemCount || 0
  node.collapsed = node.collapsed === undefined ? false : node.collapsed
  if (node.children && node.children.length > 0) {
    node.children.forEach((child: any) => enrichNode(child, level + 1))
  }
  return node
}

/* ================= 标签切换 ================= */
const switchTab = (tab: string) => {
  currentTab.value = tab
  selectedNodeId.value = null
  editingNodeId.value = null
  loadTreeData()
}

/* ================= 加载数据 ================= */
const loadTreeData = async () => {
  loading.value = true
  try {
    const url = currentTab.value === 'category'
      ? '/api/item/admin/category/tree'
      : '/api/item/admin/location/tree'
    const res = await axios.get(url)
    if (res.data.code === 200 || res.data.code === 0) {
      let data = res.data.data || []
      // 补充前端需要的字段
      data = data.map((node: any) => enrichNode(node))
      treeData.value = data
    } else {
      console.error('加载失败', res.data.msg)
      useMockData()
    }
  } catch (error) {
    console.error('加载树形数据失败:', error)
    useMockData()
  } finally {
    loading.value = false
  }
}

// 降级模拟数据
const useMockData = () => {
  if (currentTab.value === 'category') {
    treeData.value = [
      {
        id: 1,
        name: '电子产品',
        icon: '📱',
        color: '#f38181',
        description: '手机、平板、电脑等电子设备',
        sortOrder: 1,
        status: 1,
        itemCount: 15,
        collapsed: false,
        children: [
          { id: 11, name: '手机', icon: '📱', color: '#f38181', description: '智能手机', sortOrder: 1, status: 1, itemCount: 8, level: 1 },
          { id: 12, name: '电脑', icon: '💻', color: '#a1c4fd', description: '笔记本、台式机', sortOrder: 2, status: 1, itemCount: 5, level: 1 },
          { id: 13, name: '配件', icon: '🎧', color: '#84fab0', description: '耳机、充电器等', sortOrder: 3, status: 1, itemCount: 2, level: 1 }
        ]
      },
      {
        id: 2,
        name: '证件卡片',
        icon: '🆔',
        color: '#a1c4fd',
        description: '校园卡、身份证、银行卡等',
        sortOrder: 2,
        status: 1,
        itemCount: 23,
        collapsed: false,
        children: [
          { id: 21, name: '校园卡', icon: '🆔', color: '#a1c4fd', description: '学生卡、教工卡', sortOrder: 1, status: 1, itemCount: 18, level: 1 },
          { id: 22, name: '身份证', icon: '🆔', color: '#fad0c4', description: '居民身份证', sortOrder: 2, status: 1, itemCount: 3, level: 1 },
          { id: 23, name: '银行卡', icon: '💳', color: '#ff9a9e', description: '各类银行卡', sortOrder: 3, status: 0, itemCount: 2, level: 1 }
        ]
      },
      {
        id: 3,
        name: '箱包配饰',
        icon: '👜',
        color: '#fad0c4',
        description: '背包、钱包、手提包等',
        sortOrder: 3,
        status: 1,
        itemCount: 8,
        collapsed: true,
        children: []
      }
    ].map(node => enrichNode(node))
  } else {
    treeData.value = [
      {
        id: 1,
        name: '朝晖校区',
        description: '主校区',
        sortOrder: 1,
        status: 1,
        itemCount: 25,
        collapsed: false,
        children: [
          {
            id: 11,
            name: '图书馆',
            description: '一楼大厅失物招领处',
            sortOrder: 1,
            status: 1,
            itemCount: 12,
            level: 1,
            children: [
              { id: 111, name: '一楼大厅', description: '服务台旁', sortOrder: 1, status: 1, itemCount: 8, level: 2 },
              { id: 112, name: '二楼阅览室', description: '管理员处', sortOrder: 2, status: 1, itemCount: 4, level: 2 }
            ]
          },
          { id: 12, name: '食堂', description: '一楼服务台', sortOrder: 2, status: 1, itemCount: 8, level: 1 },
          { id: 13, name: '教学楼A', description: '门卫处', sortOrder: 3, status: 1, itemCount: 5, level: 1 }
        ]
      },
      {
        id: 2,
        name: '屏峰校区',
        description: '分校区',
        sortOrder: 2,
        status: 1,
        itemCount: 18,
        collapsed: false,
        children: [
          { id: 21, name: '图书馆', description: '二楼失物招领处', sortOrder: 1, status: 1, itemCount: 15, level: 1 },
          { id: 22, name: '体育馆', description: '前台', sortOrder: 2, status: 1, itemCount: 3, level: 1 }
        ]
      },
      {
        id: 3,
        name: '莫干山校区',
        description: '新校区',
        sortOrder: 3,
        status: 1,
        itemCount: 6,
        collapsed: true,
        children: [
          { id: 31, name: '行政楼', description: '101室', sortOrder: 1, status: 1, itemCount: 6, level: 1 }
        ]
      }
    ].map(node => enrichNode(node))
  }
}

/* ================= 节点操作 ================= */
const selectNode = (node: any) => {
  selectedNodeId.value = node.id
  editingNodeId.value = null
  hideContextMenu()
}

const clearSelection = () => {
  selectedNodeId.value = null
  editingNodeId.value = null
  hideContextMenu()
}

const toggleExpand = (node: any) => {
  node.collapsed = !node.collapsed
}

const expandAll = () => {
  const expand = (nodes: any[]) => {
    nodes.forEach(node => {
      node.collapsed = false
      if (node.children?.length) expand(node.children)
    })
  }
  expand(treeData.value)
}

const collapseAll = () => {
  const collapse = (nodes: any[]) => {
    nodes.forEach(node => {
      if (node.children?.length) {
        node.collapsed = true
        collapse(node.children)
      }
    })
  }
  collapse(treeData.value)
}

/* ================= 编辑功能 ================= */
const startEdit = (node: any) => {
  editingNodeId.value = node.id
  editingValue.value = node.name
  selectedNodeId.value = node.id
  
  nextTick(() => {
    const input = document.querySelector('.node-input') as HTMLInputElement
    if (input) {
      input.focus()
      input.select()
    }
  })
}

const saveEdit = (node: any, newName: string) => {
  if (!newName.trim()) {
    cancelEdit()
    return
  }
  
  node.name = newName.trim()
  editingNodeId.value = null
  updateNode(node)
}

const cancelEdit = () => {
  editingNodeId.value = null
  editingValue.value = ''
}

/* ================= 新增节点 ================= */
const addRootNode = () => {
  const newNode = {
    id: generateId(),
    name: currentTab.value === 'category' ? '新类型' : '新地点',
    icon: '',
    color: '',
    description: '',
    sortOrder: treeData.value.length + 1,
    status: 1,
    itemCount: 0,
    collapsed: false,
    children: [],
    level: 0,
    isNew: true
  }
  
  treeData.value.push(newNode)
  selectNode(newNode)
  startEdit(newNode)
  
  createNode(newNode, null)
}

const addChildNode = (parentNode: any) => {
  const newNode = {
    id: generateId(),
    name: '新节点',
    icon: '',
    color: '',
    description: '',
    sortOrder: (parentNode.children?.length || 0) + 1,
    status: 1,
    itemCount: 0,
    collapsed: false,
    children: [],
    level: (parentNode.level || 0) + 1,
    isNew: true
  }
  
  if (!parentNode.children) parentNode.children = []
  parentNode.children.push(newNode)
  parentNode.collapsed = false
  
  selectNode(newNode)
  startEdit(newNode)
  
  createNode(newNode, parentNode.id)
}

const addSiblingNode = (node: any) => {
  const parent = findParentNode(treeData.value, node.id)
  const siblings = parent ? parent.children : treeData.value
  
  const newNode = {
    id: generateId(),
    name: '新节点',
    icon: '',
    color: '',
    description: '',
    sortOrder: siblings.length + 1,
    status: 1,
    itemCount: 0,
    collapsed: false,
    children: [],
    level: node.level,
    isNew: true
  }
  
  siblings.push(newNode)
  selectNode(newNode)
  startEdit(newNode)
  
  createNode(newNode, parent?.id || null)
}

/* ================= 删除功能 ================= */
const confirmDelete = (node: any) => {
  deletingNode.value = node
  showDeleteModal.value = true
  hideContextMenu()
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  deletingNode.value = null
}

const executeDelete = async () => {
  if (!deletingNode.value) return
  
  // 如果是临时节点（新建但未保存的节点），直接从前端删除
  if (deletingNode.value.isNew) {
    removeNodeFromTree(treeData.value, deletingNode.value.id)
    if (selectedNodeId.value === deletingNode.value.id) {
      selectedNodeId.value = null
    }
    closeDeleteModal()
    return
  }
  
  submitting.value = true
  try {
    const url = currentTab.value === 'category'
      ? `/api/item/admin/category/${deletingNode.value.id}/delete`
      : `/api/item/admin/location/${deletingNode.value.id}/delete`
    
    const res = await axios.delete(url)
    
    if (res.data.code === 200 || res.data.code === 0) {
      removeNodeFromTree(treeData.value, deletingNode.value.id)
      if (selectedNodeId.value === deletingNode.value.id) {
        selectedNodeId.value = null
      }
      closeDeleteModal()
    } else {
      // 更友好的错误提示
      const errorMsg = res.data.msg || '删除失败'
      if (errorMsg.includes('不存在') || errorMsg.includes('not found')) {
        // 如果节点在数据库中不存在，也从前端移除
        removeNodeFromTree(treeData.value, deletingNode.value.id)
        if (selectedNodeId.value === deletingNode.value.id) {
          selectedNodeId.value = null
        }
        closeDeleteModal()
      } else {
        alert(`删除失败: ${errorMsg}`)
      }
    }
  } catch (error: any) {
    console.error('删除失败:', error)
    
    // 处理网络错误或404错误
    if (error.response?.status === 404 || error.message?.includes('not found')) {
      // 节点在服务器上不存在，从前端移除
      removeNodeFromTree(treeData.value, deletingNode.value.id)
      if (selectedNodeId.value === deletingNode.value.id) {
        selectedNodeId.value = null
      }
      closeDeleteModal()
    } else {
      alert('删除失败，请检查网络连接后重试')
    }
  } finally {
    submitting.value = false
  }
}

const removeNodeFromTree = (nodes: any[], targetId: number): boolean => {
  const index = nodes.findIndex(n => n.id === targetId)
  if (index > -1) {
    nodes.splice(index, 1)
    return true
  }
  
  for (const node of nodes) {
    if (node.children?.length) {
      if (removeNodeFromTree(node.children, targetId)) return true
    }
  }
  return false
}

/* ================= 属性更新 ================= */
const updateNodeProperty = async () => {
  if (!selectedNode.value) return
  await updateNode(selectedNode.value)
}

const updateNode = async (node: any) => {
  // 如果是临时节点且名称已修改，尝试创建到后端
  if (node.isNew && node.name !== '新类型' && node.name !== '新地点' && node.name !== '新节点') {
    const parent = findParentNode(treeData.value, node.id)
    await createNode(node, parent?.id || null)
    return
  }
  
  // 如果是已存在的节点，正常更新
  try {
    const url = currentTab.value === 'category'
      ? `/api/item/admin/category/${node.id}`
      : `/api/item/admin/location/${node.id}`
    
    // 只发送后端支持的字段
    const payload = {
      name: node.name,
      sort: node.sortOrder,
      status: node.status
    }
    
    const res = await axios.put(url, payload)
    if (res.data.code !== 200 && res.data.code !== 0) {
      console.error('更新失败:', res.data.msg)
    } else {
      console.log('节点更新成功')
    }
  } catch (error: any) {
    console.error('更新节点失败:', error)
  }
}

const createNode = async (node: any, parentId: number | null) => {
  // 如果节点名称是默认值，等待用户编辑后再保存到后端
  if (node.name === '新类型' || node.name === '新地点' || node.name === '新节点') {
    console.log('节点使用默认名称，等待用户编辑后再保存')
    return
  }
  
  try {
    const url = currentTab.value === 'category'
      ? '/api/item/admin/category'
      : '/api/item/admin/location'
    
    const payload = {
      name: node.name,
      parentId: parentId,
      sort: node.sortOrder,
      status: node.status
    }
    
    const res = await axios.post(url, payload)
    if ((res.data.code === 200 || res.data.code === 0) && res.data.data?.id) {
      // 成功后更新节点ID并标记为非临时节点
      node.id = res.data.data.id
      node.isNew = false
      console.log('节点创建成功，新ID:', node.id)
    } else {
      console.error('创建失败:', res.data.msg)
      // 如果创建失败，保持临时节点状态，用户可重新编辑保存
    }
  } catch (error: any) {
    console.error('创建节点失败:', error)
    // 网络错误时保持临时节点状态
  }
}

/* ================= 右键菜单 ================= */
const showContextMenu = (e: MouseEvent, node: any) => {
  e.preventDefault()
  e.stopPropagation()
  
  contextMenu.show = true
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.targetNode = node
  selectedNodeId.value = node.id
}

const hideContextMenu = () => {
  contextMenu.show = false
  contextMenu.targetNode = null
}

const handleMenuAddChild = () => {
  if (contextMenu.targetNode) {
    addChildNode(contextMenu.targetNode)
  }
  hideContextMenu()
}

const handleMenuAddSibling = () => {
  if (contextMenu.targetNode) {
    addSiblingNode(contextMenu.targetNode)
  }
  hideContextMenu()
}

const handleMenuEdit = () => {
  if (contextMenu.targetNode) {
    startEdit(contextMenu.targetNode)
  }
  hideContextMenu()
}

const handleMenuDelete = () => {
  if (contextMenu.targetNode) {
    confirmDelete(contextMenu.targetNode)
  }
}

/* ================= 键盘快捷键 ================= */
const handleKeydown = (e: KeyboardEvent) => {
  if (e.ctrlKey && e.key === 'r') {
    e.preventDefault()
    addRootNode()
    return
  }
  
  if (!selectedNodeId.value) return
  
  const currentNode = selectedNode.value
  if (!currentNode) return
  
  switch (e.key) {
    case 'F2':
      e.preventDefault()
      startEdit(currentNode)
      break
    case 'Insert':
      e.preventDefault()
      addChildNode(currentNode)
      break
    case 'Enter':
      if (editingNodeId.value) {
        const input = document.querySelector('.node-input') as HTMLInputElement
        if (input) saveEdit(currentNode, input.value)
      } else {
        e.preventDefault()
        addSiblingNode(currentNode)
      }
      break
    case 'Escape':
      if (editingNodeId.value) {
        cancelEdit()
      } else {
        clearSelection()
      }
      break
    case 'Delete':
      if (!editingNodeId.value && (currentNode.itemCount || 0) === 0) {
        e.preventDefault()
        confirmDelete(currentNode)
      }
      break
    case 'ArrowRight':
      e.preventDefault()
      if (currentNode.children?.length && currentNode.collapsed) {
        toggleExpand(currentNode)
      }
      break
    case 'ArrowLeft':
      e.preventDefault()
      if (currentNode.children?.length && !currentNode.collapsed) {
        toggleExpand(currentNode)
      }
      break
  }
}

/* ================= 全局点击关闭菜单 ================= */
const handleGlobalClick = () => {
  hideContextMenu()
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadTreeData()
  document.addEventListener('click', handleGlobalClick)
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('show-node-context-menu', ((e: CustomEvent) => {
    showContextMenu(e.detail.event, e.detail.node)
  }) as EventListener)
})

onUnmounted(() => {
  document.removeEventListener('click', handleGlobalClick)
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('show-node-context-menu', ((e: CustomEvent) => {
    showContextMenu(e.detail.event, e.detail.node)
  }) as EventListener)
})
</script>

<style scoped>
/* 样式基本保持不变，只微调了属性面板部分 */
.system-config-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

.background-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.solid-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #f8f3d4;
  pointer-events: none;
}

.layout-container {
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 100vh;
  display: flex;
}

.main-content {
  flex: 1;
  min-height: calc(100vh - 48px);
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
}

.page-header {
  margin-bottom: 25px;
}

.page-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 32px;
  color: #a67c52;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.page-subtitle {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.7);
}

.config-tabs {
  margin-bottom: 20px;
}

.tab-toolbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 8px 16px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.tab-buttons {
  display: flex;
  gap: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  background: transparent;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: rgba(166, 124, 82, 0.1);
}

.tab-btn.active {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.tab-icon {
  font-size: 18px;
}

.tree-editor-section {
  display: flex;
  gap: 20px;
  height: calc(100vh - 320px);
  min-height: 500px;
  position: relative;
}

.tree-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: rgba(166, 124, 82, 0.2);
  margin: 0 5px;
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tool-btn:hover {
  border-color: rgba(243, 129, 129, 0.5);
  background: rgba(243, 129, 129, 0.1);
}

.tool-btn.primary {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  border-color: transparent;
}

.tool-btn.primary:hover {
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.tool-icon {
  font-size: 14px;
}

.shortcut-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  background: rgba(166, 124, 82, 0.1);
  padding: 6px 12px;
  border-radius: 6px;
}

.tree-container {
  flex: 1;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
  padding-top: 60px;
  max-height: calc(100vh - 400px);
}

.tree-nodes {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
}

.tree-loading,
.tree-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(166, 124, 82, 0.2);
  border-top-color: #a67c52;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 15px;
  opacity: 0.6;
}

.empty-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 22px;
  color: #a67c52;
  margin-bottom: 10px;
}

.empty-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 20px;
}

.empty-action {
  padding: 12px 30px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.empty-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.property-panel {
  width: 320px;
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 20px;
  padding: 20px;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
  position: sticky;
  top: 20px;
  align-self: flex-start;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.panel-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0;
  font-weight: 600;
}

.panel-close {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-close:hover {
  background: rgba(166, 124, 82, 0.2);
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.prop-group {
  margin-bottom: 20px;
}

.prop-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.prop-input,
.prop-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.5);
  outline: none;
  box-sizing: border-box;
}

.prop-input:focus,
.prop-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

.prop-textarea {
  resize: vertical;
  min-height: 80px;
}

/* 移除图标和颜色选择器，简化面板 */
.status-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(166, 124, 82, 0.3);
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background: linear-gradient(to right, #f38181, #f77d5f);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.status-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.prop-meta {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.meta-item {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
}

.meta-label {
  color: rgba(166, 124, 82, 0.6);
}

.meta-value {
  color: #a67c52;
  font-weight: 600;
  margin-left: 4px;
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  min-width: 180px;
  z-index: 1000;
  border: 1px solid rgba(166, 124, 82, 0.1);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.2s ease;
}

.menu-item:hover:not(.disabled) {
  background: rgba(243, 129, 129, 0.1);
}

.menu-item.danger {
  color: #f44336;
}

.menu-item.danger:hover:not(.disabled) {
  background: rgba(244, 67, 54, 0.1);
}

.menu-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.menu-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.menu-text {
  flex: 1;
}

.menu-shortcut {
  font-size: 11px;
  color: rgba(166, 124, 82, 0.5);
  background: rgba(166, 124, 82, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.menu-divider {
  height: 1px;
  background: rgba(166, 124, 82, 0.1);
  margin: 6px 0;
}

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
  padding: 20px;
}

.confirm-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.modal-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 20px;
  color: #a67c52;
  margin: 0;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: rgba(166, 124, 82, 0.6);
  cursor: pointer;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
}

.modal-body {
  padding: 20px;
}

.confirm-content {
  text-align: center;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.confirm-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  margin-bottom: 10px;
}

.confirm-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
  margin: 5px 0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.modal-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cancel-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

.cancel-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.delete-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.delete-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
}

.modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 240px;
    max-width: calc(100vw - 240px);
    padding: 20px;
  }
  
  .tree-editor-section {
    flex-direction: column;
    height: auto;
    min-height: 400px;
  }
  
  .property-panel {
    width: 100%;
    max-height: 300px;
    position: relative;
    top: 0;
  }
}

@media (max-width: 768px) {
  .layout-container {
    flex-direction: column;
  }
  
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 16px;
    min-height: calc(100vh - 80px);
  }
  
  .page-title {
    font-size: 24px;
    text-align: center;
  }
  
  .page-subtitle {
    text-align: center;
  }
  
  .tab-buttons {
    width: 100%;
    justify-content: center;
  }
  
  .tab-text {
    display: none;
  }
  
  .tree-editor-section {
    height: auto;
    min-height: 300px;
    gap: 16px;
  }
  
  .tree-toolbar {
    position: relative;
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 16px;
    margin-bottom: 16px;
  }
  
  .toolbar-left {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .tree-container {
    padding-top: 0;
    max-height: 400px;
  }
  
  .shortcut-hint {
    display: none;
  }
  
  .tool-text {
    display: none;
  }
  
  .property-panel {
    position: relative;
    width: 100%;
    max-height: 300px;
    border-radius: 12px;
    margin-top: 16px;
  }
}
</style>