<template>
  <section class="page-shell page-shell--dashboard">
    <div class="workspace-shell">
      <aside class="workspace-sidebar" aria-label="租客功能导航">
        <div class="workspace-sidebar__header">
          <p class="workspace-sidebar__title">租客工作台</p>
        </div>

        <nav class="workspace-nav">
          <button
            v-for="(item, index) in tenantSections"
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
          <span class="eyebrow">租客控制台</span>
          <h1 class="hero-title">我的租房事项</h1>
          <p class="hero-text">集中处理预约、合同、账单、维修、投诉和消息。</p>
        </div>

        <div class="hero-actions">
          <RouterLink class="primary-button" to="/houses">浏览房源</RouterLink>
          <RouterLink class="secondary-button" to="/">返回首页</RouterLink>
        </div>
      </div>

      <div v-show="activeSection === 'overview'" class="page-card workspace-panel">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">租赁历史</span>
            <h2 class="page-title page-title--section">历史摘要</h2>
          </div>
          <button class="ghost-button" type="button" :disabled="loading.history" @click="loadHistory">
            {{ loading.history ? "刷新中..." : "刷新" }}
          </button>
        </div>

        <p v-if="errors.history" class="form-message form-message--error">{{ errors.history }}</p>

        <div v-if="history" class="history-summary">
          <div class="history-metric">
            <strong>{{ history.summary.bookings }}</strong>
            <span>预约</span>
          </div>
          <div class="history-metric">
            <strong>{{ history.summary.contracts }}</strong>
            <span>合同</span>
          </div>
          <div class="history-metric">
            <strong>{{ history.summary.payments }}</strong>
            <span>账单</span>
          </div>
          <div class="history-metric">
            <strong>{{ history.summary.repairs }}</strong>
            <span>维修</span>
          </div>
          <div class="history-metric">
            <strong>{{ history.summary.complaints }}</strong>
            <span>投诉</span>
          </div>
        </div>

        <div v-if="history?.recent_contracts?.length" class="manage-list">
          <article v-for="contract in history.recent_contracts.slice(0, 3)" :key="contract.id" class="manage-item">
            <div class="manage-item__main">
              <div class="house-meta">
                <span class="tag">{{ formatContractStatus(contract.status) }}</span>
                <span class="tag tag--light">{{ contract.contract_no }}</span>
              </div>
              <h3 class="house-title house-title--small">{{ contract.house?.title || "合同房源" }}</h3>
              <div class="booking-meta">
                <span>租期：{{ contract.start_date }} 至 {{ contract.end_date }}</span>
                <span>月租：¥{{ contract.monthly_rent }}/月</span>
              </div>
            </div>
          </article>
        </div>
      </div>

      <div v-show="activeSection === 'bookings'" class="page-card workspace-panel">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">看房预约</span>
            <h2 class="page-title page-title--section">预约记录</h2>
          </div>
        </div>

        <form class="filter-grid filter-grid--manage" @submit.prevent="loadBookings">
          <label class="field">
            <span>状态</span>
            <select v-model="bookingFilters.status">
              <option value="">全部状态</option>
              <option value="pending">待处理</option>
              <option value="confirmed">已确认</option>
              <option value="cancelled">已取消</option>
              <option value="completed">已完成</option>
            </select>
          </label>

          <div class="filter-actions filter-actions--full">
            <button class="secondary-button" type="submit" :disabled="loading.bookings">
              {{ loading.bookings ? "加载中..." : "筛选预约" }}
            </button>
            <button class="ghost-button" type="button" @click="resetBookingFilters">重置</button>
          </div>
        </form>

        <p v-if="errors.bookings" class="form-message form-message--error">{{ errors.bookings }}</p>

        <div v-if="bookings.length" class="manage-list">
          <article v-for="booking in bookings" :key="booking.id" class="manage-item">
            <div class="manage-item__main">
              <div class="house-meta">
                <span class="tag">{{ formatBookingStatus(booking.status) }}</span>
                <span class="tag tag--light">{{ formatDateTime(booking.appointment_time) }}</span>
              </div>
              <h3 class="house-title house-title--small">{{ booking.house?.title || "房源" }}</h3>
              <p class="house-address">{{ formatHouseAddress(booking.house) }}</p>
              <div class="booking-meta">
                <span>房东：{{ booking.landlord?.real_name || booking.landlord?.username || "暂无" }}</span>
                <span>租金：¥{{ booking.house?.rent || "-" }}/月</span>
              </div>
              <p v-if="booking.remark" class="page-text">备注：{{ booking.remark }}</p>
            </div>

            <div class="manage-item__actions">
              <RouterLink v-if="booking.house?.id" class="ghost-button" :to="`/houses/${booking.house.id}`">
                查看房源
              </RouterLink>
              <button
                v-if="['pending', 'confirmed'].includes(booking.status)"
                class="danger-button"
                type="button"
                @click="changeBookingStatus(booking.id, 'cancelled')"
              >
                取消预约
              </button>
            </div>
          </article>
        </div>

        <div v-else-if="!loading.bookings" class="empty-card empty-card--soft">
          <h3 class="page-title page-title--section">暂无预约记录</h3>
          <p class="page-text">可以先从房源详情页提交看房申请。</p>
        </div>
      </div>

      <div v-show="activeSection === 'contracts'" class="page-card workspace-panel">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">租赁合同</span>
            <h2 class="page-title page-title--section">合同列表</h2>
          </div>
        </div>

        <form class="filter-grid filter-grid--manage" @submit.prevent="loadContracts">
          <label class="field">
            <span>状态</span>
            <select v-model="contractFilters.status">
              <option value="">全部状态</option>
              <option value="draft">待签署</option>
              <option value="active">生效中</option>
              <option value="terminated">已终止</option>
              <option value="expired">已到期</option>
            </select>
          </label>

          <div class="filter-actions filter-actions--full">
            <button class="secondary-button" type="submit" :disabled="loading.contracts">
              {{ loading.contracts ? "加载中..." : "筛选合同" }}
            </button>
            <button class="ghost-button" type="button" @click="resetContractFilters">重置</button>
          </div>
        </form>

        <p v-if="errors.contracts" class="form-message form-message--error">{{ errors.contracts }}</p>

        <div v-if="contracts.length" class="manage-list">
          <article v-for="contract in contracts" :key="contract.id" class="manage-item">
            <div class="manage-item__main">
              <div class="house-meta">
                <span class="tag">{{ formatContractStatus(contract.status) }}</span>
                <span class="tag tag--light">{{ contract.contract_no }}</span>
              </div>
              <h3 class="house-title house-title--small">{{ contract.house?.title || "合同房源" }}</h3>
              <p class="house-address">{{ formatHouseAddress(contract.house) }}</p>
              <div class="booking-meta">
                <span>租期：{{ contract.start_date }} 至 {{ contract.end_date }}</span>
                <span>月租：¥{{ contract.monthly_rent }}/月</span>
              </div>
              <p v-if="contract.content" class="page-text">合同内容：{{ contract.content }}</p>
            </div>

            <div class="manage-item__actions">
              <button
                v-if="contract.status === 'draft'"
                class="primary-button"
                type="button"
                @click="handleSignContract(contract.id)"
              >
                签署合同
              </button>
            </div>
          </article>
        </div>

        <div v-else-if="!loading.contracts" class="empty-card empty-card--soft">
          <h3 class="page-title page-title--section">暂无合同</h3>
          <p class="page-text">房东为你创建合同后会显示在这里。</p>
        </div>
      </div>

      <div v-show="activeSection === 'payments'" class="page-card workspace-panel">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">账单支付</span>
            <h2 class="page-title page-title--section">账单列表</h2>
          </div>
        </div>

        <form class="filter-grid filter-grid--manage" @submit.prevent="loadPayments">
          <label class="field">
            <span>状态</span>
            <select v-model="paymentFilters.status">
              <option value="">全部状态</option>
              <option value="pending">待支付</option>
              <option value="paid">已支付</option>
            </select>
          </label>

          <label class="field">
            <span>类型</span>
            <select v-model="paymentFilters.payment_type">
              <option value="">全部类型</option>
              <option value="deposit">押金</option>
              <option value="rent">租金</option>
            </select>
          </label>

          <div class="filter-actions filter-actions--full">
            <button class="secondary-button" type="submit" :disabled="loading.payments">
              {{ loading.payments ? "加载中..." : "筛选账单" }}
            </button>
            <button class="ghost-button" type="button" @click="resetPaymentFilters">重置</button>
          </div>
        </form>

        <p v-if="errors.payments" class="form-message form-message--error">{{ errors.payments }}</p>

        <div v-if="payments.length" class="manage-list">
          <article v-for="payment in payments" :key="payment.id" class="manage-item">
            <div class="manage-item__main">
              <div class="house-meta">
                <span class="tag">{{ formatPaymentStatus(payment.status) }}</span>
                <span class="tag tag--light">{{ formatPaymentType(payment.payment_type) }}</span>
              </div>
              <h3 class="house-title house-title--small">{{ payment.contract?.house?.title || "付款项" }}</h3>
              <div class="booking-meta">
                <span>金额：¥{{ payment.amount }}</span>
                <span>到期日：{{ payment.due_date || "暂无" }}</span>
              </div>
              <div class="booking-meta">
                <span>合同编号：{{ payment.contract?.contract_no || "暂无" }}</span>
                <span>支付方式：{{ formatPaymentMethod(payment.payment_method) }}</span>
              </div>
            </div>

            <div class="manage-item__actions" v-if="['pending', 'overdue'].includes(payment.status)">
              <label class="field field--inline">
                <span>支付方式</span>
                <select v-model="paymentMethods[payment.id]">
                  <option value="bank">银行卡</option>
                  <option value="alipay">支付宝</option>
                  <option value="wechat">微信支付</option>
                </select>
              </label>
              <button class="primary-button" type="button" @click="handlePay(payment.id)">
                立即支付
              </button>
              <button class="ghost-button" type="button" @click="handlePaymentFail(payment.id)">
                标记失败
              </button>
            </div>
          </article>
        </div>

        <div v-else-if="!loading.payments" class="empty-card empty-card--soft">
          <h3 class="page-title page-title--section">暂无账单</h3>
          <p class="page-text">合同签署后，相关账单会显示在这里。</p>
        </div>
      </div>

      <div v-show="activeSection === 'requests'" class="dashboard-grid workspace-panel">
        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">维修申请</span>
              <h2 class="page-title page-title--section">提交维修</h2>
            </div>
          </div>

          <form class="filter-grid filter-grid--form" @submit.prevent="handleCreateRepair">
            <label class="field field--full">
              <span>租住房源</span>
              <select v-model="repairForm.house_id">
                <option value="">选择生效中的合同房源</option>
                <option v-for="contract in activeContracts" :key="contract.id" :value="contract.house_id">
                  {{ contract.house?.title || "房源" }} | {{ formatHouseAddress(contract.house) }}
                </option>
              </select>
            </label>
            <label class="field"><span>标题</span><input v-model.trim="repairForm.title" type="text" placeholder="例如：厨房水槽漏水" /></label>
            <label class="field">
              <span>优先级</span>
              <select v-model="repairForm.priority">
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
                <option value="urgent">紧急</option>
              </select>
            </label>
            <label class="field field--full">
              <span>问题描述</span>
              <textarea v-model.trim="repairForm.description" rows="4" placeholder="说明故障位置、影响范围和方便上门时间" />
            </label>
            <div class="filter-actions filter-actions--full">
              <button class="primary-button" type="submit" :disabled="loading.submitRepair">
                {{ loading.submitRepair ? "提交中..." : "提交维修申请" }}
              </button>
              <button class="ghost-button" type="button" @click="resetRepairForm">清空</button>
            </div>
          </form>

          <p v-if="messages.repairForm" class="form-message form-message--success">{{ messages.repairForm }}</p>
          <p v-if="errors.repairForm" class="form-message form-message--error">{{ errors.repairForm }}</p>
        </div>

        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">投诉反馈</span>
              <h2 class="page-title page-title--section">提交投诉</h2>
            </div>
          </div>

          <form class="filter-grid filter-grid--form" @submit.prevent="handleCreateComplaint">
            <label class="field field--full">
              <span>关联房源</span>
              <select v-model="complaintForm.house_id">
                <option value="">不关联具体房源</option>
                <option v-for="contract in contracts" :key="contract.id" :value="contract.house_id">
                  {{ contract.house?.title || "房源" }}
                </option>
              </select>
            </label>
            <label class="field field--full"><span>标题</span><input v-model.trim="complaintForm.title" type="text" placeholder="例如：服务响应不及时" /></label>
            <label class="field field--full">
              <span>投诉内容</span>
              <textarea v-model.trim="complaintForm.content" rows="4" placeholder="描述事情经过、期望处理结果和可联系时间" />
            </label>
            <div class="filter-actions filter-actions--full">
              <button class="primary-button" type="submit" :disabled="loading.submitComplaint">
                {{ loading.submitComplaint ? "提交中..." : "提交投诉" }}
              </button>
              <button class="ghost-button" type="button" @click="resetComplaintForm">清空</button>
            </div>
          </form>

          <p v-if="messages.complaintForm" class="form-message form-message--success">{{ messages.complaintForm }}</p>
          <p v-if="errors.complaintForm" class="form-message form-message--error">{{ errors.complaintForm }}</p>
        </div>
      </div>

      <div v-show="activeSection === 'progress'" class="dashboard-grid workspace-panel">
        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">维修进度</span>
              <h2 class="page-title page-title--section">我的维修单</h2>
            </div>
          </div>

          <form class="filter-grid filter-grid--manage" @submit.prevent="loadRepairs">
            <label class="field">
              <span>状态</span>
              <select v-model="repairFilters.status">
                <option value="">全部状态</option>
                <option value="submitted">已提交</option>
                <option value="processing">处理中</option>
                <option value="completed">已完成</option>
                <option value="rejected">已驳回</option>
              </select>
            </label>
            <div class="filter-actions filter-actions--full">
              <button class="secondary-button" type="submit" :disabled="loading.repairs">
                {{ loading.repairs ? "加载中..." : "筛选维修单" }}
              </button>
              <button class="ghost-button" type="button" @click="resetRepairFilters">重置</button>
            </div>
          </form>

          <p v-if="errors.repairs" class="form-message form-message--error">{{ errors.repairs }}</p>

          <div v-if="repairs.length" class="manage-list">
            <article v-for="repair in repairs" :key="repair.id" class="manage-item">
              <div class="manage-item__main">
                <div class="house-meta">
                  <span class="tag">{{ formatRepairStatus(repair.status) }}</span>
                  <span class="tag tag--light">{{ formatPriority(repair.priority) }}</span>
                </div>
                <h3 class="house-title house-title--small">{{ repair.title }}</h3>
                <p class="house-address">{{ repair.house?.title || "房源" }} | {{ formatDateTime(repair.created_at) }}</p>
                <p class="page-text">{{ repair.description }}</p>
              </div>
            </article>
          </div>

          <div v-else-if="!loading.repairs" class="empty-card empty-card--soft">
            <h3 class="page-title page-title--section">暂无维修单</h3>
            <p class="page-text">生效合同对应的房源可以提交维修申请。</p>
          </div>
        </div>

        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">投诉处理</span>
              <h2 class="page-title page-title--section">我的投诉</h2>
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
                <p class="page-text">{{ complaint.content }}</p>
                <p v-if="complaint.result" class="page-text">处理结果：{{ complaint.result }}</p>
              </div>
            </article>
          </div>

          <div v-else-if="!loading.complaints" class="empty-card empty-card--soft">
            <h3 class="page-title page-title--section">暂无投诉</h3>
            <p class="page-text">提交后的投诉会在这里查看处理进度。</p>
          </div>
        </div>
      </div>

      <MessageCenter
        v-show="activeSection === 'messages'"
        class="workspace-panel"
        eyebrow="消息中心"
        title="房源会话"
        description="查看房东回复、处理未读消息，并直接继续沟通。"
        empty-text="可以从房源详情页发起第一条咨询。"
      />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import MessageCenter from "../../components/MessageCenter.vue";
import { fetchMyBookings, updateBookingStatus } from "../../api/booking";
import { createComplaint, fetchMyComplaints } from "../../api/complaint";
import { fetchMyContracts, signContract } from "../../api/contract";
import { failPayment, fetchMyPayments, payPayment } from "../../api/payment";
import { createRepair, fetchMyRepairs } from "../../api/repair";
import { fetchRentalHistory } from "../../api/user";

const tenantSections = [
  { key: "overview", label: "租赁概览" },
  { key: "bookings", label: "看房预约" },
  { key: "contracts", label: "租赁合同" },
  { key: "payments", label: "账单支付" },
  { key: "requests", label: "服务提交" },
  { key: "progress", label: "处理进度" },
  { key: "messages", label: "消息中心" },
];

const activeSection = ref("overview");

const defaultRepairForm = () => ({
  house_id: "",
  title: "",
  description: "",
  priority: "medium",
});

const defaultComplaintForm = () => ({
  house_id: "",
  title: "",
  content: "",
});

const bookingFilters = reactive({ status: "" });
const contractFilters = reactive({ status: "" });
const paymentFilters = reactive({ status: "", payment_type: "" });
const repairFilters = reactive({ status: "" });
const complaintFilters = reactive({ status: "" });
const repairForm = reactive(defaultRepairForm());
const complaintForm = reactive(defaultComplaintForm());
const paymentMethods = reactive({});

const bookings = ref([]);
const contracts = ref([]);
const payments = ref([]);
const repairs = ref([]);
const complaints = ref([]);
const history = ref(null);
const loading = reactive({
  bookings: false,
  contracts: false,
  payments: false,
  repairs: false,
  complaints: false,
  history: false,
  submitRepair: false,
  submitComplaint: false,
});
const errors = reactive({
  bookings: "",
  contracts: "",
  payments: "",
  repairs: "",
  complaints: "",
  history: "",
  repairForm: "",
  complaintForm: "",
});
const messages = reactive({
  repairForm: "",
  complaintForm: "",
});

const activeContracts = computed(() => contracts.value.filter((contract) => contract.status === "active"));

function formatBookingStatus(status) {
  return {
    pending: "待处理",
    confirmed: "已确认",
    cancelled: "已取消",
    completed: "已完成",
  }[status] || status;
}

function formatContractStatus(status) {
  return {
    draft: "待签署",
    active: "生效中",
    terminated: "已终止",
    expired: "已到期",
  }[status] || status;
}

function formatPaymentStatus(status) {
  return {
    pending: "待支付",
    paid: "已支付",
    overdue: "已逾期",
    failed: "支付失败",
    refunded: "已退款",
  }[status] || status;
}

function formatPaymentType(type) {
  return {
    deposit: "押金",
    rent: "租金",
  }[type] || type || "未知类型";
}

function formatPaymentMethod(method) {
  return {
    bank: "银行卡",
    alipay: "支付宝",
    wechat: "微信支付",
  }[method] || method || "待支付";
}

function formatRepairStatus(status) {
  return {
    submitted: "已提交",
    processing: "处理中",
    completed: "已完成",
    rejected: "已驳回",
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

function formatPriority(priority) {
  return {
    low: "低优先级",
    medium: "中优先级",
    high: "高优先级",
    urgent: "紧急",
  }[priority] || priority;
}

function formatDateTime(value) {
  return value ? new Date(value).toLocaleString() : "未知时间";
}

function formatHouseAddress(house) {
  if (!house) {
    return "暂无地址";
  }
  return [house.city, house.district, house.community, house.address_detail].filter(Boolean).join(" ");
}

async function loadBookings() {
  loading.bookings = true;
  errors.bookings = "";
  try {
    const response = await fetchMyBookings(bookingFilters);
    bookings.value = response.data.data.items;
  } catch (error) {
    errors.bookings = error.message || "加载预约失败。";
    bookings.value = [];
  } finally {
    loading.bookings = false;
  }
}

async function loadContracts() {
  loading.contracts = true;
  errors.contracts = "";
  try {
    const response = await fetchMyContracts(contractFilters);
    contracts.value = response.data.data.items;
  } catch (error) {
    errors.contracts = error.message || "加载合同失败。";
    contracts.value = [];
  } finally {
    loading.contracts = false;
  }
}

async function loadPayments() {
  loading.payments = true;
  errors.payments = "";
  try {
    const response = await fetchMyPayments(paymentFilters);
    payments.value = response.data.data.items;
    for (const item of payments.value) {
      if (!paymentMethods[item.id]) {
        paymentMethods[item.id] = "bank";
      }
    }
  } catch (error) {
    errors.payments = error.message || "加载账单失败。";
    payments.value = [];
  } finally {
    loading.payments = false;
  }
}

async function loadRepairs() {
  loading.repairs = true;
  errors.repairs = "";
  try {
    const response = await fetchMyRepairs(repairFilters);
    repairs.value = response.data.data.items;
  } catch (error) {
    errors.repairs = error.message || "加载维修单失败。";
    repairs.value = [];
  } finally {
    loading.repairs = false;
  }
}

async function loadComplaints() {
  loading.complaints = true;
  errors.complaints = "";
  try {
    const response = await fetchMyComplaints(complaintFilters);
    complaints.value = response.data.data.items;
  } catch (error) {
    errors.complaints = error.message || "加载投诉失败。";
    complaints.value = [];
  } finally {
    loading.complaints = false;
  }
}

async function loadHistory() {
  loading.history = true;
  errors.history = "";
  try {
    const response = await fetchRentalHistory();
    history.value = response.data.data;
  } catch (error) {
    errors.history = error.message || "加载租赁历史失败。";
    history.value = null;
  } finally {
    loading.history = false;
  }
}

function resetBookingFilters() {
  bookingFilters.status = "";
  loadBookings();
}

function resetContractFilters() {
  contractFilters.status = "";
  loadContracts();
}

function resetPaymentFilters() {
  paymentFilters.status = "";
  paymentFilters.payment_type = "";
  loadPayments();
}

function resetRepairFilters() {
  repairFilters.status = "";
  loadRepairs();
}

function resetComplaintFilters() {
  complaintFilters.status = "";
  loadComplaints();
}

function resetRepairForm() {
  Object.assign(repairForm, defaultRepairForm());
  errors.repairForm = "";
  messages.repairForm = "";
}

function resetComplaintForm() {
  Object.assign(complaintForm, defaultComplaintForm());
  errors.complaintForm = "";
  messages.complaintForm = "";
}

async function changeBookingStatus(bookingId, status) {
  errors.bookings = "";
  try {
    await updateBookingStatus(bookingId, { status });
    await loadBookings();
  } catch (error) {
    errors.bookings = error.message || "更新预约状态失败。";
  }
}

async function handleSignContract(contractId) {
  errors.contracts = "";
  try {
    await signContract(contractId);
    await loadContracts();
    await loadPayments();
  } catch (error) {
    errors.contracts = error.message || "签署合同失败。";
  }
}

async function handlePay(paymentId) {
  errors.payments = "";
  try {
    await payPayment(paymentId, {
      payment_method: paymentMethods[paymentId] || "bank",
    });
    await loadPayments();
  } catch (error) {
    errors.payments = error.message || "完成支付失败。";
  }
}

async function handlePaymentFail(paymentId) {
  errors.payments = "";
  try {
    await failPayment(paymentId, {
      payment_method: paymentMethods[paymentId] || "bank",
      reason: "tenant marked payment failed",
    });
    await loadPayments();
  } catch (error) {
    errors.payments = error.message || "标记支付失败失败。";
  }
}

async function handleCreateRepair() {
  errors.repairForm = "";
  messages.repairForm = "";
  if (!repairForm.house_id || !repairForm.title || !repairForm.description) {
    errors.repairForm = "房源、标题和问题描述不能为空。";
    return;
  }

  loading.submitRepair = true;
  try {
    await createRepair({
      house_id: repairForm.house_id,
      title: repairForm.title,
      description: repairForm.description,
      priority: repairForm.priority,
    });
    messages.repairForm = "维修申请已提交。";
    resetRepairForm();
    await loadRepairs();
  } catch (error) {
    errors.repairForm = error.message || "提交维修申请失败。";
  } finally {
    loading.submitRepair = false;
  }
}

async function handleCreateComplaint() {
  errors.complaintForm = "";
  messages.complaintForm = "";
  if (!complaintForm.title || !complaintForm.content) {
    errors.complaintForm = "标题和投诉内容不能为空。";
    return;
  }

  loading.submitComplaint = true;
  try {
    await createComplaint({
      house_id: complaintForm.house_id || null,
      title: complaintForm.title,
      content: complaintForm.content,
    });
    messages.complaintForm = "投诉已提交。";
    resetComplaintForm();
    await loadComplaints();
  } catch (error) {
    errors.complaintForm = error.message || "提交投诉失败。";
  } finally {
    loading.submitComplaint = false;
  }
}

onMounted(async () => {
  await loadHistory();
  await loadBookings();
  await loadContracts();
  await loadPayments();
  await loadRepairs();
  await loadComplaints();
});
</script>
