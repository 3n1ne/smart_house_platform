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

      <div v-if="houses.length" class="house-grid">
        <RouterLink
          v-for="(house, index) in houses"
          :key="house.id"
          class="house-card"
          :to="`/houses/${house.id}`"
        >
          <div class="house-cover">
            <img v-if="house.cover_url" :src="house.cover_url" :alt="house.title" />
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
const houses = ref([]);
const page = ref(1);
const pageSize = ref(6);
const total = ref(0);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

function buildParams() {
  return {
    ...filters,
    page: page.value,
    page_size: pageSize.value,
  };
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

onMounted(() => {
  if (typeof route.query.keyword === "string") {
    filters.keyword = route.query.keyword;
  }
  loadHouses();
});
</script>
