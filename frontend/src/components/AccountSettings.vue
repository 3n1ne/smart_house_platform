<template>
  <div class="page-card workspace-panel">
    <div class="section-head section-head--compact">
      <div>
        <span class="eyebrow">账号设置</span>
        <h2 class="page-title page-title--section">个人资料</h2>
      </div>
      <button class="ghost-button" type="button" :disabled="loading" @click="loadProfile">
        {{ loading ? "刷新中..." : "刷新" }}
      </button>
    </div>

    <form class="filter-grid filter-grid--form" @submit.prevent="handleSubmit">
      <label class="field">
        <span>用户名</span>
        <input :value="profile?.username || ''" type="text" disabled />
      </label>
      <label class="field">
        <span>角色</span>
        <input :value="formatRole(profile?.role)" type="text" disabled />
      </label>
      <label class="field">
        <span>姓名</span>
        <input v-model.trim="form.real_name" type="text" placeholder="请输入姓名" />
      </label>
      <label class="field">
        <span>手机号</span>
        <input v-model.trim="form.phone" type="text" placeholder="请输入手机号" />
      </label>
      <label class="field">
        <span>邮箱</span>
        <input v-model.trim="form.email" type="email" placeholder="请输入邮箱" />
      </label>
      <label class="field">
        <span>身份证号</span>
        <input v-model.trim="form.identity_no" type="text" :placeholder="identityPlaceholder" />
      </label>

      <label class="checkbox-field field--full">
        <input v-model="form.is_mfa_enabled" type="checkbox" />
        <span>启用动态验证码登录</span>
      </label>

      <div class="filter-actions filter-actions--full">
        <button class="primary-button" type="submit" :disabled="saving">
          {{ saving ? "保存中..." : "保存设置" }}
        </button>
      </div>
    </form>

    <p v-if="successMessage" class="form-message form-message--success">{{ successMessage }}</p>
    <p v-if="errorMessage" class="form-message form-message--error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { fetchProfile, updateProfile } from "../api/user";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const profile = ref(null);
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const form = reactive({
  real_name: "",
  email: "",
  phone: "",
  identity_no: "",
  is_mfa_enabled: false,
});

const identityPlaceholder = computed(() => {
  return profile.value?.identity_no_masked ? `已保存：${profile.value.identity_no_masked}` : "可选，提交后仅脱敏展示";
});

function fillForm(user) {
  profile.value = user;
  form.real_name = user?.real_name || "";
  form.email = user?.email || "";
  form.phone = user?.phone || "";
  form.identity_no = "";
  form.is_mfa_enabled = Boolean(user?.is_mfa_enabled);
}

function formatRole(role) {
  return {
    tenant: "租客",
    landlord: "房东",
    admin: "管理员",
  }[role] || role || "未知角色";
}

async function loadProfile() {
  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  try {
    const response = await fetchProfile();
    fillForm(response.data.data);
  } catch (error) {
    errorMessage.value = error.message || "加载个人资料失败。";
  } finally {
    loading.value = false;
  }
}

async function handleSubmit() {
  saving.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  try {
    const payload = {
      real_name: form.real_name,
      email: form.email,
      phone: form.phone,
      is_mfa_enabled: form.is_mfa_enabled,
    };
    if (form.identity_no) {
      payload.identity_no = form.identity_no;
    }

    const response = await updateProfile(payload);
    const updatedUser = response.data.data;
    fillForm(updatedUser);
    authStore.setUser(updatedUser);
    successMessage.value = "账号设置已保存。";
  } catch (error) {
    errorMessage.value = error.message || "保存账号设置失败。";
  } finally {
    saving.value = false;
  }
}

onMounted(loadProfile);
</script>
