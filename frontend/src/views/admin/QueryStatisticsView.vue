<template>
  <div class="query-statistics-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">信息维护与查询</h1>
      <p class="page-subtitle">总览失物招领信息的发布、匹配、认领统计情况</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-overview">
      <div class="stat-card total">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.totalItems }}</div>
          <div class="stat-label">总发布数</div>
        </div>
      </div>
      
      <div class="stat-card lost">
        <div class="stat-icon">🔍</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.lostItems }}</div>
          <div class="stat-label">失物信息</div>
        </div>
      </div>
      
      <div class="stat-card found">
        <div class="stat-icon">📢</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.foundItems }}</div>
          <div class="stat-label">招领信息</div>
        </div>
      </div>
      
      <div class="stat-card matched">
        <div class="stat-icon">🔗</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.matchedItems }}</div>
          <div class="stat-label">已匹配</div>
        </div>
      </div>
      
      <div class="stat-card claimed">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.claimedItems }}</div>
          <div class="stat-label">已认领</div>
        </div>
      </div>
      
      <div class="stat-card success">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-value">{{ overview.successRate }}%</div>
          <div class="stat-label">成功率</div>
        </div>
      </div>
    </div>

    <!-- 时间范围筛选 -->
    <div class="time-filter">
      <div class="filter-group">
        <label class="filter-label">时间范围：</label>
        <select v-model="timeRange" class="filter-select" @change="loadStatistics">
          <option value="7">最近7天</option>
          <option value="30">最近30天</option>
          <option value="90">最近90天</option>
          <option value="365">最近1年</option>
          <option value="custom">自定义</option>
        </select>
      </div>
      
      <div v-if="timeRange === 'custom'" class="custom-range">
        <input 
          v-model="customStartDate" 
          type="date" 
          class="filter-input"
          placeholder="开始日期"
        >
        <span class="date-separator">至</span>
        <input 
          v-model="customEndDate" 
          type="date" 
          class="filter-input"
          placeholder="结束日期"
        >
        <button class="apply-btn" @click="loadStatistics">应用</button>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-card">
        <h3 class="chart-title">发布趋势</h3>
        <div class="chart-container">
          <div v-if="trendData.length === 0" class="chart-placeholder">
            <div class="placeholder-icon">📈</div>
            <div class="placeholder-text">暂无数据</div>
          </div>
          <div v-else class="trend-chart">
            <!-- 这里可以集成图表库，暂时用模拟数据展示 -->
            <div class="chart-bars">
              <div 
                v-for="(item, index) in trendData" 
                :key="index"
                class="chart-bar"
                :style="{ height: item.value * 2 + 'px' }"
                :class="{ lost: item.type === 'lost', found: item.type === 'found' }"
              >
                <span class="bar-value">{{ item.value }}</span>
                <span class="bar-label">{{ item.date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chart-card">
        <h3 class="chart-title">状态分布</h3>
        <div class="chart-container">
          <div v-if="statusData.length === 0" class="chart-placeholder">
            <div class="placeholder-icon">📊</div>
            <div class="placeholder-text">暂无数据</div>
          </div>
          <div v-else class="status-chart">
            <div 
              v-for="item in statusData" 
              :key="item.status"
              class="status-item"
            >
              <div class="status-info">
                <span class="status-name">{{ item.name }}</span>
                <span class="status-count">{{ item.count }}</span>
                <span class="status-percent">{{ item.percent }}%</span>
              </div>
              <div class="status-bar">
                <div 
                  class="status-progress" 
                  :style="{ width: item.percent + '%' }"
                  :class="getStatusClass(item.status)"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 高级查询 -->
    <div class="advanced-query">
      <div class="section-header">
        <h3 class="section-title">高级查询</h3>
        <button class="export-btn" @click="exportData">
          <span class="btn-icon">📥</span>
          导出数据
        </button>
      </div>
      
      <div class="query-form">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">物品分类：</label>
            <select v-model="queryParams.itemCategory" class="form-select">
              <option value="">全部</option>
              <option value="1">失物信息</option>
              <option value="2">招领信息</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">物品类型：</label>
            <select v-model="queryParams.itemType" class="form-select">
              <option value="">全部</option>
              <option value="101">证件类</option>
              <option value="102">银行卡</option>
              <option value="201">手机</option>
              <option value="202">电脑</option>
              <!-- 更多类型 -->
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">地点：</label>
            <select v-model="queryParams.locationId" class="form-select">
              <option value="">全部</option>
              <option value="10101">图书馆</option>
              <option value="10201">教学楼</option>
              <option value="10301">食堂</option>
              <!-- 更多地点 -->
            </select>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">开始时间：</label>
            <input v-model="queryParams.startDate" type="date" class="form-input">
          </div>
          
          <div class="form-group">
            <label class="form-label">结束时间：</label>
            <input v-model="queryParams.endDate" type="date" class="form-input">
          </div>
          
          <div class="form-group">
            <label class="form-label">关键词：</label>
            <input 
              v-model="queryParams.keyword" 
              type="text" 
              class="form-input"
              placeholder="物品名称、特征等"
            >
          </div>
        </div>
        
        <div class="form-actions">
          <button class="query-btn" @click="executeQuery">
            <span class="btn-icon">🔍</span>
            查询
          </button>
          <button class="reset-btn" @click="resetQuery">重置</button>
        </div>
      </div>
    </div>

    <!-- 查询结果 -->
    <div v-if="queryResult.length > 0" class="query-result">
      <div class="result-header">
        <h4 class="result-title">查询结果 ({{ queryResult.length }} 条)</h4>
        <div class="result-actions">
          <button class="action-btn" @click="exportQueryResult">
            <span class="btn-icon">📥</span>
            导出结果
          </button>
        </div>
      </div>
      
      <div class="result-table">
        <table>
          <thead>
            <tr>
              <th>物品名称</th>
              <th>类型</th>
              <th>地点</th>
              <th>发布时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in queryResult" :key="item.id">
              <td class="item-name">{{ item.name }}</td>
              <td>{{ item.itemCategory === 1 ? '失物' : '招领' }}</td>
              <td>{{ item.locationName }}</td>
              <td>{{ formatTime(item.createTime) }}</td>
              <td>
                <span class="status-badge" :class="getStatusClass(item.currentStatus)">
                  {{ getStatusText(item.currentStatus) }}
                </span>
              </td>
              <td>
                <button class="table-btn" @click="viewItemDetail(item)">查看</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'

// 时间范围
const timeRange = ref('30')
const customStartDate = ref('')
const customEndDate = ref('')

// 统计概览
const overview = reactive({
  totalItems: 0,
  lostItems: 0,
  foundItems: 0,
  matchedItems: 0,
  claimedItems: 0,
  successRate: 0
})

// 图表数据
const trendData = ref<any[]>([])
const statusData = ref<any[]>([])

// 查询参数
const queryParams = reactive({
  itemCategory: '',
  itemType: '',
  locationId: '',
  startDate: '',
  endDate: '',
  keyword: ''
})

// 查询结果
const queryResult = ref<any[]>([])

// 加载统计数据
const loadStatistics = async () => {
  try {
    // 加载概览数据
    const overviewResponse = await request.get('/item/admin/statistics', {
      params: { timeRange: timeRange.value }
    })
    
    if (overviewResponse.code === 200) {
      Object.assign(overview, overviewResponse.data)
    }
    
    // 加载趋势数据
    const trendResponse = await request.get('/item/admin/trend', {
      params: { timeRange: timeRange.value }
    })
    
    if (trendResponse.code === 200) {
      trendData.value = trendResponse.data
    }
    
    // 加载状态分布数据
    const statusResponse = await request.get('/item/admin/status-distribution')
    
    if (statusResponse.code === 200) {
      statusData.value = statusResponse.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 执行查询
const executeQuery = async () => {
  try {
    const response = await request.get('/item/admin/list', {
      params: queryParams
    })
    
    if (response.code === 200) {
      queryResult.value = response.data.list || []
    }
  } catch (error) {
    console.error('查询失败:', error)
  }
}

// 重置查询
const resetQuery = () => {
  Object.keys(queryParams).forEach(key => {
    (queryParams as any)[key] = ''
  })
  queryResult.value = []
}

// 导出数据
const exportData = () => {
  // 实现导出逻辑
  console.log('导出数据')
}

// 导出查询结果
const exportQueryResult = () => {
  // 实现导出查询结果逻辑
  console.log('导出查询结果')
}

// 查看物品详情
const viewItemDetail = (item: any) => {
  // 实现查看详情逻辑
  console.log('查看详情:', item)
}

// 获取状态文本
const getStatusText = (status: number) => {
  const statusMap: Record<number, string> = {
    1: '待审核',
    2: '已通过',
    3: '已匹配',
    4: '已认领',
    5: '已驳回',
    6: '已归档',
    7: '已无效'
  }
  return statusMap[status] || '未知状态'
}

// 获取状态样式类
const getStatusClass = (status: number) => {
  const classMap: Record<number, string> = {
    1: 'status-pending',
    2: 'status-approved',
    3: 'status-matched',
    4: 'status-claimed',
    5: 'status-rejected',
    6: 'status-archived',
    7: 'status-invalid'
  }
  return classMap[status] || ''
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.query-statistics-view {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-card.total {
  border-left: 4px solid #007bff;
}

.stat-card.lost {
  border-left: 4px solid #e53e3e;
}

.stat-card.found {
  border-left: 4px solid #38a169;
}

.stat-card.matched {
  border-left: 4px solid #3182ce;
}

.stat-card.claimed {
  border-left: 4px solid #805ad5;
}

.stat-card.success {
  border-left: 4px solid #dd6b20;
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.time-filter {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
}

.custom-range {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.filter-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.apply-btn {
  padding: 6px 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 16px 0;
}

.chart-container {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #999;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.placeholder-text {
  font-size: 14px;
}

.trend-chart {
  width: 100%;
  height: 100%;
}

.chart-bars {
  display: flex;
  align-items: end;
  gap: 8px;
  height: 100%;
  padding: 20px 0;
}

.chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: end;
  position: relative;
}

.chart-bar.lost {
  background: #e53e3e;
}

.chart-bar.found {
  background: #38a169;
}

.bar-value {
  font-size: 12px;
  color: white;
  margin-bottom: 4px;
}

.bar-label {
  font-size: 10px;
  color: #666;
  margin-top: 4px;
}

.status-chart {
  width: 100%;
}

.status-item {
  margin-bottom: 12px;
}

.status-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 14px;
}

.status-name {
  color: #333;
}

.status-count {
  color: #666;
}

.status-percent {
  color: #007bff;
  font-weight: 500;
}

.status-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.status-progress {
  height: 100%;
  transition: width 0.3s ease;
}

.status-progress.status-pending { background: #f6ad55; }
.status-progress.status-approved { background: #38a169; }
.status-progress.status-matched { background: #3182ce; }
.status-progress.status-claimed { background: #805ad5; }
.status-progress.status-rejected { background: #e53e3e; }
.status-progress.status-archived { background: #dd6b20; }
.status-progress.status-invalid { background: #718096; }

.advanced-query {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.export-btn {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.query-form {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: #666;
}

.form-select,
.form-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
}

.form-actions {
  display: flex;
  gap: 12px;
}

.query-btn,
.reset-btn {
  padding: 8px 16px;
  border: 1px solid #007bff;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.query-btn {
  background: #007bff;
  color: white;
}

.reset-btn {
  background: #fff;
  color: #007bff;
}

.query-result {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.action-btn {
  padding: 6px 12px;
  background: #38a169;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.result-table {
  overflow-x: auto;
}

.result-table table {
  width: 100%;
  border-collapse: collapse;
}

.result-table th,
.result-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.result-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.item-name {
  font-weight: 500;
  color: #1a1a1a;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.status-pending { background: #fffaf0; color: #dd6b20; }
.status-badge.status-approved { background: #f0fff4; color: #38a169; }
.status-badge.status-matched { background: #ebf8ff; color: #3182ce; }
.status-badge.status-claimed { background: #f0fff4; color: #38a169; }
.status-badge.status-rejected { background: #fff5f5; color: #e53e3e; }
.status-badge.status-archived { background: #fffaf0; color: #dd6b20; }
.status-badge.status-invalid { background: #f7fafc; color: #718096; }

.table-btn {
  padding: 4px 8px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .query-statistics-view {
    padding: 16px;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .result-table {
    font-size: 12px;
  }
}
</style>