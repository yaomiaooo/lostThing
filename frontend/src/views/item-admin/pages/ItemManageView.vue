<!-- src/views/item-admin/pages/ItemManageView.vue -->
<template>
  <div class="item-manage-page">
    <!-- 纯色背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航栏 -->
      <AdminNavigation />

      <!-- 右侧主内容区域 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">物品管理</h1>
          <p class="page-subtitle">管理已发布物品状态，处理认领申请，归档长期无人认领物品</p>
        </section>

        <!-- 统计概览 -->
        <section class="stats-section">
          <div class="stats-grid">
            <div class="stat-card" @click="quickFilter('all')">
              <div class="stat-icon">📦</div>
              <div class="stat-value">{{ overview.total }}</div>
              <div class="stat-label">全部物品</div>
            </div>
            <div class="stat-card highlight" @click="quickFilter('2')">
              <div class="stat-icon">✅</div>
              <div class="stat-value">{{ overview.approved }}</div>
              <div class="stat-label">已通过</div>
            </div>
            <div class="stat-card warning" @click="quickFilter('3')">
              <div class="stat-icon">🤝</div>
              <div class="stat-value">{{ overview.matched }}</div>
              <div class="stat-label">已匹配</div>
            </div>
            <div class="stat-card success" @click="quickFilter('4')">
              <div class="stat-icon">🎉</div>
              <div class="stat-value">{{ overview.claimed }}</div>
              <div class="stat-label">已认领</div>
            </div>
            <div class="stat-card danger" @click="quickFilter('7')">
              <div class="stat-icon">📁</div>
              <div class="stat-value">{{ overview.archived }}</div>
              <div class="stat-label">已归档</div>
            </div>
            <div class="stat-card info" @click="openUnclaimedModal">
              <div class="stat-icon">⏰</div>
              <div class="stat-value">{{ overview.longTermUnclaimed }}</div>
              <div class="stat-label">超30天未认领</div>
            </div>
          </div>
        </section>

        <!-- 筛选工具栏 -->
        <section class="toolbar-section">
          <div class="filter-row">
            <div class="filter-group">
              <select v-model="filterParams.status" class="filter-select" @change="loadItemList">
                <option value="">全部状态</option>
                <option value="2">已通过</option>
                <option value="3">已匹配</option>
                <option value="4">已认领</option>
                <option value="5">已驳回</option>
                <option value="6">已取消</option>
                <option value="7">已归档</option>
              </select>
              <select v-model="filterParams.itemCategory" class="filter-select" @change="loadItemList">
                <option value="">全部类型</option>
                <option value="1">失物</option>
                <option value="2">招领</option>
              </select>
              <select v-model="filterParams.locationId" class="filter-select" @change="loadItemList">
                <option value="">全部校区</option>
                <option value="1">朝晖校区</option>
                <option value="2">屏峰校区</option>
                <option value="3">莫干山校区</option>
              </select>
              <div class="refresh-btn" @click="refreshList">
                <span>刷新</span>
              </div>
            </div>
            <div class="search-box">
              <input 
                v-model="filterParams.keyword" 
                type="text" 
                class="search-input" 
                placeholder="搜索物品名称、地点..."
                @keyup.enter="loadItemList"
              />
              <button class="search-btn" @click="loadItemList">🔍︎</button>
            </div>
          </div>
          <div class="action-row" v-if="selectedItems.length > 0">
            <div class="batch-actions">
              <span class="selected-count">已选 {{ selectedItems.length }} 项</span>
              <button class="batch-btn archive-btn" @click="batchArchive">
                📁 批量归档
              </button>
              <button class="batch-btn delete-btn" @click="batchDelete">
                🗑️ 批量删除
              </button>
            </div>
          </div>
        </section>

        <!-- 物品列表 -->
        <section class="list-section">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <div class="loading-text">加载中...</div>
          </div>

          <!-- 空状态 -->
          <div v-else-if="itemList.length === 0" class="empty-container">
            <div class="empty-icon">📭</div>
            <div class="empty-title">暂无物品记录</div>
            <div class="empty-desc">当前筛选条件下没有符合条件的物品</div>
          </div>

          <!-- 数据表格 -->
          <div v-else class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox">
                    <input 
                      type="checkbox" 
                      :checked="isAllSelected"
                      @change="toggleSelectAll"
                    />
                  </th>
                  <th class="col-id">ID</th>
                  <th class="col-type">类型</th>
                  <th class="col-image">图片</th>
                  <th class="col-info">物品信息</th>
                  <th class="col-status">状态</th>
                  <th class="col-claims">认领申请</th>
                  <th class="col-time">发布时间</th>
                  <th class="col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="item in itemList" 
                  :key="item.itemId"
                  class="table-row"
                  :class="{ 'row-selected': selectedItems.includes(item.itemId) }"
                >
                  <td class="col-checkbox">
                    <input 
                      type="checkbox" 
                      :checked="selectedItems.includes(item.itemId)"
                      @change="toggleSelectItem(item.itemId)"
                    />
                  </td>
                  <td class="col-id">#{{ item.itemId }}</td>
                  <td class="col-type">
                    <span class="type-tag" :class="item.itemCategory === 1 ? 'lost-tag' : 'found-tag'">
                      {{ item.itemCategory === 1 ? '失物' : '招领' }}
                    </span>
                  </td>
                  <td class="col-image">
                    <div class="image-preview" @click="previewImage(item.firstImageUrl)">
                      <img v-if="item.firstImageUrl" :src="item.firstImageUrl" class="thumb-image" />
                      <div v-else class="no-image">无图</div>
                    </div>
                  </td>
                  <td class="col-info">
                    <div class="info-name">{{ item.name }}</div>
                    <div class="info-campus">🏫 {{ getLocationCampus(item) }}</div>
                    <div class="info-location">📍 {{ item.locationName }}</div>
                    <div v-if="item.rewardAmount > 0" class="info-reward">
                      💰 ¥{{ item.rewardAmount }}
                    </div>
                  </td>
                  <td class="col-status">
                    <span class="status-tag" :class="getStatusClass(item.currentStatus)">
                      {{ item.currentStatusName }}
                    </span>
                    <div v-if="item.archiveDesc" class="archive-desc" :title="item.archiveDesc">
                      📁 {{ truncateText(item.archiveDesc, 15) }}
                    </div>
                  </td>
                  <td class="col-claims">
                    <div v-if="item.pendingClaimCount > 0" class="claim-badge" @click="viewClaims(item)">
                      {{ item.pendingClaimCount }} 条待审核
                    </div>
                    <div v-else-if="item.claimCount > 0" class="claim-info">
                      {{ item.claimCount }} 条申请
                    </div>
                    <div v-else class="claim-empty">-</div>
                  </td>
                  <td class="col-time">
                    <div class="time-main">{{ formatDate(item.createTime) }}</div>
                    <div class="time-ago">{{ timeAgo(item.createTime) }}</div>
                  </td>
                  <td class="col-actions">
                    <div class="action-btns">
                      <button class="action-btn view-btn" @click="viewDetail(item)">查看</button>
                      <!-- 新增编辑按钮：所有状态都可以编辑 -->
                      <button 
                        class="action-btn edit-btn"
                        @click="openEditModal(item)"
                      >
                        编辑
                      </button>
                      <button 
                        v-if="item.currentStatus === 2 || item.currentStatus === 3"
                        class="action-btn status-btn"
                        @click="openStatusModal(item)"
                      >
                        更新状态
                      </button>
                      <button 
                        v-if="item.pendingClaimCount > 0"
                        class="action-btn claim-btn"
                        @click="viewClaims(item)"
                      >
                        审核认领
                      </button>
                      <button 
                        v-if="canArchive(item)"
                        class="action-btn archive-btn"
                        @click="openArchiveModal(item)"
                      >
                        归档
                      </button>
                      <button 
                        v-if="item.currentStatus === 5 || item.currentStatus === 6"
                        class="action-btn delete-btn"
                        @click="confirmDelete(item)"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <!-- 分页 -->
            <div class="pagination">
              <button 
                class="page-btn" 
                :disabled="pagination.page === 1"
                @click="changePage(pagination.page - 1)"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ pagination.page }} 页 / 共 {{ pagination.totalPages }} 页（共 {{ pagination.total }} 条）
              </span>
              <button 
                class="page-btn" 
                :disabled="pagination.page >= pagination.totalPages"
                @click="changePage(pagination.page + 1)"
              >
                下一页
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 物品详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">物品详情</h3>
          <button class="modal-close" @click="closeDetailModal">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-content" v-if="currentItem">
            <!-- 图片展示 -->
            <div class="detail-images" v-if="currentItemImages.length > 0">
              <div class="image-main">
                <img 
                  :src="currentItemImages[currentImageIndex]" 
                  class="main-image" 
                  @click="previewImage(currentItemImages[currentImageIndex])"
                />
              </div>
              <div class="image-thumbs" v-if="currentItemImages.length > 1">
                <img 
                  v-for="(img, idx) in currentItemImages" 
                  :key="idx"
                  :src="img" 
                  class="thumb" 
                  :class="{ active: idx === currentImageIndex }"
                  @click="currentImageIndex = idx"
                />
              </div>
            </div>
            
            <!-- 基本信息 -->
            <div class="detail-info">
              <div class="info-row">
                <span class="info-label">物品名称：</span>
                <span class="info-value">{{ currentItem.name }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">物品类型：</span>
                <span class="info-value">{{ currentItem.itemTypeName }}（{{ currentItem.itemCategory === 1 ? '失物' : '招领' }}）</span>
              </div>
              <div class="info-row">
                <span class="info-label">发生时间：</span>
                <span class="info-value">{{ currentItem.happenTime }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">地点：</span>
                <span class="info-value">{{ getLocationCampus(currentItem) }} {{ currentItem.locationName }} {{ currentItem.locationDetail }}</span>
              </div>
              <div class="info-row" v-if="currentItem.pickupLocation">
                <span class="info-label">领取地点：</span>
                <span class="info-value">{{ currentItem.pickupLocation }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">特征描述：</span>
                <span class="info-value description">{{ currentItem.feature }}</span>
              </div>
              <div class="info-row" v-if="currentItem.rewardAmount > 0">
                <span class="info-label">悬赏金额：</span>
                <span class="info-value reward">¥{{ currentItem.rewardAmount }} {{ currentItem.rewardDesc }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">联系人：</span>
                <span class="info-value">{{ currentItem.contactName }} {{ currentItem.contactPhone }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">发布时间：</span>
                <span class="info-value">{{ currentItem.createTime }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeDetailModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- ==================== 新增：编辑物品弹窗 ==================== -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="edit-modal">
        <div class="modal-header">
          <h3 class="modal-title">编辑物品信息</h3>
          <button class="modal-close" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <div class="edit-content" v-if="editingItem">
            <!-- 左侧：图片管理 -->
            <div class="edit-left-column">
              <div class="edit-section">
                <div class="section-header">
                  <h4 class="section-title">物品图片</h4>
                  <span class="section-subtitle">（最多5张，拖拽排序）</span>
                </div>
                
                <!-- 图片上传区域 -->
                <div 
                  class="upload-area"
                  :class="{ 'drag-over': dragOver }"
                  @click="triggerFileInput"
                  @dragover.prevent="handleDragOver"
                  @dragleave.prevent="handleDragLeave"
                  @drop.prevent="handleDrop"
                >
                  <div class="upload-icon">📷</div>
                  <p class="upload-text">点击或拖拽上传图片</p>
                  <p class="upload-hint">支持 JPG/PNG，单张不超过5MB</p>
                </div>
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept="image/*"
                  class="file-input"
                  @change="handleFileSelect"
                />

                <!-- 图片预览区 -->
                <div v-if="editImages.length > 0" class="edit-image-grid">
                  <div 
                    v-for="(image, index) in editImages"
                    :key="index"
                    class="edit-grid-item"
                    draggable="true"
                    @dragstart="handleDragStart(index)"
                    @dragover.prevent
                    @drop="handleDropSort(index)"
                  >
                    <img :src="image.previewUrl" class="edit-grid-image" />
                    <div class="edit-grid-overlay">
                      <button 
                        type="button"
                        class="edit-grid-delete-btn"
                        @click.stop="removeEditImage(index)"
                      >
                        ×
                      </button>
                      <div class="edit-grid-sort">↕</div>
                    </div>
                    <div class="edit-grid-index">{{ index + 1 }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：表单信息 -->
            <div class="edit-right-column">
              <!-- 基本信息 -->
              <div class="edit-section">
                <div class="section-header">
                  <h4 class="section-title">基本信息</h4>
                </div>
                
                <!-- 物品名称 -->
                <div class="edit-form-row">
                  <label class="edit-label">物品名称 <span class="required">*</span></label>
                  <input 
                    v-model="editForm.name" 
                    type="text" 
                    class="edit-input"
                    placeholder="请输入物品名称"
                    maxlength="50"
                  />
                </div>

                <!-- 发布类型 -->
                <div class="edit-form-row">
                  <label class="edit-label">发布类型</label>
                  <div class="edit-type-display">
                    <span class="type-badge" :class="editForm.itemCategory === 1 ? 'lost-badge' : 'found-badge'">
                      {{ editForm.itemCategory === 1 ? '失物寻找' : '招领启事' }}
                    </span>
                    <span class="type-hint">（类型不可修改）</span>
                  </div>
                </div>

                <!-- 物品分类 -->
                <div class="edit-form-row">
                  <label class="edit-label">物品分类 <span class="required">*</span></label>
                  <div class="edit-cascader">
                    <div class="cascader-level">
                      <label class="cascader-label">一级分类</label>
                      <select 
                        v-model="editSelectedFirstCategory"
                        class="edit-select"
                        @change="onEditFirstCategoryChange"
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
                    <div class="cascader-level">
                      <label class="cascader-label">二级分类</label>
                      <select 
                        v-model="editSelectedSecondCategory"
                        class="edit-select"
                        @change="onEditSecondCategoryChange"
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
                </div>
              </div>

              <!-- 地点信息 -->
              <div class="edit-section">
                <div class="section-header">
                  <h4 class="section-title">地点信息</h4>
                </div>
                
                <div class="edit-form-row">
                  <label class="edit-label">所在校区/地点 <span class="required">*</span></label>
                  <div class="edit-cascader location-cascader">
                    <div class="cascader-level">
                      <label class="cascader-label">校区</label>
                      <select 
                        v-model="editSelectedCampus"
                        class="edit-select"
                        @change="onEditCampusChange"
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
                    <div class="cascader-level">
                      <label class="cascader-label">区域</label>
                      <select 
                        v-model="editSelectedArea"
                        class="edit-select"
                        @change="onEditAreaChange"
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
                    <div class="cascader-level">
                      <label class="cascader-label">具体地点</label>
                      <select 
                        v-model="editSelectedLocation"
                        class="edit-select"
                        @change="onEditLocationChange"
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
                </div>

                <div class="edit-form-row">
                  <label class="edit-label">位置补充</label>
                  <input 
                    v-model="editForm.locationDetail" 
                    type="text" 
                    class="edit-input"
                    placeholder="如：三楼自习区、操场跑道内侧"
                    maxlength="255"
                  />
                </div>

                <!-- 领取地点（仅招领） -->
                <div class="edit-form-row" v-if="editForm.itemCategory === 2">
                  <label class="edit-label">领取地点</label>
                  <input 
                    v-model="editForm.pickupLocation" 
                    type="text" 
                    class="edit-input"
                    placeholder="如：保卫处值班室"
                    maxlength="255"
                  />
                </div>
              </div>

              <!-- 时间与悬赏 -->
              <div class="edit-section">
                <div class="section-header">
                  <h4 class="section-title">时间与悬赏</h4>
                </div>
                
                <div class="edit-form-row">
                  <label class="edit-label">{{ editForm.itemCategory === 1 ? '丢失时间' : '发现时间' }} <span class="required">*</span></label>
                  <input 
                    v-model="editForm.happenTime" 
                    type="datetime-local" 
                    class="edit-input datetime-input"
                  />
                </div>

                <!-- 悬赏金额（仅失物） -->
                <template v-if="editForm.itemCategory === 1">
                  <div class="edit-form-row">
                    <label class="edit-label">悬赏金额（元）</label>
                    <div class="currency-input">
                      <span class="currency-symbol">¥</span>
                      <input 
                        v-model="editForm.rewardAmount" 
                        type="number" 
                        class="edit-input reward-input"
                        placeholder="0.00"
                        min="0"
                        max="999999.99"
                        step="0.01"
                      />
                    </div>
                  </div>
                  <div class="edit-form-row">
                    <label class="edit-label">悬赏说明</label>
                    <input 
                      v-model="editForm.rewardDesc" 
                      type="text" 
                      class="edit-input"
                      placeholder="如：找到必有重谢"
                      maxlength="200"
                    />
                  </div>
                </template>
              </div>

              <!-- 特征描述 -->
              <div class="edit-section">
                <div class="section-header">
                  <h4 class="section-title">特征描述</h4>
                </div>
                <div class="edit-form-row">
                  <textarea 
                    v-model="editForm.feature" 
                    class="edit-textarea"
                    placeholder="请详细描述物品特征，如：颜色、大小、品牌、磨损情况等"
                    rows="4"
                    maxlength="1000"
                  ></textarea>
                  <div class="char-counter">{{ editForm.feature.length }}/1000</div>
                </div>
              </div>

              <!-- 联系方式 -->
              <div class="edit-section">
                <div class="section-header">
                  <h4 class="section-title">联系方式</h4>
                </div>
                <div class="edit-form-row">
                  <label class="edit-label">联系人 <span class="required">*</span></label>
                  <input 
                    v-model="editForm.contactName" 
                    type="text" 
                    class="edit-input"
                    placeholder="联系人姓名"
                    maxlength="20"
                  />
                </div>
                <div class="edit-form-row">
                  <label class="edit-label">联系电话 <span class="required">*</span></label>
                  <input 
                    v-model="editForm.contactPhone" 
                    type="tel" 
                    class="edit-input"
                    placeholder="11位手机号"
                    maxlength="11"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeEditModal">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="editSubmitting"
            @click="confirmEdit"
          >
            <span v-if="editSubmitting" class="loading-spinner-small"></span>
            <span v-else>保存修改</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 状态更新弹窗 -->
    <div v-if="showStatusModal" class="modal-overlay" @click.self="closeStatusModal">
      <div class="status-modal">
        <div class="modal-header">
          <h3 class="modal-title">更新物品状态</h3>
          <button class="modal-close" @click="closeStatusModal">×</button>
        </div>
        <div class="modal-body">
          <div class="current-item">
            <span class="item-name">{{ updatingItem?.name }}</span>
            <span class="current-status">当前：{{ updatingItem?.currentStatusName }}</span>
          </div>
          <div class="status-options">
            <div 
              v-for="status in availableStatuses" 
              :key="status.value"
              class="status-option"
              :class="{ active: newStatus === status.value }"
              @click="newStatus = status.value"
            >
              <div class="status-icon">{{ status.icon }}</div>
              <div class="status-info">
                <div class="status-name">{{ status.label }}</div>
                <div class="status-desc">{{ status.desc }}</div>
              </div>
            </div>
          </div>
          <div class="form-group" v-if="newStatus === 4">
            <label class="form-label">认领人信息</label>
            <input 
              v-model="statusRemark" 
              type="text" 
              class="form-input" 
              placeholder="请输入认领人姓名和联系方式..."
            />
          </div>
          <div class="form-group" v-if="newStatus === 7">
            <label class="form-label">归档说明 <span class="required">*</span></label>
            <textarea 
              v-model="statusRemark" 
              class="form-textarea"
              rows="3"
              placeholder="请说明归档原因，如：超过30天无人认领、移交保卫处等..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeStatusModal">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="!newStatus || (newStatus === 7 && !statusRemark.trim())"
            @click="confirmUpdateStatus"
          >
            确认更新
          </button>
        </div>
      </div>
    </div>

    <!-- 归档弹窗 -->
    <div v-if="showArchiveModal" class="modal-overlay" @click.self="closeArchiveModal">
      <div class="archive-modal">
        <div class="modal-header">
          <h3 class="modal-title">归档物品</h3>
          <button class="modal-close" @click="closeArchiveModal">×</button>
        </div>
        <div class="modal-body">
          <div class="archive-item">
            <span class="item-name">{{ archivingItem?.name }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">归档类型 <span class="required">*</span></label>
            <div class="archive-types">
              <button 
                v-for="type in archiveTypes" 
                :key="type"
                class="type-btn"
                :class="{ active: archiveType === type }"
                @click="archiveType = type"
              >
                {{ type }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">归档说明 <span class="required">*</span></label>
            <textarea 
              v-model="archiveDesc" 
              class="form-textarea"
              rows="3"
              placeholder="请详细说明归档原因和处理方式..."
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeArchiveModal">取消</button>
          <button 
            class="modal-btn archive-confirm-btn" 
            :disabled="!archiveType || !archiveDesc.trim()"
            @click="confirmArchive"
          >
            确认归档
          </button>
        </div>
      </div>
    </div>

    <!-- 认领申请列表弹窗 -->
    <div v-if="showClaimsModal" class="modal-overlay" @click.self="closeClaimsModal">
      <div class="claims-modal">
        <div class="modal-header">
          <h3 class="modal-title">认领申请审核</h3>
          <button class="modal-close" @click="closeClaimsModal">×</button>
        </div>
        <div class="modal-body">
          <div class="claims-item-info" v-if="claimsItem">
            <img :src="claimsItem.firstImageUrl || '/home/默认.jpg'" class="claims-item-image" />
            <div class="claims-item-detail">
              <div class="claims-item-name">{{ claimsItem.name }}</div>
              <div class="claims-item-status">当前状态：{{ claimsItem.currentStatusName }}</div>
            </div>
          </div>
          
          <div class="claims-list" v-if="claimsList.length > 0">
            <div 
              v-for="claim in claimsList" 
              :key="claim.claimId"
              class="claim-card"
            >
              <div class="claim-header">
                <div class="claim-user">
                  <div class="user-avatar">{{ claim.claimUserName?.[0] || '?' }}</div>
                  <div class="user-info">
                    <div class="user-name">{{ claim.claimUserName }}</div>
                    <div class="user-phone">{{ maskPhone(claim.claimUserPhone) }}</div>
                  </div>
                </div>
                <div class="claim-status" :class="'status-' + claim.status">
                  {{ claim.statusName }}
                </div>
              </div>
              <div class="claim-content">
                <div class="claim-label">认领说明：</div>
                <div class="claim-proof">{{ claim.proofFeature }}</div>
              </div>
              <div class="claim-time">申请时间：{{ claim.createTime }}</div>
              <div class="claim-actions" v-if="claim.status === 0">
                <button class="claim-btn approve" @click="auditClaim(claim.claimId, 1)">
                  ✓ 通过
                </button>
                <button class="claim-btn reject" @click="auditClaim(claim.claimId, 2)">
                  ✗ 驳回
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="claims-empty">
            <div class="empty-icon">📭</div>
            <div class="empty-text">暂无认领申请</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeClaimsModal">关闭</button>
        </div>
      </div>
    </div>

    <!-- 长期未认领物品弹窗 -->
    <div v-if="showUnclaimedModal" class="modal-overlay" @click.self="closeUnclaimedModal">
      <div class="unclaimed-modal">
        <div class="modal-header">
          <h3 class="modal-title">长期无人认领物品（超过30天）</h3>
          <button class="modal-close" @click="closeUnclaimedModal">×</button>
        </div>
        <div class="modal-body">
          <div class="unclaimed-list" v-if="unclaimedList.length > 0">
            <div 
              v-for="item in unclaimedList" 
              :key="item.itemId"
              class="unclaimed-item"
            >
              <div class="item-info">
                <div class="item-name">{{ item.name }}</div>
                <div class="item-location">📍 {{ item.locationName }}</div>
                <div class="item-time">发布于 {{ timeAgo(item.createTime) }}</div>
              </div>
              <button class="quick-archive-btn" @click="quickArchive(item)">
                归档
              </button>
            </div>
          </div>
          <div v-else class="unclaimed-empty">
            <div class="empty-icon">🎉</div>
            <div class="empty-text">暂无长期未认领物品</div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeUnclaimedModal">关闭</button>
          <button 
            v-if="unclaimedList.length > 0"
            class="modal-btn batch-archive-btn"
            @click="batchArchiveUnclaimed"
          >
            批量归档全部
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">确认删除</h3>
          <button class="modal-close" @click="closeDeleteModal">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-content">
            <div class="confirm-icon">⚠️</div>
            <p class="confirm-text">确定要删除「{{ deletingItem?.name }}」吗？</p>
            <p class="confirm-hint">删除后不可恢复，请谨慎操作！</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeDeleteModal">取消</button>
          <button class="modal-btn delete-confirm-btn" @click="confirmDeleteItem">
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- 图片预览 -->
    <div v-if="previewImageUrl" class="image-preview-overlay" @click.self="closeImagePreview">
      <img :src="previewImageUrl" class="preview-large" />
      <button class="preview-close" @click="closeImagePreview">×</button>
    </div>

    <!-- 认领申请驳回弹窗 -->
    <div v-if="showClaimRejectModal" class="modal-overlay" @click.self="closeClaimRejectModal">
      <div class="reject-modal">
        <div class="modal-header">
          <h3 class="modal-title">驳回认领申请</h3>
          <button class="modal-close" @click="closeClaimRejectModal">×</button>
        </div>
        <div class="modal-body">
          <div class="reject-content">
            <p class="reject-item-name">「{{ rejectingClaim?.claimUserName }}」的认领申请</p>
            <div class="form-group">
              <label class="form-label">驳回原因 <span class="required">*</span></label>
              <textarea 
                v-model="rejectReason" 
                class="form-textarea"
                placeholder="请详细说明驳回原因，如：信息不完整、照片不清晰、疑似虚假信息等..."
                rows="4"
              ></textarea>
              <div class="reason-options">
                <button 
                  v-for="reason in commonRejectReasons" 
                  :key="reason"
                  class="reason-tag"
                  @click="selectReason(reason)"
                >
                  {{ reason }}
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeClaimRejectModal">取消</button>
          <button 
            class="modal-btn reject-btn" 
            :disabled="submitting || !rejectReason.trim()"
            @click="confirmRejectClaim"
          >
            <span v-if="submitting" class="loading-spinner-small"></span>
            <span v-else>确认驳回</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import AdminNavigation from '../components/AdminNavigation.vue'

const router = useRouter()

/* ================= 数据状态 ================= */
const loading = ref(false)
const refreshing = ref(false)
const itemList = ref<any[]>([])

/* ================= 筛选参数 ================= */
const filterParams = reactive({
  status: '',
  itemCategory: '',
  locationId: '',
  keyword: '',
  sortField: 'createTime',
  sortOrder: 'desc'
})

/* ================= 分页信息 ================= */
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0,
  totalPages: 1
})

/* ================= 统计概览 ================= */
const overview = reactive({
  total: 0,
  approved: 0,
  matched: 0,
  claimed: 0,
  archived: 0,
  longTermUnclaimed: 0
})

/* ================= 批量选择 ================= */
const selectedItems = ref<number[]>([])

const isAllSelected = computed(() => {
  return itemList.value.length > 0 && selectedItems.value.length === itemList.value.length
})

/* ================= 弹窗状态 ================= */
const showDetailModal = ref(false)
const showStatusModal = ref(false)
const showArchiveModal = ref(false)
const showClaimsModal = ref(false)
const showUnclaimedModal = ref(false)
const showDeleteModal = ref(false)
const showClaimRejectModal = ref(false)
// 新增编辑弹窗状态
const showEditModal = ref(false)

const currentItem = ref<any>(null)
const currentItemImages = ref<string[]>([])
const currentImageIndex = ref(0)
const updatingItem = ref<any>(null)
const archivingItem = ref<any>(null)
const claimsItem = ref<any>(null)
const deletingItem = ref<any>(null)
const rejectingClaim = ref<any>(null)
const rejectReason = ref('')
const submitting = ref(false)

/* ================= 状态更新 ================= */
const newStatus = ref<number | null>(null)
const statusRemark = ref('')

const availableStatuses = [
  { value: 2, label: '已通过', icon: '✅', desc: '信息审核通过，正常展示' },
  { value: 3, label: '已匹配', icon: '🤝', desc: '找到匹配信息，等待认领确认' },
  { value: 4, label: '已认领', icon: '🎉', desc: '物品已被成功认领' },
  { value: 7, label: '已归档', icon: '📁', desc: '长期无人认领或已处理完毕' }
]

/* ================= 归档 ================= */
const archiveType = ref('')
const archiveDesc = ref('')
const archiveTypes = ['移交保卫处', '捐赠处理', '报废处理', '其他']

/* ================= 认领申请 ================= */
const claimsList = ref<any[]>([])
const unclaimedList = ref<any[]>([])

/* ================= 常用驳回原因 ================= */
const commonRejectReasons = [
  '信息不完整，缺少关键描述',
  '照片不清晰，无法辨认物品',
  '联系方式无效',
  '疑似虚假信息',
  '物品描述与实际不符',
  '重复认领'
]

/* ================= 图片预览 ================= */
const previewImageUrl = ref('')

/* ================= 编辑功能相关状态 ================= */
const editingItem = ref<any>(null)
const editSubmitting = ref(false)
const editForm = reactive({
  itemCategory: 1,
  itemType: 0,
  name: '',
  locationId: 0,
  locationDetail: '',
  pickupLocation: '',
  happenTime: '',
  feature: '',
  rewardAmount: 0,
  rewardDesc: '',
  contactName: '',
  contactPhone: ''
})

// 编辑弹窗中的级联选择器状态
const editSelectedFirstCategory = ref<number>(0)
const editSelectedSecondCategory = ref<number>(0)
const editSelectedCampus = ref<number>(0)
const editSelectedArea = ref<number>(0)
const editSelectedLocation = ref<number>(0)

// 分类和地点树数据
const categoryTree = ref<any[]>([])
const locationTree = ref<any[]>([])

// 计算属性：级联选择器选项
const firstCategories = computed(() => categoryTree.value)
const secondCategories = computed(() => {
  if (!editSelectedFirstCategory.value) return []
  const selectedFirst = categoryTree.value.find(cat => cat.id === editSelectedFirstCategory.value)
  return selectedFirst?.children || []
})

const campuses = computed(() => locationTree.value)
const areas = computed(() => {
  if (!editSelectedCampus.value) return []
  const selectedCampusNode = locationTree.value.find(loc => loc.id === editSelectedCampus.value)
  return selectedCampusNode?.children || []
})
const locations = computed(() => {
  if (!editSelectedArea.value) return []
  for (const campus of locationTree.value) {
    if (campus.children) {
      const selectedAreaNode = campus.children.find((area: any) => area.id === editSelectedArea.value)
      if (selectedAreaNode) {
        return selectedAreaNode.children || []
      }
    }
  }
  return []
})

// 编辑弹窗中的图片管理
const fileInput = ref<HTMLInputElement>()
const editImages = ref<Array<{ 
  file?: File;
  previewUrl: string;
  isOriginal?: boolean;
  originalId?: number;
}>>([])
const dragOver = ref(false)
const draggedImageIndex = ref<number | null>(null)

/* ================= 加载分类和地点树 ================= */
const loadCategoryTree = async () => {
  try {
    const res = await axios.get('/api/item/category/tree')
    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      categoryTree.value = res.data.data
    } else {
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

const loadLocationTree = async () => {
  try {
    const res = await axios.get('/api/item/location/tree')
    if (res.data.code === 200 && Array.isArray(res.data.data)) {
      locationTree.value = res.data.data
    } else {
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
        },
        {
          id: 3,
          name: '莫干山校区',
          children: [
            {
              id: 301,
              name: '教学楼',
              children: [
                { id: 30101, name: '教学楼 A' },
                { id: 30102, name: '教学楼 B' }
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

/* ================= 编辑弹窗级联选择器事件 ================= */
const onEditFirstCategoryChange = () => {
  editSelectedSecondCategory.value = 0
  editForm.itemType = 0
}

const onEditSecondCategoryChange = () => {
  if (editSelectedSecondCategory.value) {
    editForm.itemType = editSelectedSecondCategory.value
  }
}

const onEditCampusChange = () => {
  editSelectedArea.value = 0
  editSelectedLocation.value = 0
  editForm.locationId = 0
}

const onEditAreaChange = () => {
  editSelectedLocation.value = 0
  editForm.locationId = 0
}

const onEditLocationChange = () => {
  if (editSelectedLocation.value) {
    editForm.locationId = editSelectedLocation.value
  }
}

/* ================= 编辑弹窗图片管理 ================= */
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = true
}

const handleDragLeave = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = false
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = false
  
  const files = event.dataTransfer?.files
  if (files) {
    handleEditFiles(Array.from(files))
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return
  
  handleEditFiles(Array.from(files))
  target.value = ''
}

const handleEditFiles = (fileList: File[]) => {
  const remainingSlots = 5 - editImages.value.length
  if (remainingSlots <= 0) {
    alert('最多只能上传5张图片')
    return
  }
  
  const validFiles = fileList.slice(0, remainingSlots)
  
  validFiles.forEach(file => {
    if (!file.type.startsWith('image/')) {
      alert('只能上传图片文件')
      return
    }
    
    if (file.size > 5 * 1024 * 1024) {
      alert('图片大小不能超过5MB')
      return
    }
    
    const previewUrl = URL.createObjectURL(file)
    editImages.value.push({ 
      file: file, 
      previewUrl: previewUrl,
      isOriginal: false
    })
  })
}

const removeEditImage = (index: number) => {
  // 释放新图片的URL
  if (!editImages.value[index].isOriginal) {
    URL.revokeObjectURL(editImages.value[index].previewUrl)
  }
  
  editImages.value.splice(index, 1)
}

const handleDragStart = (index: number) => {
  draggedImageIndex.value = index
}

const handleDropSort = (dropIndex: number) => {
  if (draggedImageIndex.value === null || draggedImageIndex.value === dropIndex) return
  
  const temp = editImages.value[draggedImageIndex.value]
  editImages.value.splice(draggedImageIndex.value, 1)
  editImages.value.splice(dropIndex, 0, temp)
  
  draggedImageIndex.value = null
}

/* ================= 编辑功能核心方法 ================= */
const openEditModal = async (item: any) => {
  // 确保树数据已加载
  if (categoryTree.value.length === 0) await loadCategoryTree()
  if (locationTree.value.length === 0) await loadLocationTree()
  
  editingItem.value = item
  
  // 填充表单数据
  editForm.itemCategory = item.itemCategory
  editForm.itemType = item.itemType
  editForm.name = item.name
  editForm.locationId = item.locationId
  editForm.locationDetail = item.locationDetail || ''
  editForm.pickupLocation = item.pickupLocation || ''
  
  // 格式化时间
  if (item.happenTime) {
    let timeStr = item.happenTime
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
    editForm.happenTime = timeStr.substring(0, 16)
  } else {
    // 默认当前时间
    const now = new Date()
    editForm.happenTime = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}T${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  }
  
  editForm.feature = item.feature || ''
  editForm.rewardAmount = item.rewardAmount || 0
  editForm.rewardDesc = item.rewardDesc || ''
  editForm.contactName = item.contactName || ''
  editForm.contactPhone = item.contactPhone || ''
  
  // 设置分类选择器
  setupEditCategorySelectors(item.itemType)
  
  // 设置地点选择器
  setupEditLocationSelectors(item.locationId)
  
  // 加载图片
  await loadEditImages(item.itemId)
  
  showEditModal.value = true
}

const setupEditCategorySelectors = (itemType: number) => {
  // 查找对应的分类
  for (const firstCat of categoryTree.value) {
    if (firstCat.children) {
      for (const secondCat of firstCat.children) {
        if (secondCat.id === itemType) {
          editSelectedFirstCategory.value = firstCat.id
          editSelectedSecondCategory.value = secondCat.id
          return
        }
      }
    }
  }
}

const setupEditLocationSelectors = (locationId: number) => {
  // 查找对应的地点层级
  for (const campus of locationTree.value) {
    if (campus.children) {
      for (const area of campus.children) {
        if (area.children) {
          for (const location of area.children) {
            if (location.id === locationId) {
              editSelectedCampus.value = campus.id
              editSelectedArea.value = area.id
              editSelectedLocation.value = location.id
              return
            }
          }
        }
      }
    }
  }
}

const loadEditImages = async (itemId: number) => {
  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: itemId }
    })
    
    if (res.data.code === 200 && res.data.data.images) {
      editImages.value = []
      
      for (const image of res.data.data.images) {
        editImages.value.push({
          previewUrl: image.url,
          isOriginal: true,
          originalId: image.id
        })
      }
    } else {
      editImages.value = []
    }
  } catch (error) {
    console.error('加载图片失败:', error)
    editImages.value = []
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  editingItem.value = null
  
  // 清理图片URL，避免内存泄漏
  editImages.value.forEach(image => {
    if (!image.isOriginal && image.previewUrl) {
      URL.revokeObjectURL(image.previewUrl)
    }
  })
  editImages.value = []
  
  // 重置表单状态
  editSubmitting.value = false
}

const confirmEdit = async () => {
  if (!editingItem.value) return
  
  // 表单验证...
  if (!editForm.name.trim()) {
    alert('请输入物品名称')
    return
  }
  if (!editForm.itemType) {
    alert('请选择物品分类')
    return
  }
  if (!editForm.locationId) {
    alert('请选择地点')
    return
  }
  if (!editForm.happenTime) {
    alert('请选择时间')
    return
  }
  if (!editForm.feature.trim()) {
    alert('请输入特征描述')
    return
  }
  if (!editForm.contactName.trim()) {
    alert('请输入联系人姓名')
    return
  }
  if (!editForm.contactPhone.trim() || !/^1[3-9]\d{9}$/.test(editForm.contactPhone.trim())) {
    alert('请输入有效的手机号码')
    return
  }
  
  editSubmitting.value = true
  
  try {
    // 1. 更新物品信息
    const submitData = {
      name: editForm.name,
      itemType: editForm.itemType,
      locationId: editForm.locationId,
      locationDetail: editForm.locationDetail,
      pickupLocation: editForm.pickupLocation,
      happenTime: editForm.happenTime.replace('T', ' ') + ':00',
      feature: editForm.feature,
      rewardAmount: editForm.itemCategory === 1 ? (editForm.rewardAmount || 0) : 0,
      rewardDesc: editForm.itemCategory === 1 ? (editForm.rewardDesc || '') : '',
      contactName: editForm.contactName,
      contactPhone: editForm.contactPhone
    }
    
    const updateRes = await axios.put(`/api/item/${editingItem.value.itemId}`, submitData)
    
    if (updateRes.data.code !== 200) {
      throw new Error(updateRes.data.msg || '更新失败')
    }
    
    // 2. 更新图片（使用 try-catch 单独处理，不影响主流程）
    try {
      await updateEditImages(editingItem.value.itemId)
    } catch (imageError: any) {
      console.error('图片更新失败（非阻断）:', imageError)
      // 图片更新失败只警告，不阻断成功提示
      // 可选：alert('物品信息已保存，但图片更新失败，请稍后重试')
    }
    
    // 3. 刷新列表
    await loadItemList()
    
    // 4. 关闭弹窗并提示成功
    closeEditModal()
    alert('修改成功！')
    
  } catch (error: any) {
    console.error('更新失败:', error)
    alert(`更新失败: ${error.message || '网络错误'}`)
  } finally {
    editSubmitting.value = false
  }
}

const updateEditImages = async (itemId: number) => {
  // 如果没有图片，直接返回成功，不调用接口
  if (editImages.value.length === 0) {
    console.log('没有图片需要更新，跳过图片更新')
    return
  }
  
  try {
    const formData = new FormData()
    
    // 将所有图片添加到formData中
    for (let i = 0; i < editImages.value.length; i++) {
      const image = editImages.value[i]
      
      if (image.file) {
        // 新上传的图片，直接添加
        formData.append('images', image.file)
      } else if (image.isOriginal && image.previewUrl) {
        // 原始图片，需要从URL获取并转换为File对象
        try {
          const response = await fetch(image.previewUrl)
          if (response.ok) {
            const blob = await response.blob()
            const file = new File([blob], `image_${image.originalId || i}.jpg`, { type: blob.type })
            formData.append('images', file)
          } else {
            console.warn(`无法获取原始图片: ${image.previewUrl}`, response.status)
          }
        } catch (error) {
          console.error(`获取原始图片失败 ${i}:`, error)
          // 继续处理其他图片，不中断
        }
      }
    }
    
    // 检查是否有实际要上传的文件
    const filesToUpload = formData.getAll('images')
    if (filesToUpload.length === 0) {
      console.log('没有有效的图片文件需要上传')
      return
    }
    
    // 调用图片更新接口
    await axios.post(`/api/item/${itemId}/images/update`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  } catch (error) {
    console.error('图片更新失败:', error)
    // 抛出错误让上层处理，但不阻断主流程
    throw new Error('图片更新失败，但物品信息已保存')
  }
}

/* ================= 加载物品列表 ================= */
const loadItemList = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/item/admin/list', {
      params: {
        page: pagination.page,
        size: pagination.size,
        status: filterParams.status || undefined,
        itemCategory: filterParams.itemCategory || undefined,
        locationId: filterParams.locationId || undefined,
        keyword: filterParams.keyword || undefined,
        sortField: filterParams.sortField,
        sortOrder: filterParams.sortOrder
      }
    })
    
    if (res.data.code === 200) {
      itemList.value = res.data.data.list || []
      pagination.total = res.data.data.total || 0
      pagination.totalPages = Math.ceil(pagination.total / pagination.size)
      
      // 更新统计
      if (res.data.data.statistics) {
        const s = res.data.data.statistics
        overview.approved = s['已通过'] || 0
        overview.matched = s['已匹配'] || 0
        overview.claimed = s['已认领'] || 0
        overview.archived = s['已归档'] || 0
        overview.total = overview.approved + overview.matched + overview.claimed + 
                         overview.archived + (s['待审核'] || 0) + (s['已驳回'] || 0) + (s['已取消'] || 0)
      }
    }
  } catch (error) {
    console.error('加载物品列表失败:', error)
    // 模拟数据
    itemList.value = [
      {
        itemId: 1,
        name: '黑色蓝牙耳机',
        itemCategory: 1,
        currentStatus: 2,
        currentStatusName: '已通过',
        locationName: '健行楼 A108',
        rewardAmount: 50,
        claimCount: 2,
        pendingClaimCount: 1,
        createTime: '2026-02-28 15:00:00',
        firstImageUrl: null
      },
      {
        itemId: 2,
        name: '校园卡（李四）',
        itemCategory: 2,
        currentStatus: 3,
        currentStatusName: '已匹配',
        locationName: '图书馆一楼',
        rewardAmount: 0,
        claimCount: 1,
        pendingClaimCount: 0,
        createTime: '2026-02-27 10:30:00',
        firstImageUrl: null
      }
    ]
    overview.total = 2
    overview.approved = 1
    overview.matched = 1
  } finally {
    loading.value = false
  }
}

/* ================= 加载长期未认领统计 ================= */
const loadUnclaimedStats = async () => {
  try {
    const res = await axios.get('/api/item/unclaimed/long-term', {
      params: { days: 30, page: 1, size: 1 }
    })
    if (res.data.code === 200) {
      overview.longTermUnclaimed = res.data.data.total || 0
    }
  } catch (error) {
    console.error('加载未认领统计失败:', error)
    overview.longTermUnclaimed = 3
  }
}

/* ================= 刷新列表 ================= */
const refreshList = async () => {
  refreshing.value = true
  selectedItems.value = []
  await loadItemList()
  await loadUnclaimedStats()
  setTimeout(() => {
    refreshing.value = false
  }, 500)
}

/* ================= 分页切换 ================= */
const changePage = (page: number) => {
  if (page < 1 || page > pagination.totalPages) return
  pagination.page = page
  loadItemList()
}

/* ================= 快速筛选 ================= */
const quickFilter = (status: string) => {
  filterParams.status = status === 'all' ? '' : status
  pagination.page = 1
  loadItemList()
}

/* ================= 批量选择 ================= */
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = itemList.value.map(item => item.itemId)
  }
}

const toggleSelectItem = (itemId: number) => {
  const index = selectedItems.value.indexOf(itemId)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(itemId)
  }
}

/* ================= 查看详情 ================= */
const viewDetail = async (item: any) => {
  currentItem.value = item
  currentImageIndex.value = 0
  
  // 加载物品详情获取图片
  try {
    const res = await axios.get('/api/item/detail', {
      params: { itemId: item.itemId }
    })
    
    if (res.data.code === 200) {
      const detail = res.data.data
      currentItem.value = { ...item, ...detail.item }
      
      // 处理图片
      if (detail.images && detail.images.length > 0) {
        currentItemImages.value = detail.images.map((img: any) => img.url)
      } else if (item.firstImageUrl) {
        currentItemImages.value = [item.firstImageUrl]
      } else {
        currentItemImages.value = []
      }
    }
  } catch (error) {
    console.error('加载详情失败:', error)
    currentItemImages.value = item.firstImageUrl ? [item.firstImageUrl] : []
  }
  
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentItem.value = null
  currentItemImages.value = []
}

/* ================= 状态更新 ================= */
const openStatusModal = (item: any) => {
  updatingItem.value = item
  newStatus.value = null
  statusRemark.value = ''
  showStatusModal.value = true
}

const closeStatusModal = () => {
  showStatusModal.value = false
  updatingItem.value = null
  newStatus.value = null
  statusRemark.value = ''
}

const confirmUpdateStatus = async () => {
  if (!updatingItem.value || !newStatus.value) return
  
  try {
    const res = await axios.post(`/api/item/${updatingItem.value.itemId}/status`, {
      status: newStatus.value,
      remark: statusRemark.value
    })
    
    if (res.data.code === 200) {
      await loadItemList()
      closeStatusModal()
    }
  } catch (error) {
    console.error('更新状态失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 归档 ================= */
const canArchive = (item: any) => {
  return item.currentStatus === 2 || item.currentStatus === 3 || 
         (item.currentStatus !== 4 && item.currentStatus !== 7)
}

const openArchiveModal = (item: any) => {
  archivingItem.value = item
  archiveType.value = ''
  archiveDesc.value = ''
  showArchiveModal.value = true
}

const closeArchiveModal = () => {
  showArchiveModal.value = false
  archivingItem.value = null
  archiveType.value = ''
  archiveDesc.value = ''
}

const confirmArchive = async () => {
  if (!archivingItem.value || !archiveType.value || !archiveDesc.value.trim()) return
  
  try {
    const res = await axios.post(`/api/item/${archivingItem.value.itemId}/archive`, {
      archiveDesc: `[${archiveType.value}] ${archiveDesc.value}`
    })
    
    if (res.data.code === 200) {
      await loadItemList()
      await loadUnclaimedStats()
      closeArchiveModal()
    }
  } catch (error) {
    console.error('归档失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 批量归档 ================= */
const batchArchive = async () => {
  if (selectedItems.value.length === 0) return
  
  const confirm = window.confirm(`确定要批量归档 ${selectedItems.value.length} 个物品吗？`)
  if (!confirm) return
  
  try {
    const res = await axios.post('/api/item/batch/archive', {
      itemIds: selectedItems.value,
      archiveDesc: '管理员批量归档',
      archiveType: '批量处理'
    })
    
    if (res.data.code === 200) {
      selectedItems.value = []
      await loadItemList()
      await loadUnclaimedStats()
    }
  } catch (error) {
    console.error('批量归档失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 认领申请审核 ================= */
const viewClaims = async (item: any) => {
  claimsItem.value = item
  showClaimsModal.value = true
  
  try {
    const res = await axios.get('/api/item/claim/list', {
      params: { itemId: item.itemId, page: 1, size: 100 }
    })
    
    if (res.data.code === 200) {
      claimsList.value = res.data.data.list || []
    }
  } catch (error) {
    console.error('加载认领申请失败:', error)
    claimsList.value = []
  }
}

const closeClaimsModal = () => {
  showClaimsModal.value = false
  claimsItem.value = null
  claimsList.value = []
}

const auditClaim = async (claimId: number, status: number) => {
  if (status === 2) {
    // 驳回，先打开驳回弹窗
    const claim = claimsList.value.find(c => c.claimId === claimId)
    if (claim) {
      openClaimRejectModal(claim)
    }
  } else {
    // 通过，直接提交
    try {
      const res = await axios.post(`/api/item/claim/${claimId}/audit`, { status })
      
      if (res.data.code === 200) {
        // 刷新认领列表和物品列表
        await viewClaims(claimsItem.value)
        await loadItemList()
      }
    } catch (error) {
      console.error('审核认领申请失败:', error)
      alert('操作失败，请重试')
    }
  }
}

/* ================= 认领申请驳回 ================= */
const openClaimRejectModal = (claim: any) => {
  rejectingClaim.value = claim
  rejectReason.value = ''
  showClaimRejectModal.value = true
}

const closeClaimRejectModal = () => {
  showClaimRejectModal.value = false
  rejectingClaim.value = null
  rejectReason.value = ''
}

const selectReason = (reason: string) => {
  rejectReason.value = reason
}

const confirmRejectClaim = async () => {
  if (!rejectingClaim.value || !rejectReason.value.trim()) return
  
  submitting.value = true
  try {
    const res = await axios.post(`/api/item/claim/${rejectingClaim.value.claimId}/audit`, {
      status: 2, // 驳回
      rejectReason: rejectReason.value.trim()
    })
    
    if (res.data.code === 200) {
      // 刷新认领列表和物品列表
      await viewClaims(claimsItem.value)
      await loadItemList()
      closeClaimRejectModal()
    }
  } catch (error) {
    console.error('驳回认领申请失败:', error)
    alert('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

/* ================= 长期未认领物品 ================= */
const openUnclaimedModal = async () => {
  showUnclaimedModal.value = true
  
  try {
    const res = await axios.get('/api/item/unclaimed/long-term', {
      params: { days: 30, page: 1, size: 100 }
    })
    
    if (res.data.code === 200) {
      unclaimedList.value = res.data.data.list || []
    }
  } catch (error) {
    console.error('加载未认领物品失败:', error)
    unclaimedList.value = []
  }
}

const closeUnclaimedModal = () => {
  showUnclaimedModal.value = false
  unclaimedList.value = []
}

const quickArchive = (item: any) => {
  closeUnclaimedModal()
  openArchiveModal(item)
}

const batchArchiveUnclaimed = async () => {
  if (unclaimedList.value.length === 0) return
  
  const confirm = window.confirm(`确定要批量归档 ${unclaimedList.value.length} 个长期未认领物品吗？`)
  if (!confirm) return
  
  const itemIds = unclaimedList.value.map(item => item.itemId)
  
  try {
    const res = await axios.post('/api/item/batch/archive', {
      itemIds,
      archiveDesc: '超过30天无人认领，系统自动归档',
      archiveType: '超期归档'
    })
    
    if (res.data.code === 200) {
      closeUnclaimedModal()
      await loadItemList()
      await loadUnclaimedStats()
    }
  } catch (error) {
    console.error('批量归档失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 删除 ================= */
const confirmDelete = (item: any) => {
  deletingItem.value = item
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  deletingItem.value = null
}

const confirmDeleteItem = async () => {
  if (!deletingItem.value) return
  
  try {
    const res = await axios.delete(`/api/item/${deletingItem.value.itemId}/delete`)
    
    if (res.data.code === 200) {
      await loadItemList()
      closeDeleteModal()
    }
  } catch (error) {
    console.error('删除失败:', error)
    alert('操作失败，请重试')
  }
}

const batchDelete = async () => {
  if (selectedItems.value.length === 0) return
  
  const confirm = window.confirm(`确定要删除 ${selectedItems.value.length} 个物品吗？此操作不可恢复！`)
  if (!confirm) return
  
  // 逐个删除
  try {
    for (const itemId of selectedItems.value) {
      await axios.delete(`/api/item/${itemId}/delete`)
    }
    selectedItems.value = []
    await loadItemList()
  } catch (error) {
    console.error('批量删除失败:', error)
    alert('操作失败，请重试')
  }
}

/* ================= 图片预览 ================= */
const previewImage = (url: string | null) => {
  if (!url) return
  previewImageUrl.value = url
}

const closeImagePreview = () => {
  previewImageUrl.value = ''
}

/* ================= 工具函数 ================= */
const getStatusClass = (status: number) => {
  const classMap: Record<number, string> = {
    1: 'status-pending',
    2: 'status-approved',
    3: 'status-matched',
    4: 'status-claimed',
    5: 'status-rejected',
    6: 'status-canceled',
    7: 'status-archived'
  }
  return classMap[status] || ''
}

const formatDate = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const timeAgo = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  return `${Math.floor(diff / 2592000)}个月前`
}

const maskPhone = (phone: string) => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const truncateText = (text: string, length: number) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

/* ================= 地点解析函数 ================= */
const getLocationCampus = (item: any) => {
  const locationId = item.locationId || 0
  
  // 根据locationId的前缀判断校区
  // 1xxxx = 朝晖校区, 2xxxx = 屏峰校区, 3xxxx = 莫干山校区, 4xxxx = 西湖校区
  const idStr = String(locationId)
  
  if (idStr.startsWith('1')) {
    return '朝晖校区'
  } else if (idStr.startsWith('2')) {
    return '屏峰校区'
  } else if (idStr.startsWith('3')) {
    return '莫干山校区'
  } else if (idStr.startsWith('4')) {
    return '西湖校区'
  }
  
  // 如果无法从locationId判断，尝试从locationName中提取
  const locationName = item.locationName || ''
  const campusPatterns = ['屏峰校区', '朝晖校区', '莫干山校区', '西湖校区']
  
  for (const campus of campusPatterns) {
    if (locationName.includes(campus)) {
      return campus
    }
  }
  
  return '未知校区'
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadItemList()
  loadUnclaimedStats()
  // 预加载分类和地点树
  loadCategoryTree()
  loadLocationTree()
})
</script>

<style scoped>
/* 基础布局 */
.item-manage-page {
  width: 100vw;
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
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
  min-height: 100vh;
  padding: 24px 28px;
  margin-left: 288px;
  max-width: calc(100vw - 288px);
  box-sizing: border-box;
}

/* 页面标题 */
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

/* 统计卡片 */
.stats-section {
  margin-bottom: 25px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 15px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 20px 15px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-card.highlight {
  border-color: rgba(76, 175, 80, 0.4);
}

.stat-card.warning {
  border-color: rgba(255, 152, 0, 0.4);
}

.stat-card.success {
  border-color: rgba(33, 150, 243, 0.4);
}

.stat-card.danger {
  border-color: rgba(244, 67, 54, 0.4);
}

.stat-card.info {
  border-color: rgba(156, 39, 176, 0.4);
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.stat-value {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: #a67c52;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

/* 工具栏 */
.toolbar-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  outline: none;
}

.filter-select:focus {
  border-color: rgba(243, 129, 129, 0.7);
}

.search-box {
  display: flex;
  gap: 8px;
}

.search-input {
  width: 250px;
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
}

.search-input::placeholder {
  color: rgba(166, 124, 82, 0.5);
}

.search-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-count {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
}

.batch-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.batch-btn.archive-btn {
  background: linear-gradient(to right, #ff9800, #f57c00);
  color: white;
}

.batch-btn.delete-btn {
  background: linear-gradient(to right, #f44336, #d32f2f);
  color: white;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.refresh-icon {
  font-size: 16px;
  transition: transform 0.5s ease;
}

.refresh-icon.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 列表区域 */
.list-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  min-height: 400px;
}

/* 加载和空状态 */
.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(166, 124, 82, 0.2);
  border-top-color: #a67c52;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: #a67c52;
  margin-bottom: 12px;
  font-weight: 600;
}

.empty-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: rgba(166, 124, 82, 0.7);
}

/* 数据表格 */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-family: "Comic Sans MS", cursive;
}

.data-table th {
  background: rgba(166, 124, 82, 0.1);
  padding: 15px 12px;
  text-align: left;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
  border-bottom: 2px solid rgba(166, 124, 82, 0.2);
  white-space: nowrap;
}

.data-table td {
  padding: 15px 12px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
  font-size: 14px;
  color: rgba(166, 124, 82, 0.9);
  vertical-align: top;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.3);
}

.row-selected {
  background: rgba(243, 129, 129, 0.1) !important;
}

.col-checkbox { width: 40px; }
.col-id { width: 60px; }
.col-type { width: 80px; }
.col-image { width: 80px; }
.col-info { min-width: 150px; }
.col-status { width: 120px; }
.col-claims { width: 120px; }
.col-time { width: 120px; }
.col-actions { min-width: 200px; }

/* 类型标签 */
.type-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.lost-tag {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
}

.found-tag {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
}

/* 状态标签 */
.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}

.status-pending { background: #ff9800; }
.status-approved { background: #4caf50; }
.status-matched { background: #2196f3; }
.status-claimed { background: #9c27b0; }
.status-rejected { background: #f44336; }
.status-canceled { background: #9e9e9e; }
.status-archived { background: #795548; }

.archive-desc {
  font-size: 11px;
  color: rgba(166, 124, 82, 0.7);
  cursor: help;
}

/* 认领申请 */
.claim-badge {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(to right, #ff9800, #f57c00);
  color: white;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.claim-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.claim-info {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.claim-empty {
  color: rgba(166, 124, 82, 0.4);
}

/* 操作按钮 */
.action-btns {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.view-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

/* 新增编辑按钮样式 */
.edit-btn {
  background: linear-gradient(to right, #4caf50, #8bc34a);
  color: white;
}

.status-btn {
  background: linear-gradient(to right, #2196f3, #21cbf3);
  color: white;
}

.claim-btn {
  background: linear-gradient(to right, #ff9800, #ffc107);
  color: white;
}

.archive-btn {
  background: linear-gradient(to right, #795548, #8d6e63);
  color: white;
}

.delete-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.page-btn {
  padding: 10px 20px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.6);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
}

/* 模态框样式 */
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
  max-height: 60vh;
  overflow-y: auto;
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
}

/* ==================== 新增：编辑弹窗样式 ==================== */
.edit-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.edit-content {
  display: flex;
  gap: 25px;
}

.edit-left-column {
  flex: 0 0 300px;
}

.edit-right-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.edit-section {
  background: rgba(166, 124, 82, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(166, 124, 82, 0.1);
}

.edit-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.edit-section .section-title {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
  margin: 0;
}

.edit-section .section-subtitle {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

/* 编辑表单样式 */
.edit-form-row {
  margin-bottom: 15px;
}

.edit-form-row:last-child {
  margin-bottom: 0;
}

.edit-label {
  display: block;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  margin-bottom: 6px;
  font-weight: 500;
}

.edit-label .required {
  color: #ff4d4f;
}

.edit-input,
.edit-select,
.edit-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.6);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

.edit-input:focus,
.edit-select:focus,
.edit-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

.edit-input::placeholder,
.edit-textarea::placeholder {
  color: rgba(166, 124, 82, 0.5);
}

.edit-textarea {
  resize: vertical;
  min-height: 100px;
}

.datetime-input {
  font-size: 14px;
}

.currency-input {
  position: relative;
}

.currency-symbol {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: #a67c52;
  font-weight: 500;
}

.reward-input {
  padding-left: 28px;
}

.char-counter {
  text-align: right;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin-top: 5px;
}

/* 类型显示 */
.edit-type-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.lost-badge {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
}

.found-badge {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
}

.type-hint {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

/* 级联选择器 */
.edit-cascader {
  display: flex;
  gap: 10px;
}

.edit-cascader.location-cascader {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}

.cascader-level {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.cascader-label {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

/* 图片上传区域 */
.upload-area {
  border: 2px dashed rgba(166, 124, 82, 0.4);
  border-radius: 12px;
  padding: 30px 20px;
  background: rgba(255, 255, 255, 0.3);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 15px;
}

.upload-area:hover {
  border-color: rgba(243, 129, 129, 0.6);
  background: rgba(255, 255, 255, 0.5);
}

.upload-area.drag-over {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.upload-icon {
  font-size: 36px;
  margin-bottom: 10px;
}

.upload-text {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  margin-bottom: 5px;
  font-weight: 500;
}

.upload-hint {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin: 0;
}

.file-input {
  display: none;
}

/* 编辑图片网格 */
.edit-image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.edit-grid-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  cursor: move;
}

.edit-grid-item:hover .edit-grid-overlay {
  opacity: 1;
}

.edit-grid-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-grid-overlay {
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

.edit-grid-delete-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: #ff4d4f;
  color: white;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.edit-grid-delete-btn:hover {
  background: #ff7875;
  transform: scale(1.1);
}

.edit-grid-sort {
  position: absolute;
  top: 5px;
  left: 5px;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: move;
}

.edit-grid-index {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(243, 129, 129, 0.8);
  color: white;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

/* 状态更新弹窗特有样式 */
.status-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.current-item {
  background: rgba(166, 124, 82, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
  display: block;
  margin-bottom: 5px;
}

.current-status {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

.status-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.status-option {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.status-option:hover {
  border-color: rgba(243, 129, 129, 0.4);
  background: rgba(243, 129, 129, 0.05);
}

.status-option.active {
  border-color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.status-icon {
  font-size: 24px;
}

.status-info {
  flex: 1;
}

.status-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 3px;
}

.status-desc {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

/* 归档弹窗 */
.archive-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.archive-item {
  text-align: center;
  margin-bottom: 20px;
}

.archive-types {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.type-btn {
  padding: 8px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.type-btn:hover,
.type-btn.active {
  border-color: #f38181;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

/* 认领申请弹窗 */
.claims-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.claims-item-info {
  display: flex;
  gap: 15px;
  align-items: center;
  background: rgba(166, 124, 82, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.claims-item-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
}

.claims-item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
}

.claims-item-status {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

.claims-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.claim-card {
  border: 1.6px solid rgba(166, 124, 82, 0.2);
  border-radius: 12px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.5);
}

.claim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.claim-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  font-weight: 600;
}

.user-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  font-weight: 600;
}

.user-phone {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.claim-status {
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.claim-status.status-0 { background: #ff9800; }
.claim-status.status-1 { background: #4caf50; }
.claim-status.status-2 { background: #f44336; }

.claim-content {
  margin-bottom: 10px;
}

.claim-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 4px;
}

.claim-proof {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(166, 124, 82, 0.1);
  padding: 10px;
  border-radius: 8px;
}

.claim-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin-bottom: 12px;
}

.claim-actions {
  display: flex;
  gap: 10px;
}

.claim-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.claim-btn.approve {
  background: linear-gradient(to right, #4caf50, #8bc34a);
  color: white;
}

.claim-btn.reject {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

/* 长期未认领弹窗 */
.unclaimed-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 70vh;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.unclaimed-list {
  max-height: 50vh;
  overflow-y: auto;
}

.unclaimed-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.unclaimed-item:last-child {
  border-bottom: none;
}

.item-info {
  flex: 1;
}

.item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 4px;
}

.item-location,
.item-time {
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.quick-archive-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-archive-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

/* 确认弹窗 */
.confirm-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* 认领驳回弹窗 */
.claim-reject-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.reject-claim-info {
  background: rgba(166, 124, 82, 0.1);
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.reject-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reason-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.reason-btn {
  padding: 8px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.4);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.4);
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reason-btn:hover,
.reason-btn.active {
  border-color: #f44336;
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.confirm-content {
  text-align: center;
  padding: 20px;
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
  color: #f44336;
}

/* 按钮样式 */
.cancel-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1px solid rgba(166, 124, 82, 0.3);
}

.confirm-btn {
  background: linear-gradient(to right, #2196f3, #21cbf3);
  color: white;
}

.archive-confirm-btn {
  background: linear-gradient(to right, #795548, #8d6e63);
  color: white;
}

.delete-confirm-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.batch-archive-btn {
  background: linear-gradient(to right, #ff9800, #f57c00);
  color: white;
}

/* 图片预览 */
.image-preview {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  border: 1px solid rgba(166, 124, 82, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.image-preview:hover {
  border-color: rgba(243, 129, 129, 0.5);
  transform: scale(1.05);
}

.thumb-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.5);
}

/* 详情弹窗 */
.detail-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.detail-content {
  display: flex;
  gap: 20px;
}

.detail-images {
  flex: 0 0 300px;
}

.image-main {
  width: 100%;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(166, 124, 82, 0.1);
  margin-bottom: 12px;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-thumbs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.thumb.active {
  border-color: rgba(243, 129, 129, 0.7);
}

.thumb:hover {
  transform: scale(1.05);
}

.detail-info {
  flex: 1;
}

.info-row {
  margin-bottom: 15px;
}

.info-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
  display: block;
  margin-bottom: 4px;
}

.info-value {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  word-break: break-word;
}

.info-value.description {
  line-height: 1.5;
}

.info-value.reward {
  color: #f44336;
  font-weight: 500;
}

/* 物品信息列样式 */
.info-name {
  font-weight: 600;
  color: #a67c52;
  font-size: 14px;
  margin-bottom: 4px;
}

.info-campus {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.85);
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-location {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-reward {
  font-size: 12px;
  color: #ff9800;
  font-weight: 600;
}

/* 长期未认领物品列表中的校区样式 */
.item-campus {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.85);
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.preview-large {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  border-radius: 8px;
}

.preview-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.preview-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 驳回弹窗 */
.reject-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.reject-content {
  padding: 10px;
}

.reject-item-name {
  font-family: "Comic Sans MS", cursive;
  font-size: 16px;
  color: #a67c52;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
}

.reason-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.reason-tag {
  padding: 6px 12px;
  border: 1px solid rgba(166, 124, 82, 0.3);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
}

.reason-tag:hover {
  border-color: #f38181;
  color: #f38181;
  background: rgba(243, 129, 129, 0.1);
}

.reject-btn {
  background: linear-gradient(to right, #f44336, #ef5350);
  color: white;
}

.reject-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载动画小尺寸 */
.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 5px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  /* 编辑弹窗响应式 */
  .edit-content {
    flex-direction: column;
  }
  
  .edit-left-column {
    flex: 1;
    width: 100%;
  }
  
  .edit-image-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 15px 10px;
  }

  .stat-value {
    font-size: 20px;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .action-row {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .data-table th,
  .data-table td {
    padding: 10px 8px;
    font-size: 12px;
  }

  .col-checkbox,
  .col-id {
    display: none;
  }

  .action-btns {
    flex-direction: column;
    gap: 4px;
  }

  .action-btn {
    padding: 8px;
    font-size: 11px;
  }
  
  /* 编辑弹窗移动端适配 */
  .edit-modal {
    width: 95%;
    max-height: 95vh;
  }
  
  .edit-section {
    padding: 15px;
  }
  
  .edit-cascader.location-cascader {
    grid-template-columns: 1fr;
  }
  
  .edit-image-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>