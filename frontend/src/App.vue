<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar__inner">
        <RouterLink class="brand" to="/">
          <span class="brand__mark">租</span>
          <span>
            <span class="brand__name">智慧租房</span>
          </span>
        </RouterLink>

        <nav class="topbar__nav">
          <RouterLink class="nav-link" to="/houses">房源</RouterLink>
          <RouterLink class="nav-link" to="/news">公告</RouterLink>
          <RouterLink v-if="!authStore.isAuthenticated" class="nav-link" to="/login">
            登录
          </RouterLink>
          <RouterLink
            v-if="!authStore.isAuthenticated"
            class="nav-link nav-link--strong"
            to="/register"
          >
            注册
          </RouterLink>
          <RouterLink
            v-if="authStore.dashboardRoute"
            class="nav-link"
            :to="authStore.dashboardRoute"
          >
            控制台
          </RouterLink>
          <button
            v-if="authStore.isAuthenticated"
            class="nav-button"
            type="button"
            @click="handleLogout"
          >
            退出
          </button>
        </nav>
      </div>
    </header>

    <main>
      <RouterView />
    </main>

    <footer class="site-footer">
      <div class="site-footer__inner">
        <div>
          <span class="brand__name">智慧租房</span>
        </div>
        <nav class="topbar__nav">
          <RouterLink class="nav-link" to="/houses">房源</RouterLink>
          <RouterLink class="nav-link" to="/news">公告</RouterLink>
          <RouterLink class="nav-link" to="/login">账户</RouterLink>
        </nav>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "./stores/auth";

const authStore = useAuthStore();
const router = useRouter();

onMounted(() => {
  authStore.initialize();
});

async function handleLogout() {
  await authStore.logout();
  router.push("/login");
}
</script>
