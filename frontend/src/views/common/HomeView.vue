<template>
  <section class="page-shell page-shell--wide home-page">
    <div class="home-hero-wrap">
      <div class="hero-card home-hero">
        <div class="home-hero__content">
          <span class="eyebrow">智慧租房</span>
          <h1 class="hero-title">清晰找房<br />安心入住</h1>
          <p class="hero-text">
            为您提供一站式服务
          </p>

          <form class="editorial-search home-hero__search" @submit.prevent="goExplore">
            <input
              v-model.trim="keyword"
              type="text"
              placeholder="输入城市、小区或地址"
            />
            <button class="primary-button" type="submit">搜索房源</button>
          </form>

          <div class="home-hero__metrics" aria-label="常用功能">
            <span><strong>房源</strong> 按条件筛选</span>
            <span><strong>预约</strong> 提交看房时间</span>
            <span><strong>账单</strong> 查看付款状态</span>
          </div>
        </div>
      </div>
    </div>

    <div class="page-shell home-section">
      <div class="section-head home-section__head">
        <div>
          <h2 class="page-title page-title--section">常用入口</h2>
        </div>
        <RouterLink class="secondary-button" to="/houses">查看房源</RouterLink>
      </div>

      <div class="home-action-grid">
        <RouterLink class="home-action-card" to="/houses">
          <span class="tag">找房</span>
          <h3 class="house-title house-title--small">浏览房源</h3>
          <p class="page-text">按城市、区域、户型和租金筛选。</p>
        </RouterLink>
        <RouterLink class="home-action-card" to="/register">
          <span class="tag tag--light">账户</span>
          <h3 class="house-title house-title--small">选择身份</h3>
          <p class="page-text">租客看房，房东发布房源。</p>
        </RouterLink>
        <RouterLink class="home-action-card" to="/news">
          <span class="tag">公告</span>
          <h3 class="house-title house-title--small">查看通知</h3>
          <p class="page-text">了解房源维护和平台服务信息。</p>
        </RouterLink>
      </div>
    </div>

    <div class="feature-split home-feature">
      <article class="feature-main">
        <div class="feature-image">
          <img
            src="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=2670&auto=format&fit=crop"
            alt="精选住宅室内空间"
          />
        </div>
        <h2 class="page-title page-title--section">信息清楚，操作便捷</h2>
        <p class="page-text">
          每套房源展示价格、户型、面积、位置和状态。登录后可以预约看房、联系房东，并查看合同和账单。
        </p>
      </article>

      <aside class="feature-side">
        <div class="dispatch-list">
          <article>
            <span class="editorial-label">房源</span>
            <h3 class="house-title house-title--small">公开展示</h3>
            <p class="page-text">房东发布后，租客可按条件查找。</p>
          </article>
          <article>
            <span class="editorial-label">看房</span>
            <h3 class="house-title house-title--small">预约沟通</h3>
            <p class="page-text">租客提交时间，房东在控制台处理。</p>
          </article>
          <div class="dark-panel">
            <span class="editorial-label">房源大厅</span>
            <h3 class="house-title house-title--small">开始浏览</h3>
            <p class="page-text">直接查看当前可浏览的房源。</p>
            <RouterLink class="primary-button" to="/houses">查看房源</RouterLink>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const keyword = ref("");
const router = useRouter();

function goExplore() {
  router.push({
    path: "/houses",
    query: keyword.value ? { keyword: keyword.value } : {},
  });
}
</script>
