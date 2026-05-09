<template>
  <section class="page-shell">
    <div v-if="loading" class="page-card empty-card">
      <h1 class="page-title page-title--section">正在加载房源详情</h1>
      <p class="page-text">正在获取最新的房源信息。</p>
    </div>

    <div v-else-if="errorMessage" class="page-card empty-card">
      <h1 class="page-title page-title--section">房源详情加载失败</h1>
      <p class="form-message form-message--error">{{ errorMessage }}</p>
      <RouterLink class="secondary-button" to="/houses">返回房源列表</RouterLink>
    </div>

    <div v-else-if="house" class="stack-section">
      <section class="detail-cover">
        <img v-if="primaryMedia" :src="primaryMedia.file_url" :alt="house.title" />
        <div v-else class="house-cover__placeholder house-cover__placeholder--large">暂无图片</div>
      </section>

      <div v-if="gallery.length" class="gallery-grid">
        <div v-for="item in gallery" :key="item.id" class="gallery-item">
          <img v-if="item.media_type === 'image'" :src="item.file_url" :alt="house.title" />
          <div v-else class="gallery-video">视频</div>
        </div>
      </div>

      <div class="detail-grid">
        <article class="stack-section">
          <section class="page-card page-card--flat detail-card">
            <span class="eyebrow">房源编号 {{ String(house.id).padStart(3, "0") }}</span>
            <h1 class="page-title">{{ house.title }}</h1>
            <p class="house-address">{{ fullAddress }}</p>

            <p class="price price--large">¥{{ house.rent }}<span class="editorial-label"> / 月</span></p>

            <div class="detail-badges">
              <span class="tag">{{ house.layout || "户型待补充" }}</span>
              <span class="tag tag--light">{{ house.area }} 平方米</span>
              <span class="tag tag--light">{{ formatHouseStatus(house.status) }}</span>
            </div>

            <div class="detail-list">
              <div class="detail-row">
                <span>押金</span>
                <strong>¥{{ house.deposit || 0 }}</strong>
              </div>
              <div class="detail-row">
                <span>装修</span>
                <strong>{{ house.decoration || "未提供" }}</strong>
              </div>
              <div class="detail-row">
                <span>朝向</span>
                <strong>{{ house.orientation || "未提供" }}</strong>
              </div>
              <div class="detail-row">
                <span>楼层</span>
                <strong>{{ formatFloor(house.floor, house.total_floors) }}</strong>
              </div>
              <div class="detail-row">
                <span>房东</span>
                <strong>{{ house.landlord?.real_name || house.landlord?.username || "个人房东" }}</strong>
              </div>
              <div class="detail-row">
                <span>类型</span>
                <strong>{{ house.house_type || "住宅" }}</strong>
              </div>
            </div>

            <div>
              <span class="eyebrow">房源描述</span>
              <p class="page-text detail-description">
                {{ house.description || "该房源暂未补充更多描述。" }}
              </p>
            </div>

            <div class="detail-actions">
              <RouterLink class="secondary-button" to="/houses">返回列表</RouterLink>
              <RouterLink v-if="!authStore.isAuthenticated" class="primary-button" to="/login">
                登录后预约
              </RouterLink>
            </div>
          </section>
        </article>

        <aside class="stack-section">
          <div class="page-card booking-panel">
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

          <div class="page-card booking-panel">
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
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import { createBooking } from "../../api/booking";
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

const primaryMedia = computed(() => house.value?.media_items?.[0] || null);
const gallery = computed(() => house.value?.media_items?.slice(1) || []);
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

function formatHouseStatus(status) {
  return {
    draft: "草稿",
    available: "可租",
    rented: "已出租",
    repairing: "维修中",
    offline: "已下架",
  }[status] || status;
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
