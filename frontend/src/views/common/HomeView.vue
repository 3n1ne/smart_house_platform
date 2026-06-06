<template>
  <section class="apt-home">
    <section class="apt-hero">
      <div class="apt-hero__shade">
        <h1>寻找你的下一处住所</h1>

        <form class="apt-search-box" @submit.prevent="goExplore">
          <input v-model.trim="keyword" type="text" placeholder="输入城市、小区、学校或地址" />
          <button type="submit">搜索</button>
        </form>

        <div class="apt-home-tabs">
          <button
            v-for="item in quickSearches"
            :key="item.label"
            type="button"
            @click="quickSearch(item.query)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="apt-section">
      <div class="apt-section__head">
        <h2>从这些方式开始找房</h2>
        <RouterLink to="/houses">查看全部房源</RouterLink>
      </div>

      <div class="apt-entry-grid">
        <RouterLink v-for="entry in entries" :key="entry.title" class="apt-entry-card" :to="entry.to">
          <strong>{{ entry.title }}</strong>
          <span>{{ entry.text }}</span>
        </RouterLink>
      </div>
    </section>

    <section class="apt-featured-section">
      <h2>{{ featuredTitle }}</h2>

      <p v-if="featuredError" class="apt-featured-section__error">{{ featuredError }}</p>

      <div v-if="featuredHouses.length" class="apt-featured-grid">
        <RouterLink
          v-for="(house, index) in featuredHouses"
          :key="house.id"
          class="apt-featured-card"
          :to="`/houses/${house.id}`"
        >
          <img :src="getHouseImage(house, index)" :alt="house.title" />
          <div class="apt-featured-card__body">
            <h3>{{ house.title }}</h3>
            <p>{{ formatAddress(house) }}</p>
            <strong>{{ formatMoney(house.rent) }}</strong>
            <span>{{ house.layout || "户型待补充" }} · {{ formatArea(house.area) }}</span>
          </div>
        </RouterLink>
      </div>

      <div v-else-if="featuredLoading" class="apt-featured-grid apt-featured-grid--loading">
        <div v-for="index in 4" :key="index" class="apt-featured-card apt-featured-card--skeleton">
          <div />
          <section />
        </div>
      </div>

      <RouterLink class="apt-view-more" to="/houses">View More</RouterLink>
    </section>

    <section class="apt-simple-band">
      <article>
        <strong>更多房源</strong>
        <span>集中展示价格、户型、面积和位置。</span>
      </article>
      <article>
        <strong>筛选更快</strong>
        <span>预算、户型、区域都放在列表页顶部。</span>
      </article>
      <article>
        <strong>直接沟通</strong>
        <span>进入详情后预约看房或联系房东。</span>
      </article>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { resolveAssetUrl } from "../../api/assets";
import { fetchHouseList } from "../../api/house";

const keyword = ref("");
const router = useRouter();
const featuredHouses = ref([]);
const featuredLoading = ref(false);
const featuredError = ref("");

const fallbackImages = [
  "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?q=80&w=1200&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1600607688969-a5bfcd646154?q=80&w=1200&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=1200&auto=format&fit=crop",
  "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=1200&auto=format&fit=crop",
];

const quickSearches = [
  { label: "公寓", query: { keyword: "公寓" } },
  { label: "整租", query: { keyword: "整租" } },
  { label: "¥5000 以下", query: { max_rent: "5000" } },
  { label: "两室一厅", query: { layout: "2室1厅" } },
];

const entries = [
  { title: "按城市找", text: "输入城市或区域进入搜索结果。", to: "/houses" },
  { title: "按预算找", text: "先筛掉不合适的租金范围。", to: "/houses?max_rent=5000" },
  { title: "按户型找", text: "快速查看一居、两居或三居。", to: "/houses?layout=2室1厅" },
  { title: "发布房源", text: "房东注册后进入控制台管理。", to: "/register" },
];

const featuredTitle = "精选租房推荐";

function goExplore() {
  router.push({
    path: "/houses",
    query: keyword.value ? { keyword: keyword.value } : {},
  });
}

function quickSearch(query) {
  router.push({ path: "/houses", query });
}

function getHouseImage(house, index) {
  return house.cover_url ? resolveAssetUrl(house.cover_url) : fallbackImages[index % fallbackImages.length];
}

function formatAddress(house) {
  return [house.community, house.address_detail, house.district, house.city].filter(Boolean).join("，") || "地址待补充";
}

function formatArea(area) {
  return area ? `${Number(area).toLocaleString("zh-CN", { maximumFractionDigits: 0 })} 平方米` : "面积待补充";
}

function formatMoney(value) {
  return `¥${Number(value || 0).toLocaleString("zh-CN", { maximumFractionDigits: 0 })} / 月`;
}

async function loadFeaturedHouses() {
  featuredLoading.value = true;
  featuredError.value = "";
  try {
    const response = await fetchHouseList({ page: 1, page_size: 4 });
    featuredHouses.value = response.data.data.items;
  } catch (error) {
    featuredError.value = error.message || "精选房源加载失败。";
    featuredHouses.value = [];
  } finally {
    featuredLoading.value = false;
  }
}

onMounted(() => {
  loadFeaturedHouses();
});
</script>
