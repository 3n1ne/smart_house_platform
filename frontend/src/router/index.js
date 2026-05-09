import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import AdminDashboard from "../views/admin/AdminDashboard.vue";
import LoginView from "../views/auth/LoginView.vue";
import RegisterView from "../views/auth/RegisterView.vue";
import HomeView from "../views/common/HomeView.vue";
import HouseDetailView from "../views/common/HouseDetailView.vue";
import HouseListView from "../views/common/HouseListView.vue";
import NewsListView from "../views/common/NewsListView.vue";
import LandlordDashboard from "../views/landlord/LandlordDashboard.vue";
import TenantDashboard from "../views/tenant/TenantDashboard.vue";


const routes = [
  { path: "/", name: "home", component: HomeView },
  { path: "/login", name: "login", component: LoginView },
  { path: "/register", name: "register", component: RegisterView },
  { path: "/houses", name: "houses", component: HouseListView },
  { path: "/houses/:id", name: "house-detail", component: HouseDetailView },
  { path: "/news", name: "news", component: NewsListView },
  {
    path: "/landlord",
    name: "landlord",
    component: LandlordDashboard,
    meta: { requiresAuth: true, roles: ["landlord"] },
  },
  {
    path: "/tenant",
    name: "tenant",
    component: TenantDashboard,
    meta: { requiresAuth: true, roles: ["tenant"] },
  },
  {
    path: "/admin",
    name: "admin",
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ["admin"] },
  },
];


const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();
  if (!authStore.initialized) {
    await authStore.initialize();
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      path: "/login",
      query: { redirect: to.fullPath },
    };
  }

  if (to.meta.roles?.length && !to.meta.roles.includes(authStore.user?.role)) {
    return authStore.dashboardRoute || "/";
  }

  if ((to.path === "/login" || to.path === "/register") && authStore.isAuthenticated) {
    return authStore.dashboardRoute || "/";
  }

  return true;
});


export default router;
