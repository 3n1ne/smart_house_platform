<template>
  <section class="rental-detail-page">
    <div v-if="loading" class="page-card empty-card">
      <h1 class="page-title page-title--section">正在加载房源详情</h1>
      <p class="page-text">正在获取最新的房源信息。</p>
    </div>

    <div v-else-if="errorMessage" class="page-card empty-card">
      <h1 class="page-title page-title--section">房源详情加载失败</h1>
      <p class="form-message form-message--error">{{ errorMessage }}</p>
      <RouterLink class="secondary-button" to="/houses">返回房源列表</RouterLink>
    </div>

    <template v-else-if="house">
      <div class="listing-detail-nav">
        <RouterLink class="text-link" to="/houses">返回房源列表</RouterLink>
        <span>房源编号 {{ String(house.id).padStart(3, "0") }}</span>
      </div>

      <section class="listing-gallery">
        <div class="listing-gallery__main">
          <img
            v-if="primaryMedia && primaryMedia.media_type === 'image'"
            :src="resolveAssetUrl(primaryMedia.file_url)"
            :alt="house.title"
          />
          <div v-else class="house-cover__placeholder house-cover__placeholder--large">暂无图片</div>
        </div>
        <div class="listing-gallery__side">
          <div v-for="index in 4" :key="index" class="listing-gallery__tile">
            <img
              v-if="galleryPreview[index - 1]?.media_type === 'image'"
              :src="resolveAssetUrl(galleryPreview[index - 1].file_url)"
              :alt="house.title"
            />
            <div v-else class="house-cover__placeholder">暂无图片</div>
          </div>
        </div>
      </section>

      <div class="listing-detail-layout">
        <main class="listing-detail-main">
          <section class="listing-headline">
            <div>
              <div class="detail-badges">
                <span class="tag">{{ formatHouseStatus(house.status) }}</span>
                <span class="tag tag--light">{{ house.house_type || "住宅" }}</span>
                <span class="tag tag--light">{{ house.layout || "户型待补充" }}</span>
              </div>
              <h1 class="page-title">{{ house.title }}</h1>
              <p class="house-address">{{ fullAddress || "地址待补充" }}</p>
            </div>
            <div class="listing-headline__price">
              <strong>{{ formatMoney(house.rent) }}</strong>
              <span>/ 月</span>
            </div>
          </section>

          <section class="listing-stat-grid">
            <article>
              <span>面积</span>
              <strong>{{ formatArea(house.area) }}</strong>
            </article>
            <article>
              <span>楼层</span>
              <strong>{{ formatFloor(house.floor, house.total_floors) }}</strong>
            </article>
            <article>
              <span>朝向</span>
              <strong>{{ house.orientation || "未提供" }}</strong>
            </article>
            <article>
              <span>押金</span>
              <strong>{{ formatMoney(house.deposit || 0) }}</strong>
            </article>
          </section>

          <section class="listing-section">
            <span class="eyebrow">房源描述</span>
            <h2 class="page-title page-title--section">房子和入住信息</h2>
            <p class="page-text detail-description">
              {{ house.description || "该房源暂未补充更多描述。" }}
            </p>
          </section>

          <section class="listing-section">
            <span class="eyebrow">核心信息</span>
            <div class="listing-fact-grid">
              <div v-for="item in listingFacts" :key="item.label" class="detail-row">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
          </section>

          <section class="listing-section listing-map-summary">
            <div>
              <span class="eyebrow">周边位置</span>
              <h2 class="page-title page-title--section">{{ house.community || house.district || "位置概览" }}</h2>
              <p class="page-text">{{ fullAddress || "房东暂未补充详细地址。" }}</p>
            </div>
            <div class="listing-map-summary__canvas">
              <span>{{ house.district || house.city || "位置" }}</span>
            </div>
          </section>
        </main>

        <aside class="listing-action-rail">
          <div class="listing-action-card">
            <div class="listing-action-card__price">
              <strong>{{ formatMoney(house.rent) }}</strong>
              <span>/ 月</span>
            </div>
            <p>{{ house.layout || "户型待补充" }} · {{ formatArea(house.area) }} · {{ house.district || "区域待补充" }}</p>
            <RouterLink v-if="!authStore.isAuthenticated" class="primary-button" to="/login">
              登录后预约
            </RouterLink>
          </div>

          <div class="listing-action-card">
            <div class="section-head section-head--compact">
              <div>
                <span class="eyebrow">看房预约</span>
                <h2 class="page-title page-title--section">预约看房</h2>
              </div>
            </div>

            <form v-if="canBook" class="form-stack" @submit.prevent="handleBooking">
              <label class="field">
                <span>预约时间</span>
                <input v-model="bookingForm.appointmentTime" type="datetime-local" />
              </label>

              <label class="field">
                <span>备注</span>
                <textarea
                  v-model.trim="bookingForm.remark"
                  rows="4"
                  placeholder="填写你的看房需求或想咨询的问题"
                />
              </label>

              <p v-if="bookingError" class="form-message form-message--error">{{ bookingError }}</p>
              <p v-if="bookingSuccess" class="form-message form-message--success">{{ bookingSuccess }}</p>

              <button class="primary-button" type="submit" :disabled="submittingBooking">
                {{ submittingBooking ? "提交中..." : "提交预约" }}
              </button>
            </form>

            <div v-else class="empty-card empty-card--soft">
              <p class="page-text">{{ bookingUnavailableText }}</p>
            </div>
          </div>

          <div class="listing-action-card">
            <div class="section-head section-head--compact">
              <div>
                <span class="eyebrow">在线沟通</span>
                <h2 class="page-title page-title--section">联系房东</h2>
              </div>
            </div>

            <form v-if="canMessage" class="form-stack" @submit.prevent="handleSendMessage">
              <label class="field">
                <span>留言内容</span>
                <textarea
                  v-model.trim="messageForm.content"
                  rows="4"
                  placeholder="咨询看房安排、入住时间、费用等问题"
                />
              </label>

              <p v-if="messageError" class="form-message form-message--error">{{ messageError }}</p>
              <p v-if="messageSuccess" class="form-message form-message--success">{{ messageSuccess }}</p>

              <button class="primary-button" type="submit" :disabled="submittingMessage">
                {{ submittingMessage ? "发送中..." : "发送消息" }}
              </button>
            </form>

            <div v-else class="empty-card empty-card--soft">
              <p class="page-text">{{ messageUnavailableText }}</p>
            </div>
          </div>
        </aside>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import { createBooking } from "../../api/booking";
import { resolveAssetUrl } from "../../api/assets";
import { fetchHouseDetail } from "../../api/house";
import { sendMessage } from "../../api/message";
import { useAuthStore } from "../../stores/auth";

const route = useRoute();
const authStore = useAuthStore();
const loading = ref(false);
const errorMessage = ref("");
const house = ref(null);
const submittingBooking = ref(false);
const submittingMessage = ref(false);
const bookingError = ref("");
const bookingSuccess = ref("");
const messageError = ref("");
const messageSuccess = ref("");
const bookingForm = reactive({
  appointmentTime: "",
  remark: "",
});
const messageForm = reactive({
  content: "",
});

const allMedia = computed(() => house.value?.media_items || []);
const primaryMedia = computed(() => allMedia.value[0] || null);
const galleryPreview = computed(() => allMedia.value.slice(1, 5));
const fullAddress = computed(() =>
  [
    house.value?.province,
    house.value?.city,
    house.value?.district,
    house.value?.community,
    house.value?.address_detail,
  ]
    .filter(Boolean)
    .join(" ")
);
const listingFacts = computed(() => [
  { label: "小区", value: house.value?.community || "未提供" },
  { label: "城市区域", value: [house.value?.city, house.value?.district].filter(Boolean).join(" / ") || "未提供" },
  { label: "装修", value: house.value?.decoration || "未提供" },
  { label: "类型", value: house.value?.house_type || "住宅" },
  { label: "房东", value: house.value?.landlord?.real_name || house.value?.landlord?.username || "个人房东" },
  { label: "状态", value: formatHouseStatus(house.value?.status) },
]);
const canBook = computed(
  () =>
    authStore.isAuthenticated &&
    authStore.user?.role === "tenant" &&
    house.value?.status === "available"
);
const canMessage = computed(
  () =>
    authStore.isAuthenticated &&
    authStore.user?.role === "tenant" &&
    Boolean(house.value?.landlord?.id) &&
    authStore.user?.id !== house.value?.landlord?.id
);
const bookingUnavailableText = computed(() => {
  if (!authStore.isAuthenticated) return "请先以租客身份登录后提交看房预约。";
  if (authStore.user?.role !== "tenant") return "只有租客账号可以创建看房预约。";
  return "该房源当前不可预约。";
});
const messageUnavailableText = computed(() => {
  if (!authStore.isAuthenticated) return "请先以租客身份登录后联系房东。";
  if (authStore.user?.role !== "tenant") return "只有租客账号可以在这里发起对话。";
  return "该房源暂时无法联系房东。";
});

function formatFloor(floor, totalFloors) {
  if (!floor && !totalFloors) {
    return "未提供";
  }
  if (!totalFloors) {
    return `${floor}`;
  }
  return `${floor} / ${totalFloors}`;
}

function formatArea(area) {
  return area ? `${Number(area).toLocaleString("zh-CN")} 平方米` : "面积待补充";
}

function formatMoney(value) {
  return `¥${Number(value || 0).toLocaleString("zh-CN", { maximumFractionDigits: 0 })}`;
}

function formatHouseStatus(status) {
  return {
    draft: "草稿",
    available: "可租",
    rented: "已出租",
    repairing: "维修中",
    offline: "已下架",
  }[status] || status || "状态待补充";
}

async function loadHouseDetail() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await fetchHouseDetail(route.params.id);
    house.value = response.data.data;
  } catch (error) {
    errorMessage.value = error.message || "房源详情加载失败。";
  } finally {
    loading.value = false;
  }
}

async function handleBooking() {
  bookingError.value = "";
  bookingSuccess.value = "";

  if (!bookingForm.appointmentTime) {
    bookingError.value = "请选择预约时间。";
    return;
  }

  submittingBooking.value = true;
  try {
    await createBooking({
      house_id: house.value.id,
      appointment_time: new Date(bookingForm.appointmentTime).toISOString(),
      remark: bookingForm.remark || null,
    });
    bookingForm.appointmentTime = "";
    bookingForm.remark = "";
    bookingSuccess.value = "预约申请已提交，可在租客控制台查看进度。";
  } catch (error) {
    bookingError.value = error.message || "创建预约失败。";
  } finally {
    submittingBooking.value = false;
  }
}

async function handleSendMessage() {
  messageError.value = "";
  messageSuccess.value = "";

  if (!messageForm.content) {
    messageError.value = "请输入留言内容。";
    return;
  }

  if (!house.value?.landlord?.id) {
    messageError.value = "当前无法获取房东联系方式。";
    return;
  }

  submittingMessage.value = true;
  try {
    await sendMessage({
      receiver_id: house.value.landlord.id,
      house_id: house.value.id,
      content: messageForm.content,
    });
    messageForm.content = "";
    messageSuccess.value = "消息已发送，可在租客控制台继续沟通。";
  } catch (error) {
    messageError.value = error.message || "消息发送失败。";
  } finally {
    submittingMessage.value = false;
  }
}

onMounted(async () => {
  await authStore.initialize();
  await loadHouseDetail();
});
</script>
