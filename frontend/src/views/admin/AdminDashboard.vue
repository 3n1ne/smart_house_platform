<template>
  <section class="page-shell page-shell--dashboard">
    <div class="workspace-shell">
      <aside class="workspace-sidebar" aria-label="管理员功能导航">
        <div class="workspace-sidebar__header">
          <p class="workspace-sidebar__title">管理工作台</p>
          <p class="workspace-sidebar__text">按管理对象切换模块，概览、内容、用户和投诉各自独立。</p>
        </div>

        <nav class="workspace-nav">
          <button
            v-for="(item, index) in adminSections"
            :key="item.key"
            class="workspace-nav__button"
            :class="{ 'workspace-nav__button--active': activeSection === item.key }"
            type="button"
            @click="activeSection = item.key"
          >
            <span class="workspace-nav__index">{{ String(index + 1).padStart(2, "0") }}</span>
            <span>{{ item.label }}</span>
          </button>
        </nav>
      </aside>

      <div class="workspace-content stack-section">
      <div class="hero-card dashboard-hero">
        <div>
          <span class="eyebrow">管理员控制台</span>
          <h1 class="hero-title">系统概览</h1>
          <p class="hero-text">查看运营指标、服务状态、用户状态和投诉处理队列。</p>
        </div>
        <RouterLink class="secondary-button" to="/houses">查看公开房源</RouterLink>
      </div>

      <div v-show="activeSection === 'overview'" class="dashboard-grid workspace-panel">
        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">报表统计</span>
              <h2 class="page-title page-title--section">业务总览</h2>
            </div>
            <button class="ghost-button" type="button" @click="loadReport" :disabled="loading.report">
              {{ loading.report ? "刷新中..." : "刷新" }}
            </button>
          </div>

          <p v-if="errors.report" class="form-message form-message--error">{{ errors.report }}</p>

          <div v-if="report" class="manage-list">
            <article class="manage-item">
              <div class="manage-item__main">
                <div class="house-meta">
                  <span class="tag">用户 {{ report.totals.users }}</span>
                  <span class="tag tag--light">房源 {{ report.totals.houses }}</span>
                  <span class="tag tag--light">合同 {{ report.totals.contracts }}</span>
                  <span class="tag tag--light">公告 {{ report.totals.news }}</span>
                </div>
                <h3 class="house-title house-title--small">收入与待收</h3>
                <div class="booking-meta">
                  <span>已收金额：¥{{ report.totals.paid_amount }}</span>
                  <span>待收金额：¥{{ report.totals.pending_payment_amount }}</span>
                </div>
                <div class="booking-meta">
                  <span>出租率：{{ formatPercent(report.totals.occupancy_rate) }}</span>
                  <span>30 天活跃用户：{{ report.totals.active_users_30d }}</span>
                </div>
              </div>
            </article>

            <article class="manage-item">
              <div class="manage-item__main">
                <h3 class="house-title house-title--small">状态分布</h3>
                <div class="booking-meta">
                  <span>房源：{{ formatStatusMap(report.houses_by_status) }}</span>
                  <span>预约：{{ formatStatusMap(report.bookings_by_status) }}</span>
                </div>
                <div class="booking-meta">
                  <span>付款：{{ formatStatusMap(report.payments_by_status) }}</span>
                  <span>维修：{{ formatStatusMap(report.repairs_by_status) }}</span>
                </div>
                <div class="booking-meta">
                  <span>投诉：{{ formatStatusMap(report.complaints_by_status) }}</span>
                  <span>公告：{{ formatStatusMap(report.news_by_status) }}</span>
                </div>
              </div>
            </article>

            <article class="manage-item">
              <div class="manage-item__main">
                <h3 class="house-title house-title--small">租金收入趋势</h3>
                <p class="page-text">{{ formatIncomeTrend(report.rent_income_trend) }}</p>
              </div>
            </article>
          </div>
        </div>

        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">系统监控</span>
              <h2 class="page-title page-title--section">服务状态</h2>
            </div>
            <button class="ghost-button" type="button" @click="loadMonitor" :disabled="loading.monitor">
              {{ loading.monitor ? "刷新中..." : "刷新" }}
            </button>
          </div>

          <p v-if="errors.monitor" class="form-message form-message--error">{{ errors.monitor }}</p>

          <div v-if="monitor" class="manage-list">
            <article class="manage-item">
              <div class="manage-item__main">
                <div class="house-meta">
                  <span class="tag">{{ monitor.status }}</span>
                  <span class="tag tag--light">{{ formatDateTime(monitor.checked_at) }}</span>
                </div>
                <h3 class="house-title house-title--small">模块状态</h3>
                <p class="page-text">{{ formatStatusMap(monitor.modules) }}</p>
              </div>
            </article>

            <article class="manage-item">
              <div class="manage-item__main">
                <h3 class="house-title house-title--small">最近操作日志</h3>
                <p v-if="!monitor.recent_logs.length" class="page-text">暂无操作日志。</p>
                <div v-for="log in monitor.recent_logs" :key="log.id" class="booking-meta">
                  <span>{{ formatModule(log.module) }} / {{ formatAction(log.action) }}</span>
                  <span>{{ formatDateTime(log.created_at) }}</span>
                </div>
              </div>
            </article>
          </div>
        </div>
      </div>

      <NewsManager v-show="activeSection === 'news'" class="workspace-panel" />

      <div v-show="activeSection === 'users'" class="page-card workspace-panel">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">用户管理</span>
            <h2 class="page-title page-title--section">用户列表</h2>
          </div>
        </div>

        <form class="filter-grid filter-grid--manage" @submit.prevent="loadUsers">
          <label class="field">
            <span>角色</span>
            <select v-model="userFilters.role">
              <option value="">全部角色</option>
              <option value="tenant">租客</option>
              <option value="landlord">房东</option>
              <option value="admin">管理员</option>
            </select>
          </label>
          <label class="field">
            <span>状态</span>
            <select v-model="userFilters.status">
              <option value="">全部状态</option>
              <option value="active">正常</option>
              <option value="disabled">已禁用</option>
            </select>
          </label>
          <label class="field">
            <span>关键词</span>
            <input v-model.trim="userFilters.keyword" type="text" placeholder="用户名、姓名或手机号" />
          </label>
          <div class="filter-actions filter-actions--full">
            <button class="secondary-button" type="submit" :disabled="loading.users">
              {{ loading.users ? "加载中..." : "筛选用户" }}
            </button>
            <button class="ghost-button" type="button" @click="resetUserFilters">重置</button>
          </div>
        </form>

        <p v-if="errors.users" class="form-message form-message--error">{{ errors.users }}</p>

        <div v-if="users.length" class="manage-list">
          <article v-for="user in users" :key="user.id" class="manage-item">
            <div class="manage-item__main">
              <div class="house-meta">
                <span class="tag">{{ formatRole(user.role) }}</span>
                <span class="tag tag--light">{{ formatUserStatus(user.status) }}</span>
                <span class="tag tag--light">#{{ user.id }}</span>
              </div>
              <h3 class="house-title house-title--small">{{ user.real_name || user.username }}</h3>
              <div class="booking-meta">
                <span>用户名：{{ user.username }}</span>
                <span>手机：{{ user.phone || "暂无" }}</span>
                <span>邮箱：{{ user.email || "暂无" }}</span>
              </div>
              <div class="booking-meta">
                <span>注册时间：{{ formatDateTime(user.created_at) }}</span>
                <span>最近登录：{{ formatDateTime(user.last_login_at) }}</span>
              </div>
            </div>

            <div class="manage-item__actions">
              <button
                v-if="user.status !== 'disabled'"
                class="danger-button"
                type="button"
                @click="changeUserStatus(user.id, 'disabled')"
              >
                禁用
              </button>
              <button
                v-if="user.status === 'disabled'"
                class="secondary-button"
                type="button"
                @click="changeUserStatus(user.id, 'active')"
              >
                启用
              </button>
            </div>
          </article>
        </div>

        <div v-else-if="!loading.users" class="empty-card empty-card--soft">
          <h3 class="page-title page-title--section">暂无用户</h3>
          <p class="page-text">可以调整筛选条件后重新查询。</p>
        </div>
      </div>

      <div v-show="activeSection === 'complaints'" class="page-card workspace-panel">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">投诉管理</span>
            <h2 class="page-title page-title--section">投诉处理</h2>
          </div>
        </div>

        <form class="filter-grid filter-grid--manage" @submit.prevent="loadComplaints">
          <label class="field">
            <span>状态</span>
            <select v-model="complaintFilters.status">
              <option value="">全部状态</option>
              <option value="submitted">已提交</option>
              <option value="processing">处理中</option>
              <option value="resolved">已解决</option>
              <option value="rejected">已驳回</option>
            </select>
          </label>
          <div class="filter-actions filter-actions--full">
            <button class="secondary-button" type="submit" :disabled="loading.complaints">
              {{ loading.complaints ? "加载中..." : "筛选投诉" }}
            </button>
            <button class="ghost-button" type="button" @click="resetComplaintFilters">重置</button>
          </div>
        </form>

        <p v-if="errors.complaints" class="form-message form-message--error">{{ errors.complaints }}</p>

        <div v-if="complaints.length" class="manage-list">
          <article v-for="complaint in complaints" :key="complaint.id" class="manage-item">
            <div class="manage-item__main">
              <div class="house-meta">
                <span class="tag">{{ formatComplaintStatus(complaint.status) }}</span>
                <span class="tag tag--light">{{ formatDateTime(complaint.created_at) }}</span>
              </div>
              <h3 class="house-title house-title--small">{{ complaint.title }}</h3>
              <p class="house-address">
                {{ complaint.house?.title || "未关联房源" }} |
                {{ complaint.complainant?.real_name || complaint.complainant?.username || "匿名用户" }}
              </p>
              <p class="page-text">{{ complaint.content }}</p>
              <label class="field field--full">
                <span>处理结果</span>
                <textarea v-model.trim="complaintResults[complaint.id]" rows="3" placeholder="填写处理说明" />
              </label>
            </div>

            <div class="manage-item__actions">
              <button v-if="complaint.status === 'submitted'" class="secondary-button" type="button" @click="changeComplaintStatus(complaint.id, 'processing')">开始处理</button>
              <button v-if="['submitted', 'processing'].includes(complaint.status)" class="primary-button" type="button" @click="changeComplaintStatus(complaint.id, 'resolved')">标记解决</button>
              <button v-if="complaint.status !== 'rejected'" class="danger-button" type="button" @click="changeComplaintStatus(complaint.id, 'rejected')">驳回</button>
            </div>
          </article>
        </div>

        <div v-else-if="!loading.complaints" class="empty-card empty-card--soft">
          <h3 class="page-title page-title--section">暂无投诉</h3>
          <p class="page-text">租客或房东提交的投诉会显示在这里。</p>
        </div>
      </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import NewsManager from "../../components/NewsManager.vue";
import { fetchMyComplaints, updateComplaintStatus } from "../../api/complaint";
import { fetchMonitorOverview } from "../../api/monitor";
import { fetchReportOverview } from "../../api/report";
import { fetchUsers, updateUserStatus } from "../../api/user";

const adminSections = [
  { key: "overview", label: "系统概览" },
  { key: "news", label: "公告管理" },
  { key: "users", label: "用户管理" },
  { key: "complaints", label: "投诉处理" },
];

const activeSection = ref("overview");

const report = ref(null);
const monitor = ref(null);
const users = ref([]);
const complaints = ref([]);
const complaintResults = reactive({});
const userFilters = reactive({ role: "", status: "", keyword: "" });
const complaintFilters = reactive({ status: "" });

const loading = reactive({
  report: false,
  monitor: false,
  users: false,
  complaints: false,
});
const errors = reactive({
  report: "",
  monitor: "",
  users: "",
  complaints: "",
});

function formatStatusMap(map) {
  if (!map || !Object.keys(map).length) {
    return "暂无数据";
  }
  return Object.entries(map)
    .map(([key, value]) => `${formatStatusKey(key)}：${value}`)
    .join("，");
}

function formatPercent(value) {
  return `${Math.round((value || 0) * 10000) / 100}%`;
}

function formatIncomeTrend(items) {
  if (!items?.length) {
    return "暂无已支付账单。";
  }
  return items.map((item) => `${item.month}：¥${item.amount}`).join("，");
}

function formatStatusKey(key) {
  return {
    draft: "草稿",
    available: "可租",
    rented: "已出租",
    repairing: "维修中",
    offline: "已下架",
    pending: "待处理",
    confirmed: "已确认",
    cancelled: "已取消",
    completed: "已完成",
    active: "正常",
    disabled: "已禁用",
    terminated: "已终止",
    expired: "已到期",
    paid: "已支付",
    overdue: "已逾期",
    failed: "失败",
    refunded: "已退款",
    submitted: "已提交",
    processing: "处理中",
    resolved: "已解决",
    rejected: "已驳回",
    ok: "正常",
  }[key] || key;
}

function formatModule(module) {
  return {
    auth: "认证",
    user: "用户",
    house: "房源",
    booking: "预约",
    contract: "合同",
    payment: "支付",
    message: "消息",
    repair: "维修",
    complaint: "投诉",
  }[module] || module;
}

function formatAction(action) {
  return {
    register: "注册",
    login: "登录",
    update_profile: "更新资料",
    update_status: "更新状态",
    create: "创建",
    update: "更新",
    offline: "下架",
    add_media: "添加媒体",
    delete_media: "删除媒体",
    sign: "签署",
    pay: "支付",
    send: "发送",
  }[action] || action;
}

function formatRole(role) {
  return {
    tenant: "租客",
    landlord: "房东",
    admin: "管理员",
  }[role] || role || "未知角色";
}

function formatUserStatus(status) {
  return {
    active: "正常",
    disabled: "已禁用",
  }[status] || status;
}

function formatComplaintStatus(status) {
  return {
    submitted: "已提交",
    processing: "处理中",
    resolved: "已解决",
    rejected: "已驳回",
  }[status] || status;
}

function formatDateTime(value) {
  return value ? new Date(value).toLocaleString() : "暂无";
}

async function loadReport() {
  loading.report = true;
  errors.report = "";
  try {
    const response = await fetchReportOverview();
    report.value = response.data.data;
  } catch (error) {
    errors.report = error.message || "加载报表失败。";
    report.value = null;
  } finally {
    loading.report = false;
  }
}

async function loadMonitor() {
  loading.monitor = true;
  errors.monitor = "";
  try {
    const response = await fetchMonitorOverview();
    monitor.value = response.data.data;
  } catch (error) {
    errors.monitor = error.message || "加载监控信息失败。";
    monitor.value = null;
  } finally {
    loading.monitor = false;
  }
}

async function loadUsers() {
  loading.users = true;
  errors.users = "";
  try {
    const response = await fetchUsers(userFilters);
    users.value = response.data.data.items;
  } catch (error) {
    errors.users = error.message || "加载用户失败。";
    users.value = [];
  } finally {
    loading.users = false;
  }
}

async function loadComplaints() {
  loading.complaints = true;
  errors.complaints = "";
  try {
    const response = await fetchMyComplaints(complaintFilters);
    complaints.value = response.data.data.items;
    for (const complaint of complaints.value) {
      complaintResults[complaint.id] = complaint.result || complaintResults[complaint.id] || "";
    }
  } catch (error) {
    errors.complaints = error.message || "加载投诉失败。";
    complaints.value = [];
  } finally {
    loading.complaints = false;
  }
}

function resetUserFilters() {
  userFilters.role = "";
  userFilters.status = "";
  userFilters.keyword = "";
  loadUsers();
}

function resetComplaintFilters() {
  complaintFilters.status = "";
  loadComplaints();
}

async function changeUserStatus(userId, status) {
  errors.users = "";
  try {
    await updateUserStatus(userId, { status });
    await loadUsers();
    await loadReport();
    await loadMonitor();
  } catch (error) {
    errors.users = error.message || "更新用户状态失败。";
  }
}

async function changeComplaintStatus(complaintId, status) {
  errors.complaints = "";
  try {
    await updateComplaintStatus(complaintId, {
      status,
      result: complaintResults[complaintId] || null,
    });
    await loadComplaints();
    await loadReport();
    await loadMonitor();
  } catch (error) {
    errors.complaints = error.message || "更新投诉状态失败。";
  }
}

onMounted(async () => {
  await loadReport();
  await loadMonitor();
  await loadUsers();
  await loadComplaints();
});
</script>
