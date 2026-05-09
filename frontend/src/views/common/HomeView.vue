<template>
  <section class="page-shell page-shell--wide">
    <div class="page-shell">
      <div class="hero-card">
        <div>
          <span class="eyebrow">现代租住服务</span>
          <h1 class="hero-title">安静找房<br />从容入住</h1>
          <p class="hero-text">
            用更克制、更清晰的方式完成找房、预约、签约、付款和沟通。
          </p>
        </div>

        <form class="editorial-search" @submit.prevent="goExplore">
          <input
            v-model.trim="keyword"
            type="text"
            placeholder="输入城市、小区或地址"
          />
          <button class="primary-button" type="submit">搜索</button>
        </form>
      </div>
    </div>

    <div class="feature-split">
      <article class="feature-main">
        <div class="feature-image">
          <img
            src="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=2670&auto=format&fit=crop"
            alt="精选住宅室内空间"
          />
        </div>
        <h2 class="page-title page-title--section">空间、流程与信任</h2>
        <p class="page-text">
          房源不只是一组价格和面积。平台把真实房源、预约流程、合同和账单放在一个连续的体验里，让租住决策更安静、更确定。
        </p>
      </article>

      <aside class="feature-side">
        <div class="dispatch-list">
          <article>
            <span class="editorial-label">真实</span>
            <h3 class="house-title house-title--small">真实房源</h3>
            <p class="page-text">房源发布、状态管理和公开浏览统一接入后端数据。</p>
          </article>
          <article>
            <span class="editorial-label">流程</span>
            <h3 class="house-title house-title--small">流程闭环</h3>
            <p class="page-text">从预约到合同、付款、消息，租客和房东各自拥有控制台。</p>
          </article>
          <div class="dark-panel">
            <span class="editorial-label">精选房源</span>
            <h3 class="house-title house-title--small">开始浏览</h3>
            <p class="page-text">浏览公开房源，找到适合自己的下一处居所。</p>
            <RouterLink class="primary-button" to="/houses">查看房源</RouterLink>
          </div>
        </div>
      </aside>
    </div>

    <div class="page-shell">
      <div class="section-head">
        <div>
          <span class="eyebrow">平台能力</span>
          <h2 class="page-title page-title--section">把租房流程收拢到一处</h2>
        </div>
        <RouterLink class="text-link" to="/register">创建账号</RouterLink>
      </div>

      <div class="house-grid" style="margin-top: 40px">
        <article class="house-card">
          <div class="house-content">
            <span class="tag">认证</span>
            <h3 class="house-title">统一认证</h3>
            <p class="page-text">租客、房东和管理员按角色进入各自工作台。</p>
          </div>
        </article>
        <article class="house-card">
          <div class="house-content">
            <span class="tag tag--light">管理</span>
            <h3 class="house-title">房源管理</h3>
            <p class="page-text">房东可以创建、编辑、上架、下架和删除房源。</p>
          </div>
        </article>
        <article class="house-card">
          <div class="house-content">
            <span class="tag">沟通</span>
            <h3 class="house-title">在线沟通</h3>
            <p class="page-text">租客可在详情页联系房东，并在控制台继续对话。</p>
          </div>
        </article>
      </div>
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
