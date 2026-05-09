<template>
  <div class="page-card">
    <div class="section-head section-head--compact">
      <div>
        <span class="eyebrow">公告管理</span>
        <h2 class="page-title page-title--section">{{ editingId ? "编辑公告" : "发布公告" }}</h2>
      </div>
      <button v-if="editingId" class="ghost-button" type="button" @click="resetForm">取消编辑</button>
    </div>

    <form class="filter-grid filter-grid--form" @submit.prevent="handleSubmit">
      <label class="field field--full">
        <span>标题</span>
        <input v-model.trim="form.title" type="text" placeholder="例如：五一假期维修服务安排" />
      </label>
      <label class="field">
        <span>状态</span>
        <select v-model="form.status" :disabled="Boolean(editingId)">
          <option value="draft">草稿</option>
          <option value="published">发布</option>
        </select>
      </label>
      <label class="field field--full">
        <span>内容</span>
        <textarea v-model.trim="form.content" rows="4" placeholder="填写面向租客的公告内容" />
      </label>
      <div class="filter-actions filter-actions--full">
        <button class="primary-button" type="submit" :disabled="loading.submit">
          {{ loading.submit ? "保存中..." : editingId ? "保存修改" : "创建公告" }}
        </button>
        <button class="ghost-button" type="button" @click="resetForm">清空</button>
      </div>
    </form>

    <p v-if="messages.form" class="form-message form-message--success">{{ messages.form }}</p>
    <p v-if="errors.form" class="form-message form-message--error">{{ errors.form }}</p>

    <form class="filter-grid filter-grid--manage" @submit.prevent="loadNews">
      <label class="field">
        <span>状态</span>
        <select v-model="filters.status">
          <option value="">全部状态</option>
          <option value="draft">草稿</option>
          <option value="published">已发布</option>
          <option value="archived">已归档</option>
        </select>
      </label>
      <label class="field">
        <span>关键词</span>
        <input v-model.trim="filters.keyword" type="text" placeholder="搜索标题或内容" />
      </label>
      <div class="filter-actions filter-actions--full">
        <button class="secondary-button" type="submit" :disabled="loading.list">
          {{ loading.list ? "加载中..." : "筛选公告" }}
        </button>
        <button class="ghost-button" type="button" @click="resetFilters">重置</button>
      </div>
    </form>

    <p v-if="errors.list" class="form-message form-message--error">{{ errors.list }}</p>

    <div v-if="newsItems.length" class="manage-list">
      <article v-for="item in newsItems" :key="item.id" class="manage-item">
        <div class="manage-item__main">
          <div class="house-meta">
            <span class="tag">{{ formatNewsStatus(item.status) }}</span>
            <span class="tag tag--light">{{ formatDateTime(item.published_at || item.created_at) }}</span>
          </div>
          <h3 class="house-title house-title--small">{{ item.title }}</h3>
          <div class="booking-meta">
            <span>作者：{{ item.author?.real_name || item.author?.username || "平台" }}</span>
          </div>
          <p class="page-text news-content">{{ item.content }}</p>
        </div>

        <div class="manage-item__actions">
          <button class="ghost-button" type="button" @click="startEdit(item)">编辑</button>
          <button v-if="item.status !== 'published'" class="secondary-button" type="button" @click="changeStatus(item.id, 'published')">发布</button>
          <button v-if="item.status === 'published'" class="ghost-button" type="button" @click="changeStatus(item.id, 'archived')">归档</button>
          <button v-if="item.status !== 'draft'" class="ghost-button" type="button" @click="changeStatus(item.id, 'draft')">转草稿</button>
          <button class="danger-button" type="button" @click="removeNews(item.id)">删除</button>
        </div>
      </article>
    </div>

    <div v-else-if="!loading.list" class="empty-card empty-card--soft">
      <h3 class="page-title page-title--section">暂无公告</h3>
      <p class="page-text">创建后的公告会显示在这里。</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import {
  createNews,
  deleteNews,
  fetchMyNews,
  updateNews,
  updateNewsStatus,
} from "../api/news";

const defaultForm = () => ({
  title: "",
  content: "",
  status: "draft",
});

const form = reactive(defaultForm());
const filters = reactive({ status: "", keyword: "" });
const newsItems = ref([]);
const editingId = ref(null);
const loading = reactive({ list: false, submit: false });
const errors = reactive({ list: "", form: "" });
const messages = reactive({ form: "" });

function formatNewsStatus(status) {
  return {
    draft: "草稿",
    published: "已发布",
    archived: "已归档",
  }[status] || status;
}

function formatDateTime(value) {
  return value ? new Date(value).toLocaleString() : "暂无";
}

function resetForm() {
  Object.assign(form, defaultForm());
  editingId.value = null;
  errors.form = "";
  messages.form = "";
}

function resetFilters() {
  filters.status = "";
  filters.keyword = "";
  loadNews();
}

function startEdit(item) {
  editingId.value = item.id;
  form.title = item.title || "";
  form.content = item.content || "";
  form.status = item.status || "draft";
  errors.form = "";
  messages.form = "";
}

async function loadNews() {
  loading.list = true;
  errors.list = "";
  try {
    const response = await fetchMyNews(filters);
    newsItems.value = response.data.data.items;
  } catch (error) {
    errors.list = error.message || "加载公告失败。";
    newsItems.value = [];
  } finally {
    loading.list = false;
  }
}

async function handleSubmit() {
  errors.form = "";
  messages.form = "";
  if (!form.title || !form.content) {
    errors.form = "标题和内容不能为空。";
    return;
  }

  loading.submit = true;
  try {
    if (editingId.value) {
      await updateNews(editingId.value, {
        title: form.title,
        content: form.content,
      });
      messages.form = "公告已更新。";
    } else {
      await createNews({
        title: form.title,
        content: form.content,
        status: form.status,
      });
      messages.form = "公告已创建。";
    }
    resetForm();
    await loadNews();
  } catch (error) {
    errors.form = error.message || "保存公告失败。";
  } finally {
    loading.submit = false;
  }
}

async function changeStatus(newsId, status) {
  errors.list = "";
  try {
    await updateNewsStatus(newsId, { status });
    await loadNews();
  } catch (error) {
    errors.list = error.message || "更新公告状态失败。";
  }
}

async function removeNews(newsId) {
  errors.list = "";
  try {
    await deleteNews(newsId);
    if (editingId.value === newsId) {
      resetForm();
    }
    await loadNews();
  } catch (error) {
    errors.list = error.message || "删除公告失败。";
  }
}

onMounted(loadNews);
</script>
