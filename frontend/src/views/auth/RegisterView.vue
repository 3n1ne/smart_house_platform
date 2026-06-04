<template>
  <section class="page-shell">
    <div class="auth-layout">
      <div class="auth-hero">
        <div class="auth-image">
          <img
            src="https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=2670&auto=format&fit=crop"
            alt="现代住宅客厅"
          />
        </div>
        <div class="auth-hero__content">
          <span class="eyebrow">创建账号</span>
          <h1 class="page-title">创建账号</h1>
          <p class="page-text">租客看房，房东发布和管理房源。</p>
        </div>
      </div>

      <div class="page-card form-card">
        <div>
          <span class="eyebrow">基础信息</span>
          <h2 class="page-title page-title--section">注册账号</h2>
          <p class="page-text">请先选择角色，再填写基础信息。</p>
        </div>

        <form class="form-stack" @submit.prevent="handleSubmit">
          <label class="field">
            <span>角色</span>
            <select v-model="form.role">
              <option value="tenant">租客</option>
              <option value="landlord">房东</option>
            </select>
          </label>

          <label class="field">
            <span>用户名</span>
            <input v-model.trim="form.username" type="text" placeholder="请输入用户名" />
          </label>

          <label class="field">
            <span>真实姓名</span>
            <input v-model.trim="form.real_name" type="text" placeholder="请输入姓名" />
          </label>

          <label class="field">
            <span>邮箱</span>
            <input v-model.trim="form.email" type="email" placeholder="请输入邮箱" />
          </label>

          <label class="field">
            <span>手机号</span>
            <input v-model.trim="form.phone" type="text" placeholder="请输入手机号" />
          </label>

          <label class="field">
            <span>身份证号</span>
            <input v-model.trim="form.identity_no" type="text" placeholder="可选，提交后仅脱敏展示" />
          </label>

          <label class="field">
            <span>密码</span>
            <input v-model="form.password" type="password" placeholder="请输入密码" />
          </label>

          <label class="checkbox-field">
            <input v-model="form.enable_mfa" type="checkbox" />
            <span>启用双因素动态验证码登录</span>
          </label>

          <p v-if="errorMessage" class="form-message form-message--error">{{ errorMessage }}</p>
          <p v-if="successMessage" class="form-message form-message--success">{{ successMessage }}</p>

          <button class="primary-button" type="submit" :disabled="submitting">
            {{ submitting ? "注册中..." : "注册" }}
          </button>
        </form>

        <p class="form-footer">
          已有账号？
          <RouterLink to="/login">去登录</RouterLink>
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { register } from "../../api/auth";

const router = useRouter();

const form = reactive({
  role: "tenant",
  username: "",
  real_name: "",
  email: "",
  phone: "",
  identity_no: "",
  password: "",
  enable_mfa: false,
});

const submitting = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

function formatDuplicateRegistrationError(error) {
  const fieldLabels = {
    username: "用户名",
    email: "邮箱",
    phone: "手机号",
  };
  const duplicateFields = error.errors?.fields || [];
  const duplicateLabels = duplicateFields.map((field) => fieldLabels[field]).filter(Boolean);

  if (duplicateLabels.length) {
    return `${duplicateLabels.join("、")}已被注册，请更换后再试。`;
  }
  return "用户名、邮箱或手机号已被注册，请更换后再试。";
}

async function handleSubmit() {
  errorMessage.value = "";
  successMessage.value = "";

  if (!form.username || !form.password) {
    errorMessage.value = "用户名和密码不能为空。";
    return;
  }

  submitting.value = true;
  try {
    await register(form);
    successMessage.value = "注册成功，即将跳转到登录页。";
    setTimeout(() => {
      router.push("/login");
    }, 500);
  } catch (error) {
    if (error.code === 4009) {
      errorMessage.value = formatDuplicateRegistrationError(error);
    } else {
      errorMessage.value = error.message || "注册失败，请稍后重试。";
    }
  } finally {
    submitting.value = false;
  }
}
</script>
