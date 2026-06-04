<template>
  <section class="page-shell">
    <div class="stack-section">
      <header class="section-head">
        <div>
          <span class="eyebrow">房源大厅</span>
          <h1 class="page-title">精选房源</h1>
          <p class="page-text">按城市、区域、户型和租金筛选正在开放的房源。</p>
        </div>
        <RouterLink class="secondary-button" to="/">返回首页</RouterLink>
      </header>

      <form class="page-card filter-grid" @submit.prevent="loadHouses">
        <label class="field">
          <span>城市</span>
          <input v-model.trim="filters.city" type="text" placeholder="例如：杭州" />
        </label>

        <label class="field">
          <span>区域</span>
          <input v-model.trim="filters.district" type="text" placeholder="例如：西湖区" />
        </label>

        <label class="field">
          <span>户型</span>
          <input v-model.trim="filters.layout" type="text" placeholder="例如：两室一厅" />
        </label>

        <label class="field">
          <span>关键词</span>
          <input v-model.trim="filters.keyword" type="text" placeholder="标题 / 小区 / 地址" />
        </label>

        <label class="field">
          <span>最低租金</span>
          <input v-model.number="filters.min_rent" type="number" min="0" placeholder="3000" />
        </label>

        <label class="field">
          <span>最高租金</span>
          <input v-model.number="filters.max_rent" type="number" min="0" placeholder="8000" />
        </label>

        <div class="filter-actions filter-actions--full">
          <button class="primary-button" type="submit" :disabled="loading">
            {{ loading ? "加载中..." : "搜索房源" }}
          </button>
          <button class="ghost-button" type="button" @click="resetFilters">重置</button>
        </div>
      </form>

      <p v-if="errorMessage" class="form-message form-message--error">{{ errorMessage }}</p>

      <section class="page-card search-insights">
        <div class="section-head section-head--compact">
          <div>
            <span class="eyebrow">筛选建议</span>
            <h2 class="page-title page-title--section">按地区和户型快速查看</h2>
          </div>
          <button class="ghost-button" type="button" :disabled="insightsLoading" @click="loadInsights">
            {{ insightsLoading ? "刷新中..." : "刷新推荐" }}
          </button>
        </div>

        <p v-if="insightsError" class="form-message form-message--error">{{ insightsError }}</p>

        <div class="insight-grid">
          <div>
            <span class="editorial-label">地区</span>
            <div v-if="regions.length" class="insight-list">
              <button
                v-for="region in regions"
                :key="`${region.city}-${region.district}-${region.community || 'all'}`"
                class="insight-button"
                type="button"
                @click="applyRegion(region)"
              >
                <strong>{{ formatRegion(region) }}</strong>
                <span>{{ region.house_count }} 套 | ¥{{ region.min_rent }} - ¥{{ region.max_rent }}</span>
              </button>
            </div>
            <p v-else class="page-text">暂无地区数据。</p>
          </div>

          <div>
            <span class="editorial-label">户型</span>
            <div v-if="layouts.length" class="insight-list">
              <button
                v-for="layout in layouts"
                :key="layout.layout"
                class="insight-button"
                type="button"
                @click="applyLayout(layout.layout)"
              >
                <strong>{{ layout.layout }}</strong>
                <span>{{ layout.house_count }} 套 | ¥{{ layout.min_rent }} - ¥{{ layout.max_rent }}</span>
              </button>
            </div>
            <p v-else class="page-text">暂无户型数据。</p>
          </div>
        </div>

        <div v-if="recommendations.length" class="recommendation-strip">
          <span class="editorial-label">推荐房源</span>
          <div class="house-grid house-grid--compact">
            <RouterLink
              v-for="house in recommendations"
              :key="house.id"
              class="house-card"
              :to="`/houses/${house.id}`"
            >
              <div class="house-cover house-cover--compact">
                <img v-if="house.cover_url" :src="resolveAssetUrl(house.cover_url)" :alt="house.title" />
                <div v-else class="house-cover__placeholder">暂无图片</div>
              </div>
              <div class="house-content">
                <div class="house-meta">
                  <span class="tag">{{ house.layout || "户型待补充" }}</span>
                  <span class="tag tag--light">{{ house.city }} {{ house.district }}</span>
                </div>
                <h3 class="house-title house-title--small">{{ house.title }}</h3>
                <div class="house-footer">
                  <strong class="price price--compact">¥{{ house.rent }}/月</strong>
                  <span class="text-link">查看</span>
                </div>
              </div>
            </RouterLink>
          </div>
        </div>
      </section>

      <div v-if="houses.length" class="house-grid">
        <RouterLink
          v-for="(house, index) in houses"
          :key="house.id"
          class="house-card"
          :to="`/houses/${house.id}`"
        >
          <div class="house-cover">
            <img v-if="house.cover_url" :src="resolveAssetUrl(house.cover_url)" :alt="house.title" />
            <div v-else class="house-cover__placeholder">暂无图片</div>
            <span v-if="index === 0" class="tag" style="position: absolute; top: 0; left: 0">
              新上架
            </span>
          </div>
          <div class="house-content">
            <div class="house-meta">
              <span class="tag">{{ house.layout || "户型待补充" }}</span>
              <span class="tag tag--light">{{ house.city }} {{ house.district }}</span>
            </div>
            <h2 class="house-title">{{ house.title }}</h2>
            <p class="house-address">{{ house.community || house.address_detail }}</p>
            <div class="house-info-row">
              <span>{{ house.area }} 平方米</span>
              <span>{{ house.orientation || "朝向待补充" }}</span>
            </div>
            <div class="house-footer">
              <strong class="price">¥{{ house.rent }}/月</strong>
              <span class="text-link">查看详情</span>
            </div>
          </div>
        </RouterLink>
      </div>

      <div v-else-if="!loading" class="page-card empty-card">
        <h2 class="page-title page-title--section">暂无匹配房源</h2>
        <p class="page-text">减少筛选条件，或稍后再试。</p>
      </div>

      <div class="pagination-bar">
        <button class="ghost-button" type="button" :disabled="page <= 1 || loading" @click="changePage(page - 1)">
          上一页
        </button>
        <span class="editorial-label">第 {{ page }} / {{ totalPages }} 页</span>
        <button
          class="ghost-button"
          type="button"
          :disabled="page >= totalPages || loading"
          @click="changePage(page + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import { fetchHouseList } from "../../api/house";
import { resolveAssetUrl } from "../../api/assets";
import {
  fetchSearchLayouts,
  fetchSearchRecommendations,
  fetchSearchRegions,
} from "../../api/search";

const route = useRoute();
const filters = reactive({
  city: "",
  district: "",
  layout: "",
  keyword: "",
  min_rent: "",
  max_rent: "",
});

const loading = ref(false);
const errorMessage = ref("");
const insightsError = ref("");
const houses = ref([]);
const regions = ref([]);
const layouts = ref([]);
const recommendations = ref([]);
const page = ref(1);
const pageSize = ref(6);
const total = ref(0);
const insightsLoading = ref(false);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

function buildParams() {
  return {
    ...filters,
    page: page.value,
    page_size: pageSize.value,
  };
}

function buildInsightParams() {
  return Object.fromEntries(
    Object.entries({
      city: filters.city,
      district: filters.district,
      layout: filters.layout,
      keyword: filters.keyword,
    }).filter(([, value]) => value !== "" && value !== null && value !== undefined)
  );
}

async function loadHouses() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await fetchHouseList(buildParams());
    const payload = response.data.data;
    houses.value = payload.items;
    total.value = payload.pagination.total;
  } catch (error) {
    errorMessage.value = error.message || "房源加载失败。";
    houses.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
  loadInsights();
}

async function loadInsights() {
  insightsLoading.value = true;
  insightsError.value = "";
  try {
    const params = buildInsightParams();
    const [regionResponse, layoutResponse, recommendationResponse] = await Promise.all([
      fetchSearchRegions(params),
      fetchSearchLayouts(params),
      fetchSearchRecommendations({ city: filters.city || undefined, limit: 3 }),
    ]);
    regions.value = regionResponse.data.data.slice(0, 6);
    layouts.value = layoutResponse.data.data.slice(0, 6);
    recommendations.value = recommendationResponse.data.data;
  } catch (error) {
    insightsError.value = error.message || "智能搜索数据加载失败。";
    regions.value = [];
    layouts.value = [];
    recommendations.value = [];
  } finally {
    insightsLoading.value = false;
  }
}

function resetFilters() {
  filters.city = "";
  filters.district = "";
  filters.layout = "";
  filters.keyword = "";
  filters.min_rent = "";
  filters.max_rent = "";
  page.value = 1;
  loadHouses();
}

function changePage(nextPage) {
  page.value = nextPage;
  loadHouses();
}

function applyRegion(region) {
  filters.city = region.city || "";
  filters.district = region.district || "";
  filters.keyword = region.community || "";
  page.value = 1;
  loadHouses();
}

function applyLayout(layout) {
  filters.layout = layout || "";
  page.value = 1;
  loadHouses();
}

function formatRegion(region) {
  return [region.city, region.district, region.community].filter(Boolean).join(" / ");
}

onMounted(() => {
  if (typeof route.query.keyword === "string") {
    filters.keyword = route.query.keyword;
  }
  if (typeof route.query.city === "string") {
    filters.city = route.query.city;
  }
  if (typeof route.query.district === "string") {
    filters.district = route.query.district;
  }
  if (typeof route.query.layout === "string") {
    filters.layout = route.query.layout;
  }
  loadHouses();
});
</script>
