<!-- src/views/system-admin/pages/AccountManageView.vue -->
<template>
  <div class="account-manage-page">
    <!-- 背景 -->
    <div class="background-container">
      <div class="solid-background"></div>
    </div>

    <!-- 整体布局 -->
    <div class="layout-container">
      <!-- 左侧导航 -->
      <SysAdminNavigation 
        subtitle="账号管理"
        active-nav="账号管理"
        @logout="handleLogout"
      />

      <!-- 右侧主内容 -->
      <main class="main-content">
        <!-- 页面标题 -->
        <section class="page-header">
          <h1 class="page-title">账号与权限管理</h1>
          <p class="page-subtitle">管理学生、教师、管理员账号，配置权限，发送系统通知</p>
        </section>

        <!-- 标签页 -->
        <section class="account-tabs">
          <div class="tab-buttons">
            <button 
              v-for="tab in tabs" 
              :key="tab.key"
              class="tab-btn"
              :class="{ active: currentTab === tab.key }"
              @click="switchTab(tab.key)"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-text">{{ tab.label }}</span>
              <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
            </button>
          </div>
        </section>

        <!-- 用户管理 -->
        <section v-if="currentTab === 'users'" class="account-section">
          <!-- 统计卡片 -->
          <div class="stats-row">
            <div class="stat-mini">
              <span class="stat-icon"></span>
              <div class="stat-info">
                <span class="stat-value">{{ userStats.student }}</span>
                <span class="stat-label">学生</span>
              </div>
            </div>
            <div class="stat-mini">
              <span class="stat-icon"></span>
              <div class="stat-info">
                <span class="stat-value">{{ userStats.teacher }}</span>
                <span class="stat-label">教师</span>
              </div>
            </div>
            <div class="stat-mini">
              <span class="stat-icon"></span>
              <div class="stat-info">
                <span class="stat-value">{{ userStats.total }}</span>
                <span class="stat-label">总用户</span>
              </div>
            </div>
            <div class="stat-mini highlight">
              <span class="stat-icon"></span>
              <div class="stat-info">
                <span class="stat-value">{{ userStats.active }}</span>
                <span class="stat-label">活跃</span>
              </div>
            </div>
          </div>

          <!-- 筛选工具栏 -->
          <div class="toolbar">
            <div class="toolbar-left">
              <select v-model="userFilter.role" class="filter-select" @change="loadUsers">
                <option value="">全部角色</option>
                <option value="1">学生</option>
                <option value="2">教师</option>
              </select>
              <select v-model="userFilter.status" class="filter-select" @change="loadUsers">
                <option value="">全部状态</option>
                <option value="1">正常</option>
                <option value="0">禁用</option>
              </select>
              <div class="search-box">
                <input 
                  v-model="userFilter.keyword"
                  type="text" 
                  class="search-input"
                  placeholder="搜索姓名/学号/手机号..."
                  @keyup.enter="loadUsers"
                />
                <button class="search-btn" @click="loadUsers">搜索</button>
              </div>
            </div>
            <div class="toolbar-right">
              <button class="action-btn secondary" @click="exportUsers">
                导出
              </button>
              <button class="action-btn primary" @click="openUserModal()">
                ➕ 新增用户
              </button>
            </div>
          </div>

          <!-- 用户表格 -->
          <div class="data-table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th class="col-checkbox">
                    <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll">
                  </th>
                  <th class="col-id">ID</th>
                  <th class="col-info">用户信息</th>
                  <th class="col-role">角色</th>
                  <th class="col-contact">联系方式</th>
                  <th class="col-status">状态</th>
                  <th class="col-time">注册时间</th>
                  <th class="col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="user in userList" 
                  :key="user.userId"
                  :class="{ 'row-selected': selectedUsers.includes(user.userId) }"
                >
                  <td class="col-checkbox">
                    <input 
                      type="checkbox" 
                      :checked="selectedUsers.includes(user.userId)"
                      @change="toggleSelectUser(user.userId)"
                    >
                  </td>
                  <td class="col-id">#{{ user.userId }}</td>
                  <td class="col-info">
                    <div class="user-name">{{ user.realName }}</div>
                    <div class="user-no">{{ user.username || '-' }}</div>
                  </td>
                  <td class="col-role">
                    <span class="role-tag" :class="'role-' + user.role">
                      {{ user.role === 1 ? '学生' : user.role === 2 ? '教师' : user.roleName }}
                    </span>
                  </td>
                  <td class="col-contact">
                    <div class="contact-phone">{{ maskPhone(user.phone) }}</div>
                  </td>
                  <td class="col-status">
                    <span class="status-badge" :class="{ active: user.status === 1 }">
                      {{ user.status === 1 ? '正常' : '禁用' }}
                    </span>
                  </td>
                  <td class="col-time">{{ formatDate(user.createTime) }}</td>
                  <td class="col-actions">
                    <div class="action-group">
                      <button class="icon-action" @click="viewUserDetail(user)" title="查看">查看</button>
                      <button class="icon-action" @click="openUserModal(user)" title="编辑">编辑</button>
                      <button 
                        class="icon-action" 
                        :class="{ danger: user.status === 1 }"
                        @click="toggleUserStatus(user)"
                        :title="user.status === 1 ? '禁用' : '启用'"
                      >
                        {{ user.status === 1 ? '禁用' : '启用' }}
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
                :disabled="userPagination.page === 1"
                @click="changeUserPage(userPagination.page - 1)"
              >
                上一页
              </button>
              <span class="page-info">
                第 {{ userPagination.page }} 页 / 共 {{ userPagination.totalPages }} 页
              </span>
              <button 
                class="page-btn" 
                :disabled="userPagination.page >= userPagination.totalPages"
                @click="changeUserPage(userPagination.page + 1)"
              >
                下一页
              </button>
            </div>
          </div>

          <!-- 批量操作栏 -->
          <div v-if="selectedUsers.length > 0" class="batch-bar">
            <span class="batch-info">已选择 {{ selectedUsers.length }} 项</span>
            <div class="batch-actions">
              <button class="batch-btn" @click="batchEnableUsers">批量启用</button>
              <button class="batch-btn warning" @click="batchDisableUsers">批量禁用</button>
              <button class="batch-btn danger" @click="batchDeleteUsers">批量删除</button>
            </div>
          </div>
        </section>

        <!-- 管理员管理 -->
        <section v-if="currentTab === 'admins'" class="account-section">
          <!-- 管理员统计 -->
          <div class="admin-stats">
            <div class="admin-stat-card" v-for="stat in adminStats" :key="stat.label">
              <div class="admin-stat-icon"></div>
              <div class="admin-stat-value">{{ stat.value }}</div>
              <div class="admin-stat-label">{{ stat.label }}</div>
            </div>
          </div>

          <!-- 管理员列表 -->
          <div class="admin-list">
            <div class="section-header">
              <h3 class="section-title">失物招领管理员</h3>
              <button class="add-admin-btn" @click="openAdminModal()">
                新增管理员
              </button>
            </div>

            <div class="admin-grid">
              <div 
                v-for="admin in adminList" 
                :key="admin.adminId"
                class="admin-card"
                :class="{ disabled: admin.status === 0 }"
              >
                <div class="admin-header">
                  <div class="admin-status" :class="{ active: admin.status === 1 }">
                    {{ admin.status === 1 ? '在职' : '停用' }}
                  </div>
                </div>
                <div class="admin-body">
                  <h4 class="admin-name">{{ admin.realName }}</h4>
                  <p class="admin-account">{{ admin.username }}</p>
                  <div class="admin-meta">
                    <span class="meta-item">{{ maskPhone(admin.phone) }}</span>
                    <span class="meta-item">{{ admin.email || '-' }}</span>
                  </div>
                  <div class="admin-permissions">
                    <span 
                      v-for="perm in admin.permissions" 
                      :key="perm"
                      class="perm-tag"
                    >
                      {{ perm }}
                    </span>
                  </div>
                </div>
                <div class="admin-footer">
                  <div class="admin-stats-mini">
                    <span>审核: {{ admin.reviewCount || 0 }}</span>
                    <span>登录: {{ formatDate(admin.lastLoginTime) }}</span>
                  </div>
                  <div class="admin-actions">
                    <button class="admin-btn" @click="openAdminModal(admin)">编辑</button>
                    <button 
                      class="admin-btn"
                      :class="admin.status === 1 ? 'warning' : 'success'"
                      @click="toggleAdminStatus(admin)"
                    >
                      {{ admin.status === 1 ? '停用' : '启用' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 系统通知 -->
        <section v-if="currentTab === 'notify'" class="account-section">
          <div class="notify-layout">
            <!-- 左侧：通知表单 -->
            <div class="notify-form-panel">
              <h3 class="panel-title">发送系统通知</h3>
              
              <div class="form-section">
                <label class="form-label">通知类型</label>
                <div class="type-selector">
                  <button 
                    v-for="type in notifyTypes" 
                    :key="type.value"
                    class="type-btn"
                    :class="{ active: notifyForm.type === type.value }"
                    @click="notifyForm.type = type.value"
                  >
                    {{ type.icon }} {{ type.label }}
                  </button>
                </div>
              </div>

              <div class="form-section">
                <label class="form-label">接收对象</label>
                <div class="target-selector">
                  <label class="radio-label">
                    <input type="radio" v-model="notifyForm.targetType" value="all">
                    <span class="custom-radio"></span>
                    <span>全体用户</span>
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="notifyForm.targetType" value="role">
                    <span class="custom-radio"></span>
                    <span>指定角色</span>
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="notifyForm.targetType" value="specific">
                    <span class="custom-radio"></span>
                    <span>指定用户</span>
                  </label>
                </div>

                <!-- 角色选择 -->
                <div v-if="notifyForm.targetType === 'role'" class="sub-options">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="notifyForm.targetRoles" value="student">
                    <span class="custom-checkbox"></span>
                    <span>学生</span>
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="notifyForm.targetRoles" value="teacher">
                    <span class="custom-checkbox"></span>
                    <span>教师</span>
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="notifyForm.targetRoles" value="admin">
                    <span class="custom-checkbox"></span>
                    <span>管理员</span>
                  </label>
                </div>

                <!-- 用户选择 -->
                <div v-if="notifyForm.targetType === 'specific'" class="sub-options">
                  <div class="user-select-box">
                    <div class="selected-users">
                      <span 
                        v-for="user in selectedNotifyUsers" 
                        :key="user.userId"
                        class="selected-tag"
                      >
                        {{ user.realName }}
                        <button @click="removeNotifyUser(user.userId)">×</button>
                      </span>
                      <input 
                        v-model="userSearchKeyword"
                        type="text" 
                        class="user-search-input"
                        placeholder="搜索用户..."
                        @focus="showUserDropdown = true"
                        @input="searchUsers"
                      />
                    </div>
                    <div v-if="showUserDropdown && userSearchResults.length" class="user-dropdown">
                      <div 
                        v-for="user in userSearchResults" 
                        :key="user.userId"
                        class="dropdown-item"
                        @click="addNotifyUser(user)"
                      >
                        <img :src="user.avatar || '/default-avatar.png'" />
                        <span>{{ user.realName }} ({{ user.studentNo || user.teacherNo }})</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-section">
                <label class="form-label">通知标题 <span class="required">*</span></label>
                <input 
                  v-model="notifyForm.title"
                  type="text" 
                  class="form-input"
                  placeholder="请输入通知标题..."
                />
              </div>

              <div class="form-section">
                <label class="form-label">通知内容 <span class="required">*</span></label>
                <textarea 
                  v-model="notifyForm.content"
                  class="form-textarea"
                  rows="6"
                  placeholder="请输入通知内容..."
                ></textarea>
              </div>

              <div class="form-section">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="notifyForm.needConfirm">
                  <span class="custom-checkbox"></span>
                  <span>要求用户确认阅读（强制弹窗）</span>
                </label>
              </div>

              <div class="form-actions">
                <button class="submit-btn" :disabled="!canSendNotify || sending" @click="sendNotification">
                  <span v-if="sending" class="loading-spinner-small"></span>
                  <span v-else>📤 发送通知</span>
                </button>
                <button class="draft-btn" @click="saveDraft">💾 保存草稿</button>
              </div>
            </div>

            <!-- 右侧：发送历史 -->
            <div class="notify-history-panel">
              <h3 class="panel-title">发送历史</h3>
              <div class="history-list">
                <div 
                  v-for="item in notifyHistory" 
                  :key="item.id"
                  class="history-item"
                >
                  <div class="history-header">
                    <span class="history-type" :class="'type-' + item.type">{{ item.typeName }}</span>
                    <span class="history-time">{{ formatDate(item.createTime) }}</span>
                  </div>
                  <h4 class="history-title">{{ item.title }}</h4>
                  <p class="history-content">{{ truncateText(item.content, 50) }}</p>
                  <div class="history-stats">
                    <span>👥 接收: {{ item.receiverCount }}</span>
                    <span>👁️ 已读: {{ item.readCount }}</span>
                    <span v-if="item.needConfirm">✅ 确认: {{ item.confirmCount }}</span>
                  </div>
                </div>
              </div>
              <button class="view-more" @click="loadMoreHistory">加载更多</button>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- 用户编辑弹窗 -->
    <div v-if="showUserModal" class="modal-overlay" @click.self="closeUserModal">
      <div class="edit-modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ editingUser ? '编辑用户' : '新增用户' }}</h3>
          <button class="modal-close" @click="closeUserModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">角色 <span class="required">*</span></label>
              <select v-model="userForm.role" class="form-select">
                <option value="student">学生</option>
                <option value="teacher">教师</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">状态</label>
              <div class="switch-wrapper">
                <label class="switch">
                  <input type="checkbox" v-model="userForm.status" :true-value="1" :false-value="0">
                  <span class="slider"></span>
                </label>
                <span class="switch-label">{{ userForm.status === 1 ? '正常' : '禁用' }}</span>
              </div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">姓名 <span class="required">*</span></label>
              <input v-model="userForm.realName" type="text" class="form-input" />
              <span v-if="userFormErrors.realName" class="error-text">{{ userFormErrors.realName }}</span>
            </div>
            <div class="form-group">
              <label class="form-label">{{ userForm.role === 'student' ? '学号' : '工号' }} <span class="required">*</span></label>
              <input 
                v-model="userForm.roleNo" 
                type="text" 
                class="form-input"
                :placeholder="userForm.role === 'student' ? '请输入学号' : '请输入工号'"
              />
              <span v-if="userFormErrors.roleNo" class="error-text">{{ userFormErrors.roleNo }}</span>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">手机号 <span class="required">*</span></label>
              <input v-model="userForm.phone" type="tel" class="form-input" maxlength="11" />
              <span v-if="userFormErrors.phone" class="error-text">{{ userFormErrors.phone }}</span>
            </div>
          </div>
          <div class="form-group" v-if="!editingUser">
            <label class="form-label">初始密码 <span class="required">*</span></label>
            <div class="password-input">
              <input 
                v-model="userForm.password" 
                :type="showPassword ? 'text' : 'password'" 
                class="form-input"
              />
              <button class="toggle-pwd" @click="showPassword = !showPassword">
                {{ showPassword ? '🙈' : '👁️' }}
              </button>
            </div>
            <button class="gen-pwd" @click="generatePassword">🎲 生成随机密码</button>
            <span v-if="userFormErrors.password" class="error-text">{{ userFormErrors.password }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeUserModal">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="!validateUserForm || submitting"
            @click="saveUser"
          >
            <span v-if="submitting" class="loading-spinner-small"></span>
            <span v-else>保存</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 管理员编辑弹窗 -->
    <div v-if="showAdminModal" class="modal-overlay" @click.self="closeAdminModal">
      <div class="edit-modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ editingAdmin ? '编辑管理员' : '新增管理员' }}</h3>
          <button class="modal-close" @click="closeAdminModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">姓名 <span class="required">*</span></label>
              <input v-model="adminForm.realName" type="text" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">登录账号 <span class="required">*</span></label>
              <input v-model="adminForm.username" type="text" class="form-input" :disabled="!!editingAdmin" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">手机号 <span class="required">*</span></label>
              <input v-model="adminForm.phone" type="tel" class="form-input" maxlength="11" />
            </div>
            <div class="form-group">
              <label class="form-label">邮箱</label>
              <input v-model="adminForm.email" type="email" class="form-input" />
            </div>
          </div>
          <div class="form-group" v-if="!editingAdmin">
            <label class="form-label">初始密码 <span class="required">*</span></label>
            <div class="password-input">
              <input 
                v-model="adminForm.password" 
                :type="showAdminPassword ? 'text' : 'password'" 
                class="form-input"
              />
              <button class="toggle-pwd" @click="showAdminPassword = !showAdminPassword">
                {{ showAdminPassword ? '隐藏' : '查看' }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">管理权限 <span class="required">*</span></label>
            <div class="permission-grid">
              <label 
                v-for="perm in availablePermissions" 
                :key="perm.value"
                class="permission-checkbox"
              >
                <input 
                  type="checkbox" 
                  v-model="adminForm.permissions" 
                  :value="perm.value"
                >
                <span class="custom-checkbox"></span>
                <span class="perm-name">{{ perm.label }}</span>
              </label>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">状态</label>
            <div class="switch-wrapper">
              <label class="switch">
                <input type="checkbox" v-model="adminForm.status" :true-value="1" :false-value="0">
                <span class="slider"></span>
              </label>
              <span class="switch-label">{{ adminForm.status === 1 ? '在职' : '停用' }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeAdminModal">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="!validateAdminForm || submitting"
            @click="saveAdmin"
          >
            <span v-if="submitting" class="loading-spinner-small"></span>
            <span v-else>保存</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 用户详情弹窗 -->
    <div v-if="showUserDetailModal" class="modal-overlay" @click.self="closeUserDetailModal">
      <div class="detail-modal">
        <div class="modal-header">
          <h3 class="modal-title">用户详情</h3>
          <button class="modal-close" @click="closeUserDetailModal">×</button>
        </div>
        <div class="modal-body">
          <div class="user-detail-header">
            <img :src="detailUser.avatar || '/default-avatar.png'" class="detail-avatar" />
            <div class="detail-info">
              <h4 class="detail-name">{{ detailUser.realName }}</h4>
              <p class="detail-role">{{ detailUser.role === 1 ? '学生' : detailUser.role === 2 ? '教师' : detailUser.roleName }}</p>
            </div>
            <span class="detail-status" :class="{ active: detailUser.status === 1 }">
              {{ detailUser.status === 1 ? '正常' : '禁用' }}
            </span>
          </div>
          <div class="detail-section">
            <h5>基本信息</h5>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="item-label">{{ detailUser.role === 1 ? '学号' : '工号' }}</span>
                <span class="item-value">{{ detailUser.username || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="item-label">手机号</span>
                <span class="item-value">{{ detailUser.phone }}</span>
              </div>
              <div class="detail-item">
                <span class="item-label">注册时间</span>
                <span class="item-value">{{ detailUser.createTime }}</span>
              </div>
            </div>
          </div>
          <div class="detail-section">
            <h5>活动统计</h5>
            <div class="detail-stats">
              <div class="stat-box">
                <span class="stat-num">{{ detailUser.publishCount || 0 }}</span>
                <span class="stat-label">发布物品</span>
              </div>
              <div class="stat-box">
                <span class="stat-num">{{ detailUser.claimCount || 0 }}</span>
                <span class="stat-label">认领申请</span>
              </div>
              <div class="stat-box">
                <span class="stat-num">{{ detailUser.foundCount || 0 }}</span>
                <span class="stat-label">成功找回</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="closeUserDetailModal">关闭</button>
          <button class="modal-btn confirm-btn" @click="viewUserItems">查看发布物品</button>
        </div>
      </div>
    </div>

    <!-- 导出格式选择弹窗 -->
    <div v-if="showExportModal" class="modal-overlay" @click.self="showExportModal = false">
      <div class="edit-modal">
        <div class="modal-header">
          <h3 class="modal-title">导出用户数据</h3>
          <button class="modal-close" @click="showExportModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">导出格式</label>
            <div class="radio-group">
              <label class="radio-item">
                <input 
                  type="radio" 
                  v-model="exportFormat" 
                  value="csv"
                />
                <span class="custom-radio"></span>
                <span>CSV格式 (.csv)</span>
              </label>
              <label class="radio-item">
                <input 
                  type="radio" 
                  v-model="exportFormat" 
                  value="xlsx"
                />
                <span class="custom-radio"></span>
                <span>Excel格式 (.xlsx)</span>
              </label>
            </div>
          </div>
          <div style="font-size: 12px; color: #999; margin-top: 8px;">
            <p>• 将导出当前筛选条件下的所有用户数据</p>
            <p>• 包含用户基本信息、状态等完整字段</p>
            <p>• Excel功能开发中，暂时提供CSV格式</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn cancel-btn" @click="showExportModal = false">取消</button>
          <button 
            class="modal-btn confirm-btn" 
            :disabled="exporting"
            @click="doExport"
          >
            <span v-if="exporting" class="loading-spinner-small"></span>
            <span v-else>确定导出</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SysAdminNavigation from '../components/SysAdminNavigation.vue'

const router = useRouter()

/* ================= 标签页配置 ================= */
const tabs = [
  { key: 'users', label: '用户管理', icon: '', badge: null },
  { key: 'admins', label: '管理员', icon: '', badge: null },
  { key: 'notify', label: '系统通知', icon: '', badge: null }
]
const currentTab = ref('users')

/* ================= 用户管理 ================= */
const userStats = reactive({
  student: 0,
  teacher: 0,
  total: 0,
  active: 0
})

const userFilter = reactive({
  role: '',
  status: '',
  keyword: ''
})

const userList = ref<any[]>([])
const userPagination = reactive({
  page: 1,
  size: 10,
  total: 0,
  totalPages: 1
})

const selectedUsers = ref<number[]>([])
const isAllSelected = computed(() => {
  return userList.value.length > 0 && selectedUsers.value.length === userList.value.length
})

/* ================= 管理员管理 ================= */
const adminStats = computed(() => [
  { icon: '👤', value: adminList.value.length, label: '管理员总数' },
  { icon: '✅', value: adminList.value.filter(a => a.status === 1).length, label: '在职' },
  { icon: '🚫', value: adminList.value.filter(a => a.status === 0).length, label: '停用' },
  { icon: '📋', value: adminList.value.reduce((sum, a) => sum + (a.reviewCount || 0), 0), label: '总审核数' }
])

const adminList = ref<any[]>([])
const availablePermissions = [
  { value: 'review', label: '信息审核', icon: '✅' },
  { value: 'manage', label: '物品管理', icon: '📦' },
  { value: 'user', label: '用户管理', icon: '👥' },
  { value: 'notice', label: '公告管理', icon: '📢' },
  { value: 'data', label: '数据导出', icon: '📊' },
  { value: 'config', label: '系统配置', icon: '⚙️' }
]

/* ================= 通知管理 ================= */
const notifyTypes = [
  { value: 'system', label: '系统通知', icon: '🔔' },
  { value: 'policy', label: '政策更新', icon: '📋' },
  { value: 'maintain', label: '维护公告', icon: '🔧' },
  { value: 'urgent', label: '紧急通知', icon: '⚠️' }
]

const notifyForm = reactive({
  type: 'system',
  targetType: 'all',
  targetRoles: [] as string[],
  targetUsers: [] as number[],
  title: '',
  content: '',
  needConfirm: false
})

const notifyHistory = ref<any[]>([])
const sending = ref(false)
const selectedNotifyUsers = ref<any[]>([])
const userSearchKeyword = ref('')
const userSearchResults = ref<any[]>([])
const showUserDropdown = ref(false)

const canSendNotify = computed(() => {
  if (!notifyForm.title.trim() || !notifyForm.content.trim()) return false
  if (notifyForm.targetType === 'role' && notifyForm.targetRoles.length === 0) return false
  if (notifyForm.targetType === 'specific' && notifyForm.targetUsers.length === 0) return false
  return true
})

/* ================= 弹窗状态 ================= */
const showUserModal = ref(false)
const showAdminModal = ref(false)
const showUserDetailModal = ref(false)
const editingUser = ref<any>(null)
const editingAdmin = ref<any>(null)
const detailUser = ref<any>({})
const submitting = ref(false)
const showPassword = ref(false)
const showAdminPassword = ref(false)

/* ================= 表单数据 ================= */
const userForm = reactive({
  role: 'student',
  realName: '',
  roleNo: '',
  phone: '',
  password: '',
  status: 1
})

const adminForm = reactive({
  realName: '',
  username: '',
  phone: '',
  email: '',
  password: '',
  permissions: [] as string[],
  status: 1
})

/* ================= 计算属性 ================= */
const validateUserForm = computed(() => {
  return userForm.realName.trim() && 
         userForm.roleNo.trim() && 
         userForm.phone.trim() && 
         userForm.phone.length === 11 &&
         (editingUser.value || userForm.password.trim())
})

const validateAdminForm = computed(() => {
  return adminForm.realName.trim() && 
         adminForm.username.trim() && 
         adminForm.phone.trim() && 
         adminForm.phone.length === 11 &&
         adminForm.permissions.length > 0 &&
         (editingAdmin.value || adminForm.password.trim())
})

/* ================= 标签切换 ================= */
const switchTab = (tab: string) => {
  currentTab.value = tab
  if (tab === 'users') loadUsers()
  if (tab === 'admins') loadAdmins()
  if (tab === 'notify') loadNotifyHistory()
}

/* ================= 用户管理方法 ================= */
const loadUsers = async () => {
  try {
    const res = await axios.get('/api/user/list', {
      params: {
        page: userPagination.page,
        size: userPagination.size,
        role: userFilter.role || undefined,
        status: userFilter.status || undefined,
        keyword: userFilter.keyword || undefined
      }
    })
    
    if (res.data.code === 0) {
      userList.value = res.data.data.list || []
      userPagination.total = res.data.data.total || 0
      userPagination.totalPages = Math.ceil(userPagination.total / userPagination.size)
      
      // 更新统计
      userStats.total = userList.value.length
      userStats.student = userList.value.filter(u => u.role === 1).length
      userStats.teacher = userList.value.filter(u => u.role === 2).length
      userStats.active = userList.value.filter(u => u.status === 1).length
    }
  } catch (error) {
    console.error('加载用户失败:', error)
    // 模拟数据
    userList.value = [
      { userId: 1, realName: '张三', studentNo: '2023001', role: 'student', phone: '13800138001', email: 'zhangsan@example.com', status: 1, createTime: '2026-01-15 10:30:00', avatar: null, publishCount: 3, claimCount: 2, foundCount: 1 },
      { userId: 2, realName: '李四', teacherNo: 'T2024001', role: 'teacher', phone: '13800138002', email: 'lisi@example.com', status: 1, createTime: '2026-01-20 14:20:00', avatar: null, publishCount: 1, claimCount: 0, foundCount: 0 },
      { userId: 3, realName: '王五', studentNo: '2023002', role: 'student', phone: '13800138003', email: null, status: 0, createTime: '2026-02-01 09:15:00', avatar: null, publishCount: 0, claimCount: 0, foundCount: 0 }
    ]
    userPagination.total = 3
    userPagination.totalPages = 1
    userStats.student = 2
    userStats.teacher = 1
    userStats.total = 3
    userStats.active = 2
  }
}

const changeUserPage = (page: number) => {
  userPagination.page = page
  loadUsers()
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedUsers.value = []
  } else {
    selectedUsers.value = userList.value.map(u => u.userId)
  }
}

const toggleSelectUser = (userId: number) => {
  const index = selectedUsers.value.indexOf(userId)
  if (index > -1) {
    selectedUsers.value.splice(index, 1)
  } else {
    selectedUsers.value.push(userId)
  }
}



const closeUserModal = () => {
  showUserModal.value = false
  editingUser.value = null
}

const generatePassword = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let pwd = ''
  for (let i = 0; i < 8; i++) {
    pwd += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  userForm.password = pwd
  showPassword.value = true
}

/* ================= 表单验证错误信息 ================= */
const userFormErrors = reactive({
  realName: '',
  roleNo: '',
  phone: '',
  password: ''
})

/* ================= 手机号正则 ================= */
const phoneRegex = /^1[3-9]\d{9}$/

const openUserModal = (user?: any) => {
  editingUser.value = user || null
  // 清空错误信息
  Object.keys(userFormErrors).forEach(key => {
    userFormErrors[key as keyof typeof userFormErrors] = ''
  })
  
  if (user) {
    Object.assign(userForm, {
      role: user.role === 1 ? 'student' : user.role === 2 ? 'teacher' : 'student',
      realName: user.realName,
      roleNo: user.username || '',
      phone: user.phone,
      password: '',
      status: user.status
    })
  } else {
    Object.assign(userForm, {
      role: 'student',
      realName: '',
      roleNo: '',
      phone: '',
      password: '',
      status: 1
    })
  }
  showPassword.value = false
  showUserModal.value = true
}

const validateUserFormFields = () => {
  let isValid = true
  
  // 清空之前的错误
  Object.keys(userFormErrors).forEach(key => {
    userFormErrors[key as keyof typeof userFormErrors] = ''
  })
  
  if (!userForm.realName.trim()) {
    userFormErrors.realName = '姓名不能为空'
    isValid = false
  }
  
  if (!userForm.roleNo.trim()) {
    userFormErrors.roleNo = userForm.role === 'student' ? '学号不能为空' : '工号不能为空'
    isValid = false
  }
  
  if (!userForm.phone.trim()) {
    userFormErrors.phone = '手机号不能为空'
    isValid = false
  } else if (!phoneRegex.test(userForm.phone)) {
    userFormErrors.phone = '手机号格式不正确'
    isValid = false
  }
  
  if (!editingUser.value && !userForm.password.trim()) {
    userFormErrors.password = '初始密码不能为空'
    isValid = false
  } else if (!editingUser.value && userForm.password.length < 6) {
    userFormErrors.password = '密码长度至少6位'
    isValid = false
  }
  
  return isValid
}

const saveUser = async () => {
  // 前端表单验证
  if (!validateUserFormFields()) {
    return
  }
  
  submitting.value = true
  try {
    const url = editingUser.value ? `/api/user/${editingUser.value.userId}` : '/api/user/create'
    const method = editingUser.value ? 'put' : 'post'
    
    const payload: any = {
      username: userForm.roleNo,
      realName: userForm.realName,
      phone: userForm.phone,
      role: userForm.role === 'student' ? 1 : 2,
      status: userForm.status
    }
    
    if (userForm.password) {
      payload.password = userForm.password
    }
    
    const res = await axios[method](url, payload)
    
    if (res.data.code === 0) {
      alert(editingUser.value ? '更新成功！' : '创建成功！')
      await loadUsers()
      closeUserModal()
    } else {
      alert(res.data.msg || '操作失败，请重试')
    }
  } catch (error: any) {
    console.error('保存用户失败:', error)
    const errorMsg = error.response?.data?.msg || '操作失败，请重试'
    alert(errorMsg)
  } finally {
    submitting.value = false
  }
}

const toggleUserStatus = async (user: any) => {
  try {
    const res = await axios.put(`/api/user/${user.userId}/status`, {
      status: user.status === 1 ? 0 : 1
    })
    
    if (res.data.code === 0) {
      user.status = user.status === 1 ? 0 : 1
    }
  } catch (error) {
    console.error('切换状态失败:', error)
    alert('操作失败')
  }
}

const viewUserDetail = (user: any) => {
  detailUser.value = user
  showUserDetailModal.value = true
}

const closeUserDetailModal = () => {
  showUserDetailModal.value = false
  detailUser.value = {}
}

const viewUserItems = () => {
  // 跳转到物品管理页面并筛选该用户的物品
  router.push(`/item-admin/items?userId=${detailUser.value.userId}`)
  closeUserDetailModal()
}

/* ================= 导出功能 ================= */
const showExportModal = ref(false)
const exportFormat = ref('csv')
const exporting = ref(false)

const exportUsers = () => {
  showExportModal.value = true
}

const doExport = async () => {
  exporting.value = true
  try {
    const params = new URLSearchParams({
      format: exportFormat.value,
      role: userFilter.role || '',
      status: userFilter.status || '',
      keyword: userFilter.keyword || ''
    })
    
    const response = await axios.get(`/api/user/export?${params.toString()}`, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 生成文件名
    const filename = `用户数据_${new Date().toISOString().slice(0, 10)}.${exportFormat.value}`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    alert('导出成功！')
    showExportModal.value = false
  } catch (error: any) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

const batchEnableUsers = async () => {
  if (!confirm(`确定要启用选中的 ${selectedUsers.value.length} 个用户吗？`)) return
  try {
    const res = await axios.post('/api/user/batch-status', {
      userIds: selectedUsers.value,
      status: 1
    })
    if (res.data.code === 0) {
      selectedUsers.value = []
      await loadUsers()
    } else {
      alert(res.data.msg || '批量操作失败')
    }
  } catch (error: any) {
    console.error('批量启用失败:', error)
    const errorMsg = error.response?.data?.msg || '批量操作失败'
    alert(errorMsg)
  }
}

const batchDisableUsers = async () => {
  if (!confirm(`确定要禁用选中的 ${selectedUsers.value.length} 个用户吗？`)) return
  try {
    const res = await axios.post('/api/user/batch-status', {
      userIds: selectedUsers.value,
      status: 0
    })
    if (res.data.code === 0) {
      selectedUsers.value = []
      await loadUsers()
    } else {
      alert(res.data.msg || '批量操作失败')
    }
  } catch (error: any) {
    console.error('批量禁用失败:', error)
    const errorMsg = error.response?.data?.msg || '批量操作失败'
    alert(errorMsg)
  }
}

const batchDeleteUsers = async () => {
  if (!confirm(`确定要删除选中的 ${selectedUsers.value.length} 个用户吗？此操作不可恢复！`)) return
  try {
    await axios.delete('/api/user/batch-delete', {
      data: { userIds: selectedUsers.value }
    })
    selectedUsers.value = []
    await loadUsers()
  } catch (error) {
    alert('批量删除失败')
  }
}

/* ================= 管理员管理方法 ================= */
const loadAdmins = async () => {
  try {
    const res = await axios.get('/api/admin/admins')
    if (res.data.code === 200) {
      adminList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载管理员失败:', error)
    adminList.value = [
      { adminId: 1, realName: '管理员A', username: 'admin001', phone: '13900139001', email: 'admin1@example.com', status: 1, permissions: ['review', 'manage', 'notice'], reviewCount: 156, lastLoginTime: '2026-03-01 09:30:00', avatar: null },
      { adminId: 2, realName: '管理员B', username: 'admin002', phone: '13900139002', email: 'admin2@example.com', status: 1, permissions: ['review', 'data'], reviewCount: 89, lastLoginTime: '2026-02-28 16:45:00', avatar: null },
      { adminId: 3, realName: '管理员C', username: 'admin003', phone: '13900139003', email: null, status: 0, permissions: ['review'], reviewCount: 0, lastLoginTime: '2026-01-15 11:20:00', avatar: null }
    ]
  }
}

const openAdminModal = (admin?: any) => {
  editingAdmin.value = admin || null
  if (admin) {
    Object.assign(adminForm, {
      realName: admin.realName,
      username: admin.username,
      phone: admin.phone,
      email: admin.email || '',
      password: '',
      permissions: [...admin.permissions],
      status: admin.status
    })
  } else {
    Object.assign(adminForm, {
      realName: '',
      username: '',
      phone: '',
      email: '',
      password: '',
      permissions: ['review'],
      status: 1
    })
  }
  showAdminPassword.value = false
  showAdminModal.value = true
}

const closeAdminModal = () => {
  showAdminModal.value = false
  editingAdmin.value = null
}

const saveAdmin = async () => {
  submitting.value = true
  try {
    const url = editingAdmin.value ? `/api/admin/admins/${editingAdmin.value.adminId}` : '/api/admin/admins'
    const method = editingAdmin.value ? 'put' : 'post'
    
    const res = await axios[method](url, adminForm)
    
    if (res.data.code === 200) {
      await loadAdmins()
      closeAdminModal()
    }
  } catch (error) {
    console.error('保存管理员失败:', error)
    alert('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

const toggleAdminStatus = async (admin: any) => {
  try {
    const res = await axios.post(`/api/admin/admins/${admin.adminId}/status`, {
      status: admin.status === 1 ? 0 : 1
    })
    
    if (res.data.code === 200) {
      admin.status = admin.status === 1 ? 0 : 1
    }
  } catch (error) {
    console.error('切换状态失败:', error)
    alert('操作失败')
  }
}

/* ================= 通知管理方法 ================= */
const loadNotifyHistory = async () => {
  try {
    const res = await axios.get('/api/announcements/admin/list')
    if (res.data.code === 0) {
      notifyHistory.value = res.data.data || []
    }
  } catch (error) {
    notifyHistory.value = [
      { id: 1, type: 'system', typeName: '系统', title: '系统维护通知', content: '系统将于本周六凌晨 2:00-4:00 进行例行维护...', createTime: '2026-02-28 10:00:00', receiverCount: 1256, readCount: 890, confirmCount: 0, needConfirm: false },
      { id: 2, type: 'policy', typeName: '政策', title: '审核规范更新', content: '请严格按照新的审核标准执行...', createTime: '2026-02-27 14:30:00', receiverCount: 3, readCount: 3, confirmCount: 3, needConfirm: true },
      { id: 3, type: 'urgent', typeName: '紧急', title: '安全漏洞修复', content: '发现安全漏洞，请立即更新密码...', createTime: '2026-02-25 09:15:00', receiverCount: 1256, readCount: 1200, confirmCount: 1150, needConfirm: true }
    ]
  }
}

const searchUsers = async () => {
  if (!userSearchKeyword.value.trim()) {
    userSearchResults.value = []
    return
  }
  try {
    const res = await axios.get('/api/user/list', {
      params: { keyword: userSearchKeyword.value, size: 10 }
    })
    if (res.data.code === 0) {
      userSearchResults.value = (res.data.data.list || []).filter((u: any) => 
        !notifyForm.targetUsers.includes(u.userId)
      )
    }
  } catch (error) {
    userSearchResults.value = []
  }
}

const addNotifyUser = (user: any) => {
  if (!notifyForm.targetUsers.includes(user.userId)) {
    notifyForm.targetUsers.push(user.userId)
    selectedNotifyUsers.value.push(user)
  }
  userSearchKeyword.value = ''
  userSearchResults.value = []
  showUserDropdown.value = false
}

const removeNotifyUser = (userId: number) => {
  const index = notifyForm.targetUsers.indexOf(userId)
  if (index > -1) {
    notifyForm.targetUsers.splice(index, 1)
    selectedNotifyUsers.value = selectedNotifyUsers.value.filter(u => u.userId !== userId)
  }
}

const sendNotification = async () => {
  sending.value = true
  try {
    const res = await axios.post('/api/announcements/admin', notifyForm)
    if (res.data.code === 0) {
      alert('通知发送成功！')
      // 重置表单
      notifyForm.title = ''
      notifyForm.content = ''
      notifyForm.targetUsers = []
      selectedNotifyUsers.value = []
      await loadNotifyHistory()
    }
  } catch (error) {
    console.error('发送通知失败:', error)
    alert('发送失败，请重试')
  } finally {
    sending.value = false
  }
}

const saveDraft = () => {
  localStorage.setItem('notifyDraft', JSON.stringify(notifyForm))
  alert('草稿已保存')
}

const loadMoreHistory = () => {
  // 加载更多历史记录
}

/* ================= 工具函数 ================= */
const maskPhone = (phone: string) => {
  if (!phone || phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const formatDate = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const truncateText = (text: string, length: number) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

/* ================= 退出登录 ================= */
const handleLogout = () => {
  router.push('/login')
}

/* ================= 生命周期 ================= */
onMounted(() => {
  loadUsers()
  
  // 加载草稿
  const draft = localStorage.getItem('notifyDraft')
  if (draft) {
    const parsed = JSON.parse(draft)
    Object.assign(notifyForm, parsed)
  }
})
</script>

<style scoped>
/* 基础布局 */
.account-manage-page {
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

/* 标签页 */
.account-tabs {
  margin-bottom: 25px;
}

.tab-buttons {
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 8px;
  border: 2px solid rgba(166, 124, 82, 0.2);
  width: fit-content;
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
  position: relative;
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

.tab-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  background: #f44336;
  color: white;
  font-size: 11px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 内容区域 */
.account-section {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

/* 统计行 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.stat-mini {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  transition: all 0.3s ease;
}

.stat-mini:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.stat-mini.highlight {
  border-color: rgba(76, 175, 80, 0.3);
  background: rgba(76, 175, 80, 0.08);
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: #a67c52;
  font-weight: 700;
}

.stat-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  outline: none;
}

.search-box {
  display: flex;
  gap: 8px;
}

.search-input {
  width: 220px;
  padding: 10px 15px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
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

.action-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn.primary {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.action-btn.secondary {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
}

/* 数据表格 */
.data-table-wrapper {
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
  vertical-align: middle;
}

.data-table tr:hover {
  background: rgba(255, 255, 255, 0.3);
}

.data-table tr.row-selected {
  background: rgba(243, 129, 129, 0.1);
}

.col-checkbox { width: 40px; }
.col-id { width: 60px; }
.col-avatar { width: 60px; }
.col-info { min-width: 150px; }
.col-role { width: 100px; }
.col-contact { min-width: 150px; }
.col-status { width: 80px; }
.col-time { width: 120px; }
.col-actions { width: 120px; }

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.user-name {
  font-weight: 600;
  color: #a67c52;
  margin-bottom: 4px;
}

.user-no {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

.role-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.role-student {
  background: rgba(33, 150, 243, 0.15);
  color: #2196f3;
}

.role-teacher {
  background: rgba(156, 39, 176, 0.15);
  color: #9c27b0;
}

.contact-phone {
  font-weight: 500;
  color: #a67c52;
}

.contact-email {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
  margin-top: 4px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.status-badge.active {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.action-group {
  display: flex;
  gap: 8px;
}

.icon-action {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(166, 124, 82, 0.1);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.icon-action:hover {
  background: rgba(166, 124, 82, 0.2);
  transform: scale(1.1);
}

.icon-action.danger:hover {
  background: rgba(244, 67, 54, 0.15);
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

/* 批量操作栏 */
.batch-bar {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 15px 25px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 100;
  border: 2px solid rgba(166, 124, 82, 0.2);
}

.batch-info {
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  color: #a67c52;
  font-weight: 600;
}

.batch-actions {
  display: flex;
  gap: 12px;
}

.batch-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
}

.batch-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

.batch-btn.warning {
  background: rgba(255, 152, 0, 0.15);
  color: #ff9800;
}

.batch-btn.warning:hover {
  background: rgba(255, 152, 0, 0.25);
}

.batch-btn.danger {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.batch-btn.danger:hover {
  background: rgba(244, 67, 54, 0.25);
}

/* 管理员区域 */
.admin-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.admin-stat-card {
  text-align: center;
  padding: 25px 20px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  transition: all 0.3s ease;
}

.admin-stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.admin-stat-icon {
  font-size: 36px;
  margin-bottom: 10px;
}

.admin-stat-value {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 28px;
  color: #a67c52;
  font-weight: 700;
}

.admin-stat-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.7);
}

.admin-list {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 20px;
  color: #a67c52;
  margin: 0;
}

.add-admin-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.add-admin-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.admin-card {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(166, 124, 82, 0.15);
  transition: all 0.3s ease;
}

.admin-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
  border-color: rgba(243, 129, 129, 0.3);
}

.admin-card.disabled {
  opacity: 0.7;
  background: rgba(166, 124, 82, 0.05);
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.admin-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(166, 124, 82, 0.2);
}

.admin-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.admin-status.active {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.admin-body {
  margin-bottom: 15px;
}

.admin-name {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0 0 5px 0;
}

.admin-account {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.6);
  margin: 0 0 12px 0;
}

.admin-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 15px;
}

.meta-item {
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
}

.admin-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.perm-tag {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  background: rgba(243, 129, 129, 0.15);
  color: #f38181;
  font-weight: 500;
}

.admin-footer {
  padding-top: 15px;
  border-top: 1px solid rgba(166, 124, 82, 0.1);
}

.admin-stats-mini {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.admin-actions {
  display: flex;
  gap: 10px;
}

.admin-btn {
  flex: 1;
  padding: 8px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 13px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.admin-btn:hover {
  border-color: rgba(243, 129, 129, 0.5);
  background: rgba(243, 129, 129, 0.1);
}

.admin-btn.success {
  border-color: rgba(76, 175, 80, 0.5);
  color: #4caf50;
}

.admin-btn.success:hover {
  background: rgba(76, 175, 80, 0.1);
}

.admin-btn.warning {
  border-color: rgba(255, 152, 0, 0.5);
  color: #ff9800;
}

.admin-btn.warning:hover {
  background: rgba(255, 152, 0, 0.1);
}

/* 通知区域 */
.notify-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 25px;
}

.notify-form-panel,
.notify-history-panel {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  padding: 25px;
  border: 2px solid rgba(166, 124, 82, 0.15);
}

.panel-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 18px;
  color: #a67c52;
  margin: 0 0 20px 0;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(166, 124, 82, 0.1);
}

.form-section {
  margin-bottom: 20px;
}

.form-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
}

.type-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.type-btn {
  padding: 10px 16px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.5);
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.type-btn:hover {
  border-color: rgba(243, 129, 129, 0.5);
}

.type-btn.active {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(243, 129, 129, 0.3);
}

.target-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-label,
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.radio-label input,
.checkbox-label input {
  display: none;
}

.custom-radio,
.custom-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(166, 124, 82, 0.4);
  border-radius: 50%;
  position: relative;
  transition: all 0.3s ease;
}

.custom-checkbox {
  border-radius: 5px;
}

.radio-label input:checked + .custom-radio,
.checkbox-label input:checked + .custom-checkbox {
  border-color: #f38181;
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.custom-radio::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  opacity: 0;
  transition: all 0.3s ease;
}

.checkbox-label input:checked + .custom-checkbox::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.radio-label input:checked + .custom-radio::after {
  opacity: 1;
}

.sub-options {
  margin-left: 30px;
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.user-select-box {
  position: relative;
}

.selected-users {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.5);
  min-height: 44px;
}

.selected-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.selected-tag button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.user-search-input {
  flex: 1;
  min-width: 100px;
  border: none;
  background: transparent;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  outline: none;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
  border: 1px solid rgba(166, 124, 82, 0.1);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: rgba(243, 129, 129, 0.1);
}

.dropdown-item img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.5);
  outline: none;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  border-color: rgba(243, 129, 129, 0.7);
  box-shadow: 0 0 0 3px rgba(243, 129, 129, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.submit-btn,
.draft-btn {
  flex: 1;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-family: "Comic Sans MS", cursive;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 129, 129, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.draft-btn {
  background: rgba(166, 124, 82, 0.1);
  color: #a67c52;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
}

.draft-btn:hover {
  background: rgba(166, 124, 82, 0.2);
}

/* 历史记录 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 600px;
  overflow-y: auto;
}

.history-item {
  padding: 15px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.1);
  transition: all 0.3s ease;
}

.history-item:hover {
  border-color: rgba(243, 129, 129, 0.3);
  transform: translateX(4px);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.history-type {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.history-type.type-system { background: rgba(33, 150, 243, 0.15); color: #2196f3; }
.history-type.type-policy { background: rgba(156, 39, 176, 0.15); color: #9c27b0; }
.history-type.type-maintain { background: rgba(255, 152, 0, 0.15); color: #ff9800; }
.history-type.type-urgent { background: rgba(244, 67, 54, 0.15); color: #f44336; }

.history-time {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

.history-title {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 15px;
  color: #a67c52;
  margin: 0 0 8px 0;
}

.history-content {
  font-size: 13px;
  color: rgba(166, 124, 82, 0.8);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.history-stats {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.view-more {
  width: 100%;
  padding: 12px;
  margin-top: 15px;
  border: 1.6px dashed rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  background: transparent;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-more:hover {
  border-color: #f38181;
  color: #f38181;
  background: rgba(243, 129, 129, 0.05);
}

/* 弹窗样式 */
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

.edit-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.detail-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 450px;
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

.confirm-btn {
  background: linear-gradient(to right, #f38181, #f77d5f);
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(243, 129, 129, 0.3);
}

.modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 表单样式 */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-select {
  width: 100%;
  padding: 12px;
  border: 1.6px solid rgba(166, 124, 82, 0.3);
  border-radius: 10px;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
  background: rgba(255, 255, 255, 0.5);
  outline: none;
  cursor: pointer;
}

.password-input {
  position: relative;
}

.password-input .form-input {
  padding-right: 45px;
}

.toggle-pwd {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.gen-pwd {
  margin-top: 8px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: rgba(166, 124, 82, 0.1);
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: #a67c52;
  cursor: pointer;
}

.gen-pwd:hover {
  background: rgba(166, 124, 82, 0.2);
}

.permission-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.permission-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.permission-checkbox:hover {
  background: rgba(166, 124, 82, 0.05);
}

.perm-icon {
  font-size: 16px;
}

.switch-wrapper {
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

.switch-label {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

/* 用户详情弹窗 */
.user-detail-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(166, 124, 82, 0.1);
}

.detail-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(166, 124, 82, 0.2);
}

.detail-info {
  flex: 1;
}

.detail-name {
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 22px;
  color: #a67c52;
  margin: 0 0 5px 0;
}

.detail-role {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.7);
  margin: 0;
}

.detail-status {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.detail-status.active {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.detail-section {
  margin-bottom: 25px;
}

.detail-section h5 {
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: rgba(166, 124, 82, 0.8);
  margin: 0 0 15px 0;
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.item-label {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.6);
}

.item-value {
  font-size: 14px;
  color: #a67c52;
  font-weight: 500;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.stat-box {
  text-align: center;
  padding: 20px;
  background: rgba(166, 124, 82, 0.05);
  border-radius: 12px;
}

.stat-num {
  display: block;
  font-family: "Comic Sans MS", "Marker Felt", cursive;
  font-size: 24px;
  color: #a67c52;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-box .stat-label {
  font-size: 12px;
  color: rgba(166, 124, 82, 0.7);
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误提示文本 */
.error-text {
  display: block;
  margin-top: 5px;
  font-family: "Comic Sans MS", cursive;
  font-size: 12px;
  color: #f44336;
}

/* 单选按钮组 */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-family: "Comic Sans MS", cursive;
  font-size: 14px;
  color: #a67c52;
}

.radio-item input {
  display: none;
}

.radio-item .custom-radio {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(166, 124, 82, 0.4);
  border-radius: 50%;
  position: relative;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.radio-item input:checked + .custom-radio {
  border-color: #f38181;
  background: linear-gradient(to right, #f38181, #f77d5f);
}

.radio-item .custom-radio::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
  transition: transform 0.3s ease;
}

.radio-item input:checked + .custom-radio::after {
  transform: translate(-50%, -50%) scale(1);
}

/* 响应式 */
@media (max-width: 1200px) {
  .notify-layout {
    grid-template-columns: 1fr;
  }
  
  .admin-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    max-width: 100vw;
    padding: 20px 15px;
    padding-bottom: 100px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .stats-row,
  .admin-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    flex-wrap: wrap;
  }
  
  .search-input {
    width: auto;
    flex: 1;
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
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .permission-grid {
    grid-template-columns: 1fr;
  }
  
  .batch-bar {
    left: 15px;
    right: 15px;
    transform: none;
    flex-direction: column;
    gap: 15px;
  }
}
</style>