<template>
  <section class="page-shell">
    <div class="auth-layout">
      <div class="auth-hero">
        <div class="auth-image">
          <img
            src="https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=2670&auto=format&fit=crop"
            alt="安静的住宅空间"
          />
        </div>
        <div class="auth-hero__content">
          <span class="eyebrow">账户登录</span>
          <h1 class="page-title">欢迎回来</h1>
          <p class="page-text">登录后继续处理房源、预约、合同、账单和消息。</p>
        </div>
      </div>

      <div class="page-card form-card">
        <div>
          <span class="eyebrow">继续使用</span>
          <h2 class="page-title page-title--section">账户登录</h2>
          <p class="page-text">支持用户名、邮箱或手机号登录。</p>
        </div>

        <form class="form-stack" @submit.prevent="handleSubmit">
          <label class="field">
            <span>账号</span>
            <input v-model.trim="form.username" type="text" placeholder="用户名 / 邮箱 / 手机号" />
          </label>

          <label class="field">
            <span>密码</span>
            <input v-model="form.password" type="password" placeholder="请输入密码" />
          </label>

          <p v-if="errorMessage" class="form-message form-message--error">{{ errorMessage }}</p>
          <p v-if="successMessage" class="form-message form-message--success">{{ successMessage }}</p>

          <button class="primary-button" type="submit" :disabled="submitting">
            {{ submitting ? "登录中..." : "登录" }}
          </button>
        </form>

        <p class="form-footer">
          还没有账号？
          <RouterLink to="/register">立即注册</RouterLink>
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../../stores/auth";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const submitting = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

async function handleSubmit() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!form.username || !form.password) {
    errorMessage.value = "请输入账号和密码。";
    return;
  }

  submitting.value = true;
  try {
    await authStore.login(form);
    successMessage.value = "登录成功，正在跳转。";
    const redirect = route.query.redirect;
    const fallbackRoute = authStore.dashboardRoute || "/";
    const target = typeof redirect === "string" ? redirect : fallbackRoute;
    setTimeout(() => {
      router.push(target);
    }, 300);
  } catch (error) {
    errorMessage.value = error.message || "登录失败，请稍后重试。";
  } finally {
    submitting.value = false;
  }
}
</script>
