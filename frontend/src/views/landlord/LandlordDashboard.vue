<template>
  <section class="page-shell page-shell--dashboard">
    <div class="workspace-shell">
      <aside class="workspace-sidebar" aria-label="房东功能导航">
        <div class="workspace-sidebar__header">
          <p class="workspace-sidebar__title">房东工作台</p>
        </div>

        <nav class="workspace-nav">
          <button
            v-for="(item, index) in landlordSections"
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
          <span class="eyebrow">房东控制台</span>
          <h1 class="hero-title">房源运营管理</h1>
          <p class="hero-text">管理房源、预约、合同、收款、维修和租客沟通。</p>
        </div>

        <div class="hero-actions">
          <button class="primary-button" type="button" @click="startCreate">发布房源</button>
          <RouterLink class="secondary-button" to="/houses">公开房源</RouterLink>
        </div>
      </div>

      <div v-show="activeSection === 'houses'" class="dashboard-grid workspace-panel">
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
            <label class="field"><span>标题</span><input v-model.trim="form.title" type="text" placeholder="例如：一室一厅" /></label>
            <label class="field">
              <span>类型</span>
              <select v-model="form.house_type">
                <option value="">选择类型</option>
                <option value="整租">整租</option>
                <option value="合租">合租</option>
                <option value="公寓">公寓</option>
              </select>
            </label>
            <label class="field field--full">
              <span>位置</span>
              <div class="location-picker">
                <select v-model="form.province" @change="handleProvinceChange">
                  <option value="">选择省份</option>
                  <option v-for="province in provinceOptions" :key="province" :value="province">
                    {{ province }}
                  </option>
                  <option :value="OTHER_REGION_VALUE">其他省份</option>
                </select>
                <select v-model="form.city" :disabled="!form.province || form.province === OTHER_REGION_VALUE" @change="handleCityChange">
                  <option value="">选择城市</option>
                  <option v-for="city in cityOptions" :key="city" :value="city">
                    {{ city }}
                  </option>
                  <option v-if="form.province && form.province !== OTHER_REGION_VALUE" :value="OTHER_REGION_VALUE">其他城市</option>
                </select>
                <select v-model="form.district" :disabled="!form.city || form.city === OTHER_REGION_VALUE" @change="handleDistrictChange">
                  <option value="">选择区域</option>
                  <option v-for="district in districtOptions" :key="district" :value="district">
                    {{ district }}
                  </option>
                  <option v-if="form.city && form.city !== OTHER_REGION_VALUE" :value="OTHER_REGION_VALUE">其他区域</option>
                </select>
              </div>
            </label>
            <div v-if="usesCustomRegion" class="custom-region-grid field--full">
              <label v-if="form.province === OTHER_REGION_VALUE" class="field">
                <span>省份</span>
                <input v-model.trim="form.custom_province" type="text" placeholder="请输入省份" />
              </label>
              <label v-if="form.province === OTHER_REGION_VALUE || form.city === OTHER_REGION_VALUE" class="field">
                <span>城市</span>
                <input v-model.trim="form.custom_city" type="text" placeholder="请输入城市" />
              </label>
              <label v-if="form.province === OTHER_REGION_VALUE || form.city === OTHER_REGION_VALUE || form.district === OTHER_REGION_VALUE" class="field">
                <span>区域</span>
                <input v-model.trim="form.custom_district" type="text" placeholder="请输入区域" />
              </label>
            </div>
            <label class="field"><span>小区</span><input v-model.trim="form.community" type="text" placeholder="请输入小区名称" /></label>
            <label class="field"><span>详细地址</span><input v-model.trim="form.address_detail" type="text" placeholder="楼栋、单元、门牌号" /></label>
            <label class="field">
              <span>户型</span>
              <select v-model="form.layout">
                <option value="">选择户型</option>
                <option value="一室一厅">一室一厅</option>
                <option value="两室一厅">两室一厅</option>
                <option value="三室一厅">三室一厅</option>
                <option value="三室两厅">三室两厅</option>
                <option value="四室及以上">四室及以上</option>
                <option value="单间">单间</option>
              </select>
            </label>
            <label class="field"><span>面积</span><input v-model.number="form.area" type="number" min="1" step="0.1" placeholder="89" /></label>
            <label class="field"><span>租金</span><input v-model.number="form.rent" type="number" min="0" step="0.01" placeholder="5500" /></label>
            <label class="field field--full">
              <span>描述</span>
              <textarea v-model.trim="form.description" rows="3" placeholder="补充交通、装修、配套和周边信息" />
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
                    <img v-if="media.media_type === 'image'" :src="resolveAssetUrl(media.file_url)" :alt="house.title" />
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

      <div v-show="activeSection === 'bookings'" class="page-card workspace-panel">
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

      <div v-show="activeSection === 'contracts'" class="dashboard-grid workspace-panel">
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

      <div v-show="activeSection === 'operations'" class="dashboard-grid workspace-panel">
        <div class="page-card">
          <div class="section-head section-head--compact">
            <div>
              <span class="eyebrow">收款记录</span>
              <h2 class="page-title page-title--section">账单收款</h2>
            </div>
            <button class="ghost-button" type="button" :disabled="loading.payments" @click="handleOverdueScan">
              扫描逾期
            </button>
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
            <div class="manage-item__actions" v-if="payment.status === 'paid'">
              <button class="danger-button" type="button" @click="handleRefund(payment.id)">登记退款</button>
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

      <NewsManager v-show="activeSection === 'news'" class="workspace-panel" />

      <MessageCenter
        v-show="activeSection === 'messages'"
        class="workspace-panel"
        eyebrow="消息中心"
        title="租客会话"
        description="查看未读咨询，并直接回复租客。"
        empty-text="租客从房源页联系你后，会话会显示在这里。"
      />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import MessageCenter from "../../components/MessageCenter.vue";
import NewsManager from "../../components/NewsManager.vue";
import { resolveAssetUrl } from "../../api/assets";
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
import { fetchMyPayments, markOverduePayments, refundPayment } from "../../api/payment";
import { fetchMyRepairs, updateRepairStatus } from "../../api/repair";

const landlordSections = [
  { key: "houses", label: "房源管理" },
  { key: "bookings", label: "看房预约" },
  { key: "contracts", label: "合同管理" },
  { key: "operations", label: "收款维修" },
  { key: "news", label: "公告管理" },
  { key: "messages", label: "消息中心" },
];

const activeSection = ref("houses");

const OTHER_REGION_VALUE = "__other__";
const REGION_OPTIONS = [
  {
    name: "北京市",
    cities: [
      { name: "北京市", districts: ["东城区", "西城区", "朝阳区", "海淀区", "丰台区", "通州区", "昌平区", "大兴区"] },
    ],
  },
  {
    name: "上海市",
    cities: [
      { name: "上海市", districts: ["黄浦区", "徐汇区", "长宁区", "静安区", "普陀区", "浦东新区", "闵行区", "宝山区"] },
    ],
  },
  {
    name: "天津市",
    cities: [
      { name: "天津市", districts: ["和平区", "河东区", "河西区", "南开区", "河北区", "红桥区", "滨海新区", "西青区"] },
    ],
  },
  {
    name: "重庆市",
    cities: [
      { name: "重庆市", districts: ["渝中区", "江北区", "南岸区", "九龙坡区", "沙坪坝区", "渝北区", "巴南区", "两江新区"] },
    ],
  },
  {
    name: "河北省",
    cities: [
      { name: "石家庄市", districts: ["长安区", "桥西区", "新华区", "裕华区", "藁城区", "鹿泉区"] },
      { name: "唐山市", districts: ["路南区", "路北区", "开平区", "丰南区", "丰润区", "曹妃甸区"] },
      { name: "保定市", districts: ["竞秀区", "莲池区", "满城区", "清苑区", "徐水区"] },
      { name: "廊坊市", districts: ["广阳区", "安次区", "三河市", "固安县", "香河县"] },
    ],
  },
  {
    name: "山西省",
    cities: [
      { name: "太原市", districts: ["小店区", "迎泽区", "杏花岭区", "万柏林区", "晋源区"] },
      { name: "大同市", districts: ["平城区", "云冈区", "新荣区", "云州区"] },
      { name: "晋中市", districts: ["榆次区", "太谷区", "祁县", "平遥县"] },
    ],
  },
  {
    name: "内蒙古自治区",
    cities: [
      { name: "呼和浩特市", districts: ["新城区", "回民区", "玉泉区", "赛罕区", "土默特左旗"] },
      { name: "包头市", districts: ["东河区", "昆都仑区", "青山区", "九原区"] },
      { name: "鄂尔多斯市", districts: ["东胜区", "康巴什区", "达拉特旗", "伊金霍洛旗"] },
    ],
  },
  {
    name: "辽宁省",
    cities: [
      { name: "沈阳市", districts: ["和平区", "沈河区", "大东区", "皇姑区", "铁西区", "浑南区", "于洪区"] },
      { name: "大连市", districts: ["中山区", "西岗区", "沙河口区", "甘井子区", "旅顺口区", "金州区"] },
      { name: "鞍山市", districts: ["铁东区", "铁西区", "立山区", "千山区"] },
    ],
  },
  {
    name: "吉林省",
    cities: [
      { name: "长春市", districts: ["南关区", "宽城区", "朝阳区", "二道区", "绿园区", "净月区"] },
      { name: "吉林市", districts: ["昌邑区", "龙潭区", "船营区", "丰满区"] },
      { name: "延边朝鲜族自治州", districts: ["延吉市", "图们市", "敦化市", "珲春市"] },
    ],
  },
  {
    name: "黑龙江省",
    cities: [
      { name: "哈尔滨市", districts: ["道里区", "南岗区", "道外区", "香坊区", "松北区", "平房区"] },
      { name: "齐齐哈尔市", districts: ["龙沙区", "建华区", "铁锋区", "昂昂溪区"] },
      { name: "大庆市", districts: ["萨尔图区", "龙凤区", "让胡路区", "红岗区"] },
    ],
  },
  {
    name: "浙江省",
    cities: [
      { name: "杭州市", districts: ["上城区", "拱墅区", "西湖区", "滨江区", "萧山区", "余杭区", "临平区", "钱塘区"] },
      { name: "宁波市", districts: ["海曙区", "江北区", "北仑区", "镇海区", "鄞州区"] },
      { name: "温州市", districts: ["鹿城区", "龙湾区", "瓯海区", "洞头区"] },
      { name: "绍兴市", districts: ["越城区", "柯桥区", "上虞区", "诸暨市"] },
      { name: "嘉兴市", districts: ["南湖区", "秀洲区", "嘉善县", "海宁市"] },
      { name: "金华市", districts: ["婺城区", "金东区", "义乌市", "东阳市"] },
    ],
  },
  {
    name: "江苏省",
    cities: [
      { name: "南京市", districts: ["玄武区", "秦淮区", "建邺区", "鼓楼区", "浦口区", "江宁区"] },
      { name: "苏州市", districts: ["姑苏区", "虎丘区", "吴中区", "相城区", "吴江区", "工业园区"] },
      { name: "无锡市", districts: ["梁溪区", "锡山区", "惠山区", "滨湖区", "新吴区"] },
      { name: "常州市", districts: ["天宁区", "钟楼区", "新北区", "武进区", "金坛区"] },
      { name: "南通市", districts: ["崇川区", "通州区", "海门区", "如东县"] },
      { name: "徐州市", districts: ["鼓楼区", "云龙区", "泉山区", "铜山区", "贾汪区"] },
    ],
  },
  {
    name: "安徽省",
    cities: [
      { name: "合肥市", districts: ["瑶海区", "庐阳区", "蜀山区", "包河区", "肥西县", "长丰县"] },
      { name: "芜湖市", districts: ["镜湖区", "弋江区", "鸠江区", "湾沚区"] },
      { name: "蚌埠市", districts: ["龙子湖区", "蚌山区", "禹会区", "淮上区"] },
      { name: "阜阳市", districts: ["颍州区", "颍东区", "颍泉区", "临泉县"] },
    ],
  },
  {
    name: "福建省",
    cities: [
      { name: "福州市", districts: ["鼓楼区", "台江区", "仓山区", "晋安区", "马尾区", "长乐区"] },
      { name: "厦门市", districts: ["思明区", "湖里区", "集美区", "海沧区", "同安区", "翔安区"] },
      { name: "泉州市", districts: ["鲤城区", "丰泽区", "洛江区", "泉港区", "晋江市", "石狮市"] },
      { name: "漳州市", districts: ["芗城区", "龙文区", "龙海区", "长泰区"] },
    ],
  },
  {
    name: "江西省",
    cities: [
      { name: "南昌市", districts: ["东湖区", "西湖区", "青云谱区", "青山湖区", "红谷滩区", "新建区"] },
      { name: "赣州市", districts: ["章贡区", "南康区", "赣县区", "信丰县"] },
      { name: "九江市", districts: ["浔阳区", "濂溪区", "柴桑区", "瑞昌市"] },
    ],
  },
  {
    name: "山东省",
    cities: [
      { name: "济南市", districts: ["历下区", "市中区", "槐荫区", "天桥区", "历城区", "高新区"] },
      { name: "青岛市", districts: ["市南区", "市北区", "李沧区", "崂山区", "黄岛区", "城阳区"] },
      { name: "烟台市", districts: ["芝罘区", "福山区", "牟平区", "莱山区", "蓬莱区"] },
      { name: "潍坊市", districts: ["奎文区", "潍城区", "坊子区", "寒亭区"] },
      { name: "临沂市", districts: ["兰山区", "罗庄区", "河东区", "沂南县"] },
    ],
  },
  {
    name: "河南省",
    cities: [
      { name: "郑州市", districts: ["中原区", "二七区", "管城回族区", "金水区", "惠济区", "郑东新区"] },
      { name: "洛阳市", districts: ["老城区", "西工区", "涧西区", "洛龙区", "偃师区"] },
      { name: "开封市", districts: ["龙亭区", "顺河回族区", "鼓楼区", "禹王台区", "祥符区"] },
      { name: "新乡市", districts: ["红旗区", "卫滨区", "凤泉区", "牧野区"] },
    ],
  },
  {
    name: "湖北省",
    cities: [
      { name: "武汉市", districts: ["江岸区", "江汉区", "硚口区", "汉阳区", "武昌区", "洪山区", "东湖高新区"] },
      { name: "襄阳市", districts: ["襄城区", "樊城区", "襄州区", "枣阳市"] },
      { name: "宜昌市", districts: ["西陵区", "伍家岗区", "点军区", "猇亭区", "夷陵区"] },
      { name: "黄石市", districts: ["黄石港区", "西塞山区", "下陆区", "铁山区"] },
    ],
  },
  {
    name: "湖南省",
    cities: [
      { name: "长沙市", districts: ["芙蓉区", "天心区", "岳麓区", "开福区", "雨花区", "望城区"] },
      { name: "株洲市", districts: ["荷塘区", "芦淞区", "石峰区", "天元区", "渌口区"] },
      { name: "湘潭市", districts: ["雨湖区", "岳塘区", "湘潭县", "湘乡市"] },
      { name: "岳阳市", districts: ["岳阳楼区", "云溪区", "君山区", "岳阳县"] },
    ],
  },
  {
    name: "广东省",
    cities: [
      { name: "广州市", districts: ["越秀区", "海珠区", "荔湾区", "天河区", "白云区", "番禺区"] },
      { name: "深圳市", districts: ["福田区", "罗湖区", "南山区", "宝安区", "龙岗区", "龙华区"] },
      { name: "佛山市", districts: ["禅城区", "南海区", "顺德区", "三水区", "高明区"] },
      { name: "东莞市", districts: ["莞城区", "南城区", "东城区", "万江区", "松山湖"] },
      { name: "珠海市", districts: ["香洲区", "斗门区", "金湾区", "横琴新区"] },
      { name: "惠州市", districts: ["惠城区", "惠阳区", "博罗县", "惠东县"] },
      { name: "中山市", districts: ["石岐街道", "东区街道", "西区街道", "南区街道", "火炬开发区"] },
    ],
  },
  {
    name: "广西壮族自治区",
    cities: [
      { name: "南宁市", districts: ["兴宁区", "青秀区", "江南区", "西乡塘区", "良庆区", "邕宁区"] },
      { name: "柳州市", districts: ["城中区", "鱼峰区", "柳南区", "柳北区", "柳江区"] },
      { name: "桂林市", districts: ["秀峰区", "叠彩区", "象山区", "七星区", "临桂区"] },
    ],
  },
  {
    name: "海南省",
    cities: [
      { name: "海口市", districts: ["秀英区", "龙华区", "琼山区", "美兰区"] },
      { name: "三亚市", districts: ["海棠区", "吉阳区", "天涯区", "崖州区"] },
      { name: "儋州市", districts: ["那大镇", "白马井镇", "排浦镇", "王五镇"] },
    ],
  },
  {
    name: "四川省",
    cities: [
      { name: "成都市", districts: ["锦江区", "青羊区", "金牛区", "武侯区", "成华区", "高新区", "天府新区"] },
      { name: "绵阳市", districts: ["涪城区", "游仙区", "安州区"] },
      { name: "德阳市", districts: ["旌阳区", "罗江区", "广汉市", "什邡市"] },
      { name: "乐山市", districts: ["市中区", "沙湾区", "五通桥区", "峨眉山市"] },
      { name: "宜宾市", districts: ["翠屏区", "南溪区", "叙州区", "江安县"] },
    ],
  },
  {
    name: "贵州省",
    cities: [
      { name: "贵阳市", districts: ["南明区", "云岩区", "花溪区", "乌当区", "白云区", "观山湖区"] },
      { name: "遵义市", districts: ["红花岗区", "汇川区", "播州区", "仁怀市"] },
      { name: "六盘水市", districts: ["钟山区", "六枝特区", "水城区", "盘州市"] },
    ],
  },
  {
    name: "云南省",
    cities: [
      { name: "昆明市", districts: ["五华区", "盘龙区", "官渡区", "西山区", "呈贡区", "安宁市"] },
      { name: "曲靖市", districts: ["麒麟区", "沾益区", "马龙区", "宣威市"] },
      { name: "大理白族自治州", districts: ["大理市", "祥云县", "宾川县", "洱源县"] },
      { name: "丽江市", districts: ["古城区", "玉龙纳西族自治县", "永胜县", "华坪县"] },
    ],
  },
  {
    name: "西藏自治区",
    cities: [
      { name: "拉萨市", districts: ["城关区", "堆龙德庆区", "达孜区", "林周县"] },
      { name: "日喀则市", districts: ["桑珠孜区", "南木林县", "江孜县", "定日县"] },
    ],
  },
  {
    name: "陕西省",
    cities: [
      { name: "西安市", districts: ["新城区", "碑林区", "莲湖区", "雁塔区", "未央区", "长安区", "高新区"] },
      { name: "咸阳市", districts: ["秦都区", "杨陵区", "渭城区", "兴平市"] },
      { name: "宝鸡市", districts: ["渭滨区", "金台区", "陈仓区", "凤翔区"] },
    ],
  },
  {
    name: "甘肃省",
    cities: [
      { name: "兰州市", districts: ["城关区", "七里河区", "西固区", "安宁区", "红古区"] },
      { name: "天水市", districts: ["秦州区", "麦积区", "清水县", "秦安县"] },
      { name: "酒泉市", districts: ["肃州区", "玉门市", "敦煌市", "金塔县"] },
    ],
  },
  {
    name: "青海省",
    cities: [
      { name: "西宁市", districts: ["城东区", "城中区", "城西区", "城北区", "湟中区"] },
      { name: "海东市", districts: ["乐都区", "平安区", "民和回族土族自治县", "互助土族自治县"] },
    ],
  },
  {
    name: "宁夏回族自治区",
    cities: [
      { name: "银川市", districts: ["兴庆区", "西夏区", "金凤区", "永宁县", "贺兰县"] },
      { name: "吴忠市", districts: ["利通区", "红寺堡区", "青铜峡市", "盐池县"] },
    ],
  },
  {
    name: "新疆维吾尔自治区",
    cities: [
      { name: "乌鲁木齐市", districts: ["天山区", "沙依巴克区", "新市区", "水磨沟区", "头屯河区"] },
      { name: "克拉玛依市", districts: ["克拉玛依区", "独山子区", "白碱滩区", "乌尔禾区"] },
      { name: "昌吉回族自治州", districts: ["昌吉市", "阜康市", "呼图壁县", "玛纳斯县"] },
    ],
  },
  {
    name: "香港特别行政区",
    cities: [
      { name: "香港特别行政区", districts: ["中西区", "湾仔区", "东区", "南区", "油尖旺区", "深水埗区", "九龙城区", "沙田区"] },
    ],
  },
  {
    name: "澳门特别行政区",
    cities: [
      { name: "澳门特别行政区", districts: ["花地玛堂区", "圣安多尼堂区", "大堂区", "望德堂区", "风顺堂区", "氹仔", "路环"] },
    ],
  },
  {
    name: "台湾省",
    cities: [
      { name: "台北市", districts: ["中正区", "大同区", "中山区", "松山区", "大安区", "信义区"] },
      { name: "新北市", districts: ["板桥区", "新庄区", "中和区", "永和区", "三重区", "新店区"] },
      { name: "高雄市", districts: ["新兴区", "前金区", "苓雅区", "鼓山区", "左营区", "三民区"] },
    ],
  },
];

const defaultHouseForm = () => ({
  title: "",
  province: "",
  city: "",
  district: "",
  custom_province: "",
  custom_city: "",
  custom_district: "",
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

const provinceOptions = computed(() => REGION_OPTIONS.map((region) => region.name));
const selectedProvince = computed(() => REGION_OPTIONS.find((region) => region.name === form.province));
const cityOptions = computed(() => selectedProvince.value?.cities.map((city) => city.name) || []);
const selectedCity = computed(() => selectedProvince.value?.cities.find((city) => city.name === form.city));
const districtOptions = computed(() => selectedCity.value?.districts || []);
const usesCustomRegion = computed(() =>
  [form.province, form.city, form.district].includes(OTHER_REGION_VALUE)
);

const contractableBookings = computed(() =>
  bookings.value.filter((booking) => ["confirmed", "completed"].includes(booking.status))
);

function resolveRegion(source) {
  return {
    province: source.province === OTHER_REGION_VALUE ? source.custom_province : source.province,
    city:
      source.province === OTHER_REGION_VALUE || source.city === OTHER_REGION_VALUE
        ? source.custom_city
        : source.city,
    district:
      source.province === OTHER_REGION_VALUE || source.city === OTHER_REGION_VALUE || source.district === OTHER_REGION_VALUE
        ? source.custom_district
        : source.district,
  };
}

function normalizePayload(source) {
  const region = resolveRegion(source);
  return {
    title: source.title,
    province: region.province || null,
    city: region.city,
    district: region.district,
    community: source.community || null,
    address_detail: source.address_detail,
    house_type: source.house_type || null,
    layout: source.layout,
    area: source.area,
    rent: source.rent,
    deposit: source.deposit === "" || source.deposit == null ? source.rent || 0 : source.deposit,
    decoration: source.decoration || null,
    floor: source.floor || null,
    total_floors: source.total_floors || null,
    orientation: source.orientation || null,
    description: source.description || null,
    status: source.status || "draft",
  };
}

function handleProvinceChange() {
  form.city = "";
  form.district = "";
  if (form.province !== OTHER_REGION_VALUE) {
    form.custom_province = "";
  }
  form.custom_city = "";
  form.custom_district = "";
}

function handleCityChange() {
  form.district = "";
  if (form.city !== OTHER_REGION_VALUE) {
    form.custom_city = "";
  }
  form.custom_district = "";
}

function handleDistrictChange() {
  if (form.district !== OTHER_REGION_VALUE) {
    form.custom_district = "";
  }
}

function applyRegionToForm(province, city, district) {
  form.custom_province = "";
  form.custom_city = "";
  form.custom_district = "";

  if (!province) {
    form.province = "";
    form.city = "";
    form.district = "";
    return;
  }

  const provinceOption = REGION_OPTIONS.find((region) => region.name === province);
  if (!provinceOption) {
    form.province = OTHER_REGION_VALUE;
    form.city = "";
    form.district = "";
    form.custom_province = province;
    form.custom_city = city || "";
    form.custom_district = district || "";
    return;
  }

  form.province = province;
  const cityOption = provinceOption.cities.find((item) => item.name === city);
  if (!city) {
    form.city = "";
    form.district = "";
    return;
  }
  if (!cityOption) {
    form.city = OTHER_REGION_VALUE;
    form.district = "";
    form.custom_city = city;
    form.custom_district = district || "";
    return;
  }

  form.city = city;
  if (!district) {
    form.district = "";
    return;
  }
  if (cityOption.districts.includes(district)) {
    form.district = district;
    return;
  }

  form.district = OTHER_REGION_VALUE;
  form.custom_district = district;
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
  activeSection.value = "houses";
  resetForm();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function startEdit(house) {
  activeSection.value = "houses";
  Object.assign(form, {
    title: house.title || "",
    province: "",
    city: "",
    district: "",
    custom_province: "",
    custom_city: "",
    custom_district: "",
    community: house.community || "",
    address_detail: house.address_detail || "",
    house_type: house.house_type || "",
    layout: house.layout || "",
    area: house.area || "",
    rent: house.rent || "",
    deposit: house.deposit ?? "",
    decoration: house.decoration || "",
    floor: house.floor || "",
    total_floors: house.total_floors || "",
    orientation: house.orientation || "",
    description: house.description || "",
    status: house.status || "draft",
  });
  applyRegionToForm(house.province || "", house.city || "", house.district || "");
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

async function handleOverdueScan() {
  errors.payments = "";
  try {
    await markOverduePayments();
    await loadPayments();
  } catch (error) {
    errors.payments = error.message || "扫描逾期账单失败。";
  }
}

async function handleRefund(paymentId) {
  errors.payments = "";
  try {
    await refundPayment(paymentId, { reason: "landlord registered refund" });
    await loadPayments();
  } catch (error) {
    errors.payments = error.message || "登记退款失败。";
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

  const region = resolveRegion(form);
  if (!region.province || !region.city || !region.district) {
    errors.houseForm = "请按省、市、区选择或填写完整位置。";
    return;
  }
  if (!form.title || !form.address_detail || !form.layout) {
    errors.houseForm = "标题、详细地址和户型不能为空。";
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
