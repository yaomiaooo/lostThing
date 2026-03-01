<!-- src/views/system-admin/pages/components/TreeNode.vue -->
<template>
  <div class="tree-node-wrapper">
    <div 
      class="tree-node"
      :class="{ 
        'node-selected': selectedId === node.id,
        'node-editing': editingId === node.id,
        'node-collapsed': node.collapsed,
        'node-disabled': node.status === 0
      }"
      :style="{ paddingLeft: level * 28 + 'px' }"
      @click.stop="$emit('select', node)"
      @dblclick.stop="$emit('edit', node)"
      @contextmenu.prevent.stop="handleRightClick($event, node)"
    >
      <!-- 展开/收起按钮 -->
      <button 
        v-if="node.children?.length"
        class="expand-btn"
        @click.stop="$emit('toggle', node)"
      >
        <span class="expand-icon">{{ node.collapsed ? '▶' : '▼' }}</span>
      </button>
      <span v-else class="expand-placeholder"></span>
      
      <!-- 节点图标（仅装饰，不可编辑） -->
      <span 
        v-if="node.icon" 
        class="node-icon"
        :style="{ background: node.color }"
      >
        {{ node.icon }}
      </span>
      
      <!-- 节点内容 -->
      <div class="node-content">
        <input
          v-if="editingId === node.id"
          type="text"
          class="node-input"
          v-model="editValue"
          @blur="handleSave"
          @keydown.enter="handleSave"
          @keydown.esc="$emit('cancel')"
          @click.stop
        />
        <span v-else class="node-label">{{ node.name }}</span>
        
        <!-- 节点标签 -->
        <div class="node-badges">
          <span v-if="node.itemCount > 0" class="badge count">
            {{ node.itemCount }}
          </span>
          <span v-if="node.status === 0" class="badge disabled">禁用</span>
          <span v-if="node.isNew" class="badge new">新</span>
        </div>
      </div>
      
      <!-- 快速操作按钮（悬停显示） -->
      <div class="node-actions">
        <button 
          class="action-mini"
          title="添加子节点"
          @click.stop="$emit('add-child', node)"
        >
          +
        </button>
        <button 
          class="action-mini"
          title="编辑"
          @click.stop="$emit('edit', node)"
        >
          ✏️
        </button>
      </div>
    </div>
    
    <!-- 子节点 -->
    <div 
      v-if="node.children?.length && !node.collapsed"
      class="node-children"
    >
      <tree-node
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :level="level + 1"
        :selected-id="selectedId"
        :editing-id="editingId"
        @select="$emit('select', $event)"
        @edit="$emit('edit', $event)"
        @save="$emit('save', $event, $event.target?.value)"
        @cancel="$emit('cancel')"
        @add-child="$emit('add-child', $event)"
        @add-sibling="$emit('add-sibling', $event)"
        @delete="$emit('delete', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  node: any
  level: number
  selectedId: number | null
  editingId: number | null
}>()

const emit = defineEmits<{
  select: [node: any]
  edit: [node: any]
  save: [node: any, value: string]
  cancel: []
  'add-child': [node: any]
  'add-sibling': [node: any]
  delete: [node: any]
  toggle: [node: any]
}>()

const editValue = ref('')

watch(() => props.editingId, (newVal) => {
  if (newVal === props.node.id) {
    editValue.value = props.node.name
    nextTick(() => {
      const input = document.querySelector('.node-input') as HTMLInputElement
      if (input) {
        input.focus()
        input.select()
      }
    })
  }
})

const handleSave = () => {
  emit('save', props.node, editValue.value)
}

const handleRightClick = (e: MouseEvent, node: any) => {
  const event = new CustomEvent('show-node-context-menu', {
    detail: { event: e, node }
  })
  document.dispatchEvent(event)
}
</script>

<style scoped>
.tree-node-wrapper {
  user-select: none;
  width: 100%;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin: 2px 0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  width: 100%;
  box-sizing: border-box;
  min-height: 48px;
}

.tree-node:hover {
  background: rgba(166, 124, 82, 0.1);
  transform: translateX(4px);
}

.tree-node.node-selected {
  background: rgba(243, 129, 129, 0.2);
  border: 2px solid rgba(243, 129, 129, 0.4);
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.15);
}

.tree-node.node-editing {
  background: rgba(243, 129, 129, 0.1);
  border: 2px solid rgba(243, 129, 129, 0.3);
}

.tree-node.node-disabled {
  opacity: 0.5;
  background: rgba(166, 124, 82, 0.05);
}

.expand-btn {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 4px;
  background: rgba(166, 124, 82, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.expand-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.expand-icon {
  font-size: 10px;
  color: #a67c52;
  transition: transform 0.2s ease;
}

.node-collapsed .expand-icon {
  transform: rotate(-90deg);
}

.expand-placeholder {
  width: 20px;
  flex-shrink: 0;
}

.node-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.node-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  max-width: calc(100% - 120px);
}

.node-input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #f38181;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: white;
  outline: none;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}

.node-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.node-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 11px;
  font-weight: 600;
}

.badge.count {
  background: rgba(166, 124, 82, 0.15);
  color: #a67c52;
}

.badge.disabled {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.badge.new {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.node-actions {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.3s ease;
  flex-shrink: 0;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.action-mini {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: rgba(166, 124, 82, 0.1);
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.action-mini:hover {
  background: rgba(243, 129, 129, 0.25);
  transform: scale(1.15);
  box-shadow: 0 2px 8px rgba(243, 129, 129, 0.2);
}

.node-children {
  position: relative;
}

.node-children::before {
  content: '';
  position: absolute;
  left: 24px;
  top: 0;
  bottom: 12px;
  width: 2px;
  background: rgba(166, 124, 82, 0.1);
  border-radius: 1px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .tree-node {
    padding: 10px 12px;
    min-height: 44px;
  }
  
  .node-content {
    max-width: calc(100% - 100px);
  }
  
  .action-mini {
    width: 26px;
    height: 26px;
  }
}

@media (max-width: 768px) {
  .tree-node {
    padding: 8px 10px;
    min-height: 40px;
    gap: 6px;
  }
  
  .node-actions {
    opacity: 1;
    gap: 4px;
  }
  
  .action-mini {
    width: 24px;
    height: 24px;
    font-size: 11px;
  }
  
  .node-content {
    gap: 8px;
    max-width: calc(100% - 80px);
  }
  
  .node-label {
    font-size: 14px;
  }
  
  .expand-btn {
    width: 18px;
    height: 18px;
  }
  
  .expand-placeholder {
    width: 18px;
  }
  
  .node-icon {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
}
</style>