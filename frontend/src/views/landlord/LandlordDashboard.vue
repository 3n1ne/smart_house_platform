<template>
  <section class="page-shell">
    <div class="stack-section">
      <div class="hero-card dashboard-hero">
        <div>
          <span class="eyebrow">房东控制台</span>
          <h1 class="hero-title">房源运营管理</h1>
          <p class="hero-text">管理房源、预约、合同、收款、维修和租客沟通。</p>
        </div>

        <div class="hero-actions">
          <button class="primary-button" type="button" @click="startCreate">发布房源</button>
          <RouterLink class="secondary-button" to="/houses">公开房源</RouterLink>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">房源编辑</span>
              <h2 class="page-title page-title--section">
                {{ editingId ? "编辑房源" : "创建房源" }}
              </h2>
            </div>
            <button v-if="editingId" class="ghost-button" type="button" @click="resetForm">取消编辑</button>
          </div>

          <form class="filter-grid filter-grid--form" @submit.prevent="handleSubmit">
            <label class="field"><span>标题</span><input v-model.trim="form.title" type="text" placeholder="例如：近地铁精装两室一厅" /></label>
            <label class="field"><span>省份</span><input v-model.trim="form.province" type="text" placeholder="例如：浙江省" /></label>
            <label class="field"><span>城市</span><input v-model.trim="form.city" type="text" placeholder="例如：杭州市" /></label>
            <label class="field"><span>区域</span><input v-model.trim="form.district" type="text" placeholder="例如：西湖区" /></label>
            <label class="field"><span>小区</span><input v-model.trim="form.community" type="text" placeholder="请输入小区名称" /></label>
            <label class="field"><span>详细地址</span><input v-model.trim="form.address_detail" type="text" placeholder="请输入楼栋、单元、门牌号" /></label>
            <label class="field"><span>类型</span><input v-model.trim="form.house_type" type="text" placeholder="公寓 / 整租 / 合租" /></label>
            <label class="field"><span>户型</span><input v-model.trim="form.layout" type="text" placeholder="例如：两室一厅" /></label>
            <label class="field"><span>面积</span><input v-model.number="form.area" type="number" min="1" step="0.1" placeholder="89" /></label>
            <label class="field"><span>租金</span><input v-model.number="form.rent" type="number" min="0" step="0.01" placeholder="5500" /></label>
            <label class="field"><span>押金</span><input v-model.number="form.deposit" type="number" min="0" step="0.01" placeholder="5500" /></label>
            <label class="field"><span>装修</span><input v-model.trim="form.decoration" type="text" placeholder="精装 / 简装" /></label>
            <label class="field"><span>楼层</span><input v-model.number="form.floor" type="number" min="1" placeholder="8" /></label>
            <label class="field"><span>总楼层</span><input v-model.number="form.total_floors" type="number" min="1" placeholder="18" /></label>
            <label class="field"><span>朝向</span><input v-model.trim="form.orientation" type="text" placeholder="例如：朝南" /></label>
            <label class="field">
              <span>状态</span>
              <select v-model="form.status">
                <option value="draft">草稿</option>
                <option value="available">可租</option>
                <option value="repairing">维修中</option>
                <option value="offline">已下架</option>
              </select>
            </label>
            <label class="field field--full">
              <span>描述</span>
              <textarea v-model.trim="form.description" rows="4" placeholder="填写交通、装修、配套和周边信息" />
            </label>

            <div class="filter-actions filter-actions--full">
              <button class="primary-button" type="submit" :disabled="loading.submitHouse">
                {{ loading.submitHouse ? "保存中..." : editingId ? "保存修改" : "创建房源" }}
              </button>
              <button class="ghost-button" type="button" @click="resetForm">清空</button>
            </div>
          </form>

          <p v-if="messages.houseForm" class="form-message form-message--success">{{ messages.houseForm }}</p>
          <p v-if="errors.houseForm" class="form-message form-message--error">{{ errors.houseForm }}</p>
        </div>

        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">我的房源</span>
              <h2 class="page-title page-title--section">当前房源</h2>
            </div>
          </div>

          <form class="filter-grid filter-grid--manage" @submit.prevent="loadMyHouses">
            <label class="field">
              <span>状态</span>
              <select v-model="houseFilters.status">
                <option value="">全部状态</option>
                <option value="draft">草稿</option>
                <option value="available">可租</option>
                <option value="rented">已出租</option>
                <option value="repairing">维修中</option>
                <option value="offline">已下架</option>
              </select>
            </label>
            <label class="field"><span>城市</span><input v-model.trim="houseFilters.city" type="text" placeholder="城市" /></label>
            <label class="field"><span>关键词</span><input v-model.trim="houseFilters.keyword" type="text" placeholder="标题或地址" /></label>

            <div class="filter-actions filter-actions--full">
              <button class="secondary-button" type="submit" :disabled="loading.houses">
                {{ loading.houses ? "加载中..." : "筛选房源" }}
              </button>
              <button class="ghost-button" type="button" @click="resetHouseFilters">重置</button>
            </div>
          </form>

          <p v-if="errors.houses" class="form-message form-message--error">{{ errors.houses }}</p>

          <div v-if="houses.length" class="manage-list">
            <article v-for="house in houses" :key="house.id" class="manage-item">
              <div class="manage-item__main">
                <div class="house-meta">
                  <span class="tag">{{ formatHouseStatus(house.status) }}</span>
                  <span class="tag tag--light">{{ house.city }} {{ house.district }}</span>
                </div>
                <h3 class="house-title house-title--small">{{ house.title }}</h3>
                <p class="house-address">{{ house.community || house.address_detail }}</p>
                <div class="house-info-row">
                  <span>{{ house.layout }} | {{ house.area }} 平方米</span>
                  <strong class="price price--compact">¥{{ house.rent }}/月</strong>
                </div>
                <div v-if="house.media_items?.length" class="media-strip">
                  <div v-for="media in house.media_items" :key="media.id" class="media-thumb">
                    <img v-if="media.media_type === 'image'" :src="media.file_url" :alt="house.title" />
                    <div v-else class="media-thumb__video">视频</div>
                    <button class="media-thumb__remove" type="button" @click="removeHouseMedia(house.id, media.id)">
                      删除
                    </button>
                  </div>
                </div>
              </div>

              <div class="manage-item__actions">
                <button class="ghost-button" type="button" @click="startEdit(house)">编辑</button>
                <button v-if="house.status !== 'available'" class="secondary-button" type="button" @click="changeHouseStatus(house.id, 'available')">上架</button>
                <button v-if="house.status !== 'offline'" class="ghost-button" type="button" @click="changeHouseStatus(house.id, 'offline')">下架</button>
                <button v-if="house.status !== 'draft'" class="ghost-button" type="button" @click="changeHouseStatus(house.id, 'draft')">设为草稿</button>
                <label class="secondary-button media-upload-button">
                  {{ mediaUploading[house.id] ? "上传中..." : "上传图片" }}
                  <input type="file" accept="image/*,video/*" :disabled="mediaUploading[house.id]" @change="uploadHouseMedia(house.id, $event)" />
                </label>
                <button class="danger-button" type="button" @click="handleDelete(house.id)">删除</button>
              </div>
            </article>
          </div>

          <div v-else-if="!loading.houses" class="empty-card empty-card--soft">
            <h3 class="page-title page-title--section">暂无房源</h3>
            <p class="page-text">可以先发布第一套房源，或放宽当前筛选条件。</p>
          </div>
        </div>
      </div>

      <div class="page-card">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">看房申请</span>
            <h2 class="page-title page-title--section">预约申请</h2>
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
                <span>租客：{{ booking.tenant?.real_name || booking.tenant?.username || "暂无" }}</span>
                <span>联系方式：{{ booking.tenant?.phone || "暂无" }}</span>
              </div>
              <p v-if="booking.remark" class="page-text">备注：{{ booking.remark }}</p>
            </div>

            <div class="manage-item__actions">
              <button v-if="booking.status === 'pending'" class="secondary-button" type="button" @click="changeBookingStatus(booking.id, 'confirmed')">确认预约</button>
              <button v-if="booking.status === 'pending'" class="ghost-button" type="button" @click="changeBookingStatus(booking.id, 'cancelled')">拒绝预约</button>
              <button v-if="booking.status === 'confirmed'" class="primary-button" type="button" @click="changeBookingStatus(booking.id, 'completed')">标记完成</button>
            </div>
          </article>
        </div>

        <div v-else-if="!loading.bookings" class="empty-card empty-card--soft">
          <h3 class="page-title page-title--section">暂无预约申请</h3>
          <p class="page-text">租客提交的预约申请会显示在这里。</p>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">合同创建</span>
              <h2 class="page-title page-title--section">创建合同</h2>
            </div>
          </div>

          <form class="filter-grid filter-grid--form" @submit.prevent="handleCreateContract">
            <label class="field field--full">
              <span>预约记录</span>
              <select v-model="contractForm.booking_id">
                <option value="">请选择已确认或已完成的预约</option>
                <option v-for="booking in contractableBookings" :key="booking.id" :value="booking.id">
                  {{ booking.house?.title || "房源" }} | {{ booking.tenant?.real_name || booking.tenant?.username }} | {{ formatDateTime(booking.appointment_time) }}
                </option>
              </select>
            </label>

            <label class="field"><span>开始日期</span><input v-model="contractForm.start_date" type="date" /></label>
            <label class="field"><span>结束日期</span><input v-model="contractForm.end_date" type="date" /></label>
            <label class="field">
              <span>付款周期</span>
              <select v-model="contractForm.payment_cycle">
                <option value="monthly">按月</option>
              </select>
            </label>
            <label class="field field--full">
              <span>合同内容</span>
              <textarea v-model.trim="contractForm.content" rows="4" placeholder="填写入住规则、付款约定和补充条款" />
            </label>

            <div class="filter-actions filter-actions--full">
              <button class="primary-button" type="submit" :disabled="loading.submitContract">
                {{ loading.submitContract ? "创建中..." : "创建合同" }}
              </button>
              <button class="ghost-button" type="button" @click="resetContractForm">清空</button>
            </div>
          </form>

          <p v-if="messages.contractForm" class="form-message form-message--success">{{ messages.contractForm }}</p>
          <p v-if="errors.contractForm" class="form-message form-message--error">{{ errors.contractForm }}</p>
        </div>

        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">租赁合同</span>
              <h2 class="page-title page-title--section">当前合同</h2>
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
                  <span>租客：{{ contract.tenant?.real_name || contract.tenant?.username || "暂无" }}</span>
                  <span>租期：{{ contract.start_date }} 至 {{ contract.end_date }}</span>
                </div>
                <div class="booking-meta">
                  <span>月租：¥{{ contract.monthly_rent }}/月</span>
                  <span>押金：¥{{ contract.deposit }}</span>
                </div>
              </div>

              <div class="manage-item__actions">
                <button v-if="contract.status === 'active'" class="danger-button" type="button" @click="changeContractStatus(contract.id, 'terminated')">
                  终止合同
                </button>
              </div>
            </article>
          </div>

          <div v-else-if="!loading.contracts" class="empty-card empty-card--soft">
            <h3 class="page-title page-title--section">暂无合同</h3>
            <p class="page-text">可从已确认的预约中创建第一份合同。</p>
          </div>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">收款记录</span>
              <h2 class="page-title page-title--section">账单收款</h2>
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
                  <span>付款人：{{ payment.payer?.real_name || payment.payer?.username || "暂无" }}</span>
                  <span>金额：¥{{ payment.amount }}</span>
                </div>
                <div class="booking-meta">
                  <span>到期日：{{ payment.due_date || "暂无" }}</span>
                  <span>支付方式：{{ formatPaymentMethod(payment.payment_method) }}</span>
                </div>
              </div>
            </article>
          </div>

          <div v-else-if="!loading.payments" class="empty-card empty-card--soft">
            <h3 class="page-title page-title--section">暂无账单</h3>
            <p class="page-text">租客签署合同后，相关账单会显示在这里。</p>
          </div>
        </div>

        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">维修处理</span>
              <h2 class="page-title page-title--section">维修工单</h2>
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
                <p class="house-address">{{ repair.house?.title || "房源" }} | {{ formatHouseAddress(repair.house) }}</p>
                <div class="booking-meta">
                  <span>租客：{{ repair.tenant?.real_name || repair.tenant?.username || "暂无" }}</span>
                  <span>提交时间：{{ formatDateTime(repair.created_at) }}</span>
                </div>
                <p class="page-text">{{ repair.description }}</p>
              </div>

              <div class="manage-item__actions">
                <button v-if="repair.status === 'submitted'" class="secondary-button" type="button" @click="changeRepairStatus(repair.id, 'processing')">开始处理</button>
                <button v-if="['submitted', 'processing'].includes(repair.status)" class="primary-button" type="button" @click="changeRepairStatus(repair.id, 'completed')">标记完成</button>
                <button v-if="repair.status === 'submitted'" class="danger-button" type="button" @click="changeRepairStatus(repair.id, 'rejected')">驳回</button>
              </div>
            </article>
          </div>

          <div v-else-if="!loading.repairs" class="empty-card empty-card--soft">
            <h3 class="page-title page-title--section">暂无维修工单</h3>
            <p class="page-text">租客提交的维修申请会显示在这里。</p>
          </div>
        </div>
      </div>

      <NewsManager />

      <MessageCenter
        eyebrow="消息中心"
        title="租客会话"
        description="查看未读咨询，并直接回复租客。"
        empty-text="租客从房源页联系你后，会话会显示在这里。"
      />
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import MessageCenter from "../../components/MessageCenter.vue";
import NewsManager from "../../components/NewsManager.vue";
import { fetchMyBookings, updateBookingStatus } from "../../api/booking";
import { createContract, fetchMyContracts, updateContractStatus } from "../../api/contract";
import {
  createHouse,
  deleteHouse,
  deleteHouseMedia,
  fetchMyHouses,
  addHouseMedia,
  updateHouse,
  updateHouseStatus,
} from "../../api/house";
import { fetchMyPayments } from "../../api/payment";
import { fetchMyRepairs, updateRepairStatus } from "../../api/repair";

const defaultHouseForm = () => ({
  title: "",
  province: "",
  city: "",
  district: "",
  community: "",
  address_detail: "",
  house_type: "",
  layout: "",
  area: "",
  rent: "",
  deposit: "",
  decoration: "",
  floor: "",
  total_floors: "",
  orientation: "",
  description: "",
  status: "draft",
});

const defaultContractForm = () => ({
  booking_id: "",
  start_date: "",
  end_date: "",
  payment_cycle: "monthly",
  content: "",
});

const form = reactive(defaultHouseForm());
const contractForm = reactive(defaultContractForm());
const houseFilters = reactive({ status: "", city: "", keyword: "" });
const bookingFilters = reactive({ status: "" });
const contractFilters = reactive({ status: "" });
const paymentFilters = reactive({ status: "", payment_type: "" });
const repairFilters = reactive({ status: "" });
const mediaUploading = reactive({});

const houses = ref([]);
const bookings = ref([]);
const contracts = ref([]);
const payments = ref([]);
const repairs = ref([]);
const editingId = ref(null);

const loading = reactive({
  houses: false,
  bookings: false,
  contracts: false,
  payments: false,
  repairs: false,
  submitHouse: false,
  submitContract: false,
});
const errors = reactive({
  houseForm: "",
  houses: "",
  bookings: "",
  contractForm: "",
  contracts: "",
  payments: "",
  repairs: "",
});
const messages = reactive({
  houseForm: "",
  contractForm: "",
});

const contractableBookings = computed(() =>
  bookings.value.filter((booking) => ["confirmed", "completed"].includes(booking.status))
);

function normalizePayload(source) {
  return {
    title: source.title,
    province: source.province || null,
    city: source.city,
    district: source.district,
    community: source.community || null,
    address_detail: source.address_detail,
    house_type: source.house_type || null,
    layout: source.layout,
    area: source.area,
    rent: source.rent,
    deposit: source.deposit || 0,
    decoration: source.decoration || null,
    floor: source.floor || null,
    total_floors: source.total_floors || null,
    orientation: source.orientation || null,
    description: source.description || null,
    status: source.status || "draft",
  };
}

function resetForm() {
  Object.assign(form, defaultHouseForm());
  editingId.value = null;
  errors.houseForm = "";
  messages.houseForm = "";
}

function resetContractForm() {
  Object.assign(contractForm, defaultContractForm());
  errors.contractForm = "";
  messages.contractForm = "";
}

function startCreate() {
  resetForm();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function startEdit(house) {
  Object.assign(form, {
    title: house.title || "",
    province: house.province || "",
    city: house.city || "",
    district: house.district || "",
    community: house.community || "",
    address_detail: house.address_detail || "",
    house_type: house.house_type || "",
    layout: house.layout || "",
    area: house.area || "",
    rent: house.rent || "",
    deposit: house.deposit || "",
    decoration: house.decoration || "",
    floor: house.floor || "",
    total_floors: house.total_floors || "",
    orientation: house.orientation || "",
    description: house.description || "",
    status: house.status || "draft",
  });
  editingId.value = house.id;
  errors.houseForm = "";
  messages.houseForm = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetHouseFilters() {
  houseFilters.status = "";
  houseFilters.city = "";
  houseFilters.keyword = "";
  loadMyHouses();
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

function formatHouseStatus(status) {
  return {
    draft: "草稿",
    available: "可租",
    rented: "已出租",
    repairing: "维修中",
    offline: "已下架",
  }[status] || status;
}

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

async function loadMyHouses() {
  loading.houses = true;
  errors.houses = "";
  try {
    const response = await fetchMyHouses(houseFilters);
    houses.value = response.data.data.items;
  } catch (error) {
    errors.houses = error.message || "加载房源失败。";
    houses.value = [];
  } finally {
    loading.houses = false;
  }
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
    errors.repairs = error.message || "加载维修工单失败。";
    repairs.value = [];
  } finally {
    loading.repairs = false;
  }
}

async function handleSubmit() {
  errors.houseForm = "";
  messages.houseForm = "";

  if (!form.title || !form.city || !form.district || !form.address_detail || !form.layout) {
    errors.houseForm = "标题、城市、区域、详细地址和户型不能为空。";
    return;
  }
  if (!form.area || !form.rent) {
    errors.houseForm = "面积和租金不能为空。";
    return;
  }

  loading.submitHouse = true;
  try {
    const payload = normalizePayload(form);
    if (editingId.value) {
      await updateHouse(editingId.value, payload);
      messages.houseForm = "房源更新成功。";
    } else {
      await createHouse(payload);
      messages.houseForm = "房源创建成功。";
    }
    resetForm();
    await loadMyHouses();
  } catch (error) {
    errors.houseForm = error.message || "保存房源失败。";
  } finally {
    loading.submitHouse = false;
  }
}

async function handleCreateContract() {
  errors.contractForm = "";
  messages.contractForm = "";

  if (!contractForm.booking_id || !contractForm.start_date || !contractForm.end_date) {
    errors.contractForm = "预约记录、开始日期和结束日期不能为空。";
    return;
  }

  loading.submitContract = true;
  try {
    await createContract({
      booking_id: contractForm.booking_id,
      start_date: contractForm.start_date,
      end_date: contractForm.end_date,
      payment_cycle: contractForm.payment_cycle,
      content: contractForm.content || null,
    });
    messages.contractForm = "合同创建成功。";
    resetContractForm();
    await loadContracts();
  } catch (error) {
    errors.contractForm = error.message || "创建合同失败。";
  } finally {
    loading.submitContract = false;
  }
}

async function changeHouseStatus(houseId, status) {
  errors.houses = "";
  try {
    await updateHouseStatus(houseId, { status });
    await loadMyHouses();
  } catch (error) {
    errors.houses = error.message || "更新房源状态失败。";
  }
}

async function handleDelete(houseId) {
  errors.houses = "";
  try {
    await deleteHouse(houseId);
    if (editingId.value === houseId) {
      resetForm();
    }
    await loadMyHouses();
  } catch (error) {
    errors.houses = error.message || "删除房源失败。";
  }
}

async function uploadHouseMedia(houseId, event) {
  const [file] = event.target.files || [];
  event.target.value = "";
  if (!file) {
    return;
  }

  errors.houses = "";
  mediaUploading[houseId] = true;
  try {
    const formData = new FormData();
    formData.append("file", file);
    await addHouseMedia(houseId, formData);
    await loadMyHouses();
  } catch (error) {
    errors.houses = error.message || "上传房源媒体失败。";
  } finally {
    mediaUploading[houseId] = false;
  }
}

async function removeHouseMedia(houseId, mediaId) {
  errors.houses = "";
  try {
    await deleteHouseMedia(houseId, mediaId);
    await loadMyHouses();
  } catch (error) {
    errors.houses = error.message || "删除房源媒体失败。";
  }
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

async function changeContractStatus(contractId, status) {
  errors.contracts = "";
  try {
    await updateContractStatus(contractId, { status });
    await loadContracts();
    await loadMyHouses();
  } catch (error) {
    errors.contracts = error.message || "更新合同状态失败。";
  }
}

async function changeRepairStatus(repairId, status) {
  errors.repairs = "";
  try {
    await updateRepairStatus(repairId, { status });
    await loadRepairs();
  } catch (error) {
    errors.repairs = error.message || "更新维修状态失败。";
  }
}

onMounted(async () => {
  await loadMyHouses();
  await loadBookings();
  await loadContracts();
  await loadPayments();
  await loadRepairs();
});
</script>
