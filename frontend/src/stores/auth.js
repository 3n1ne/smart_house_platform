import { computed, ref } from "vue";
import { defineStore } from "pinia";

import { fetchCurrentUser, login as loginRequest, logout as logoutRequest } from "../api/auth";


export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("access_token") || "");
  const user = ref(null);
  const initialized = ref(false);

  const isAuthenticated = computed(() => Boolean(token.value && user.value));
  const dashboardRoute = computed(() => {
    if (!user.value?.role) {
      return "";
    }

    const routeMap = {
      admin: "/admin",
      landlord: "/landlord",
      tenant: "/tenant",
    };
    return routeMap[user.value.role] || "/";
  });

  function setSession(accessToken, userInfo) {
    token.value = accessToken;
    user.value = userInfo;

    if (accessToken) {
      localStorage.setItem("access_token", accessToken);
    } else {
      localStorage.removeItem("access_token");
    }
  }

  function setUser(userInfo) {
    user.value = userInfo;
  }

  async function initialize() {
    if (initialized.value) {
      return;
    }

    if (!token.value) {
      initialized.value = true;
      return;
    }

    try {
      const response = await fetchCurrentUser();
      user.value = response.data.data;
    } catch {
      setSession("", null);
    } finally {
      initialized.value = true;
    }
  }

  async function login(credentials) {
    const response = await loginRequest(credentials);
    const payload = response.data.data;
    setSession(payload.access_token, payload.user);
    initialized.value = true;
    return payload.user;
  }

  async function logout() {
    try {
      if (token.value) {
        await logoutRequest();
      }
    } catch {
      // Ignore logout errors and clear local session anyway.
    } finally {
      setSession("", null);
      initialized.value = true;
    }
  }

  return {
    dashboardRoute,
    initialized,
    initialize,
    isAuthenticated,
    login,
    logout,
    setUser,
    token,
    user,
  };
});
