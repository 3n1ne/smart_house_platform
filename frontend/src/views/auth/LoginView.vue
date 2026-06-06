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
            <span>登录身份</span>
            <select v-model="form.role">
              <option v-for="role in roleOptions" :key="role.value" :value="role.value">
                {{ role.label }}
              </option>
            </select>
          </label>

          <label class="field">
            <span>账号</span>
            <input v-model.trim="form.username" type="text" placeholder="用户名 / 邮箱 / 手机号" />
          </label>

          <label class="field">
            <span>密码</span>
            <input v-model="form.password" type="password" placeholder="请输入密码" />
          </label>

          <label class="field">
            <span>动态验证码</span>
            <input v-model.trim="form.verification_code" type="text" inputmode="numeric" placeholder="开启双因素账号需填写" />
          </label>

          <button class="secondary-button" type="button" :disabled="codeSubmitting || !form.username" @click="handleRequestCode">
            {{ codeSubmitting ? "发送中..." : "获取动态验证码" }}
          </button>

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

import { requestVerificationCode } from "../../api/auth";
import { useAuthStore } from "../../stores/auth";

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const form = reactive({
  role: "tenant",
  username: "",
  password: "",
  verification_code: "",
});

const submitting = ref(false);
const codeSubmitting = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const roleOptions = [
  { value: "tenant", label: "租客" },
  { value: "landlord", label: "房东" },
  { value: "admin", label: "管理员" },
];
const roleLabels = Object.fromEntries(roleOptions.map((role) => [role.value, role.label]));

async function handleRequestCode() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!form.username) {
    errorMessage.value = "请先输入账号。";
    return;
  }

  codeSubmitting.value = true;
  try {
    const response = await requestVerificationCode({ username: form.username });
    const payload = response.data.data;
    if (payload.verification_code) {
      form.verification_code = payload.verification_code;
      successMessage.value = "动态验证码已生成并填入表单。";
    } else {
      successMessage.value = "动态验证码已发送，请在有效期内登录。";
    }
  } catch (error) {
    errorMessage.value = error.message || "动态验证码获取失败。";
  } finally {
    codeSubmitting.value = false;
  }
}

async function handleSubmit() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!form.username || !form.password) {
    errorMessage.value = "请输入账号和密码。";
    return;
  }

  submitting.value = true;
  try {
    const user = await authStore.login({
      username: form.username,
      password: form.password,
      verification_code: form.verification_code || undefined,
    });

    if (user.role !== form.role) {
      await authStore.logout();
      errorMessage.value = `当前账号是${roleLabels[user.role] || "未知身份"}，不是${roleLabels[form.role]}。请切换身份后再登录。`;
      return;
    }

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
