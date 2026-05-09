<template>
  <section class="page-shell">
    <div class="stack-section">
      <div class="hero-card dashboard-hero">
        <div>
          <span class="eyebrow">平台公告</span>
          <h1 class="hero-title">租住资讯</h1>
          <p class="hero-text">查看房源维护、租赁服务和平台运营相关公告。</p>
        </div>
        <RouterLink class="secondary-button" to="/houses">浏览房源</RouterLink>
      </div>

      <div class="page-card">
        <form class="filter-grid filter-grid--manage" @submit.prevent="loadNews">
          <label class="field">
            <span>关键词</span>
            <input v-model.trim="filters.keyword" type="text" placeholder="搜索标题或内容" />
          </label>
          <div class="filter-actions filter-actions--full">
            <button class="secondary-button" type="submit" :disabled="loading">
              {{ loading ? "加载中..." : "搜索公告" }}
            </button>
            <button class="ghost-button" type="button" @click="resetFilters">重置</button>
          </div>
        </form>

        <p v-if="errorMessage" class="form-message form-message--error">{{ errorMessage }}</p>

        <div v-if="newsItems.length" class="manage-list">
          <article v-for="item in newsItems" :key="item.id" class="manage-item">
            <div class="manage-item__main">
              <div class="house-meta">
                <span class="tag">已发布</span>
                <span class="tag tag--light">{{ formatDateTime(item.published_at || item.created_at) }}</span>
              </div>
              <h2 class="house-title house-title--small">{{ item.title }}</h2>
              <div class="booking-meta">
                <span>发布人：{{ item.author?.real_name || item.author?.username || "平台" }}</span>
              </div>
              <p class="page-text news-content">{{ item.content }}</p>
            </div>
          </article>
        </div>

        <div v-else-if="!loading" class="empty-card empty-card--soft">
          <h2 class="page-title page-title--section">暂无公告</h2>
          <p class="page-text">当前没有已发布的公告。</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import { fetchPublishedNews } from "../../api/news";

const filters = reactive({ keyword: "" });
const newsItems = ref([]);
const loading = ref(false);
const errorMessage = ref("");

function formatDateTime(value) {
  return value ? new Date(value).toLocaleString() : "暂无";
}

async function loadNews() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await fetchPublishedNews(filters);
    newsItems.value = response.data.data.items;
  } catch (error) {
    errorMessage.value = error.message || "加载公告失败。";
    newsItems.value = [];
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.keyword = "";
  loadNews();
}

onMounted(loadNews);
</script>
