<template>
  <section class="apt-search-page">
    <form class="apt-toolbar" @submit.prevent="submitSearch">
      <div class="apt-toolbar__search">
        <input v-model.trim="filters.keyword" type="text" placeholder="城市、区域、小区或地址" />
        <button type="submit">搜索</button>
      </div>

      <div class="apt-filter-row">
        <label>
          <span>城市</span>
          <select v-model="filters.city" @change="handleCityChange">
            <option value="">不限</option>
            <option v-for="city in cityOptions" :key="city" :value="city">{{ city }}</option>
          </select>
        </label>
        <label>
          <span>区域</span>
          <select v-model="filters.district">
            <option value="">不限</option>
            <option v-for="district in availableDistricts" :key="district" :value="district">
              {{ district }}
            </option>
          </select>
        </label>
        <label>
          <span>户型</span>
          <select v-model="filters.layout">
            <option value="">不限</option>
            <option v-for="layout in layoutOptions" :key="layout" :value="layout">{{ layout }}</option>
          </select>
        </label>
        <label class="apt-filter-row__rent">
          <span>租金范围</span>
          <input v-model.trim="rentRange" type="text" placeholder="如 3000-5000" />
        </label>
        <button class="apt-filter-row__reset" type="button" @click="resetFilters">重置</button>
      </div>
    </form>

    <div class="apt-filter-chips">
      <button type="button" @click="applyBudget('', 3000)">¥3000 以下</button>
      <button type="button" @click="applyBudget(3000, 5000)">¥3000-5000</button>
      <button type="button" @click="applyBudget(5000, 8000)">¥5000-8000</button>
      <button type="button" @click="applyLayout('1室1厅')">1室1厅</button>
      <button type="button" @click="applyLayout('2室1厅')">2室1厅</button>
      <button type="button" @click="applyLayout('3室2厅')">3室2厅</button>
    </div>

    <p v-if="errorMessage" class="form-message form-message--error">{{ errorMessage }}</p>

    <div class="apt-results-layout apt-results-layout--no-map">
      <main class="apt-list-panel">
        <header class="apt-list-head">
          <div>
            <h1>{{ total ? `${total} 套房源` : "搜索房源" }}</h1>
            <p>{{ resultSubtitle }}</p>
          </div>
          <span>{{ loading ? "加载中" : `第 ${page} / ${totalPages} 页` }}</span>
        </header>

        <div v-if="activeFilterLabels.length" class="apt-active-filters">
          <button
            v-for="item in activeFilterLabels"
            :key="item.key"
            type="button"
            @click="clearFilter(item.key)"
          >
            {{ item.label }} ×
          </button>
        </div>

        <div v-if="houses.length" class="apt-listings">
          <article v-for="(house, index) in houses" :key="house.id" class="apt-listing-card">
            <RouterLink class="apt-listing-card__media" :to="`/houses/${house.id}`">
              <img v-if="house.cover_url" :src="resolveAssetUrl(house.cover_url)" :alt="house.title" />
              <span v-else>暂无图片</span>
              <em v-if="index === 0">新上架</em>
            </RouterLink>

            <div class="apt-listing-card__body">
              <div class="apt-listing-card__price">
                <strong>{{ formatMoney(house.rent) }}</strong>
                <span>/月</span>
              </div>

              <RouterLink class="apt-listing-card__title" :to="`/houses/${house.id}`">
                {{ house.title }}
              </RouterLink>

              <p>{{ formatLocation(house) }}</p>

              <div class="apt-listing-card__facts">
                <span>{{ house.layout || "户型待补充" }}</span>
                <span>{{ formatArea(house.area) }}</span>
                <span>{{ house.orientation || "朝向待补充" }}</span>
              </div>

              <div class="apt-listing-card__actions">
                <RouterLink :to="`/houses/${house.id}`">查看详情</RouterLink>
                <span>{{ formatHouseStatus(house.status) }}</span>
              </div>
            </div>
          </article>
        </div>

        <div v-else-if="!loading" class="page-card empty-card">
          <h2 class="page-title page-title--section">暂无匹配房源</h2>
          <p class="page-text">减少筛选条件，或稍后再试。</p>
        </div>

        <div class="apt-pagination">
          <button type="button" :disabled="page <= 1 || loading" @click="changePage(page - 1)">
            上一页
          </button>
          <span>第 {{ page }} / {{ totalPages }} 页</span>
          <button type="button" :disabled="page >= totalPages || loading" @click="changePage(page + 1)">
            下一页
          </button>
        </div>
      </main>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import { resolveAssetUrl } from "../../api/assets";
import { fetchHouseList } from "../../api/house";

const route = useRoute();
const filters = reactive({
  city: "",
  district: "",
  layout: "",
  keyword: "",
  min_rent: "",
  max_rent: "",
});

const loading = ref(false);
const errorMessage = ref("");
const houses = ref([]);
const page = ref(1);
const pageSize = ref(8);
const total = ref(0);
const rentRange = ref("");

const cityOptions = [
  "北京市",
  "上海市",
  "广州市",
  "深圳市",
  "杭州市",
  "南京市",
  "苏州市",
  "成都市",
  "重庆市",
  "武汉市",
  "西安市",
  "天津市",
  "郑州市",
  "长沙市",
  "青岛市",
  "厦门市",
  "合肥市",
  "宁波市",
  "佛山市",
  "东莞市",
];

const districtOptionsByCity = {
  北京市: ["朝阳区", "海淀区", "东城区", "西城区", "丰台区", "通州区", "昌平区", "大兴区"],
  上海市: ["浦东新区", "徐汇区", "静安区", "黄浦区", "长宁区", "普陀区", "杨浦区", "闵行区"],
  广州市: ["天河区", "越秀区", "海珠区", "荔湾区", "白云区", "番禺区", "黄埔区", "南沙区"],
  深圳市: ["南山区", "福田区", "罗湖区", "宝安区", "龙岗区", "龙华区", "盐田区", "光明区"],
  杭州市: ["西湖区", "上城区", "拱墅区", "滨江区", "萧山区", "余杭区", "钱塘区", "临平区"],
  南京市: ["鼓楼区", "玄武区", "秦淮区", "建邺区", "栖霞区", "雨花台区", "江宁区", "浦口区"],
  苏州市: ["姑苏区", "工业园区", "虎丘区", "吴中区", "相城区", "吴江区", "昆山市", "常熟市"],
  成都市: ["锦江区", "青羊区", "金牛区", "武侯区", "成华区", "高新区", "双流区", "龙泉驿区"],
  重庆市: ["渝中区", "江北区", "南岸区", "九龙坡区", "沙坪坝区", "渝北区", "巴南区", "北碚区"],
  武汉市: ["江岸区", "江汉区", "武昌区", "洪山区", "汉阳区", "硚口区", "东西湖区", "东湖高新区"],
  西安市: ["雁塔区", "碑林区", "莲湖区", "新城区", "未央区", "灞桥区", "长安区", "高新区"],
  天津市: ["和平区", "河西区", "南开区", "河东区", "河北区", "红桥区", "滨海新区", "津南区"],
  郑州市: ["金水区", "二七区", "中原区", "管城回族区", "惠济区", "郑东新区", "高新区", "经开区"],
  长沙市: ["芙蓉区", "天心区", "岳麓区", "开福区", "雨花区", "望城区", "长沙县", "浏阳市"],
  青岛市: ["市南区", "市北区", "崂山区", "李沧区", "黄岛区", "城阳区", "即墨区", "胶州市"],
  厦门市: ["思明区", "湖里区", "集美区", "海沧区", "同安区", "翔安区"],
  合肥市: ["蜀山区", "庐阳区", "包河区", "瑶海区", "高新区", "经开区", "滨湖新区", "肥西县"],
  宁波市: ["海曙区", "江北区", "鄞州区", "镇海区", "北仑区", "奉化区", "慈溪市", "余姚市"],
  佛山市: ["禅城区", "南海区", "顺德区", "三水区", "高明区"],
  东莞市: ["南城街道", "东城街道", "莞城街道", "万江街道", "松山湖", "虎门镇", "长安镇", "厚街镇"],
};

const fallbackDistrictOptions = [
  "朝阳区",
  "浦东新区",
  "天河区",
  "南山区",
  "西湖区",
  "鼓楼区",
  "工业园区",
  "锦江区",
];

const layoutOptions = [
  "开间",
  "1室1厅",
  "2室1厅",
  "2室2厅",
  "3室1厅",
  "3室2厅",
  "4室2厅",
  "复式",
  "别墅",
  "两室一厅",
];

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));
const availableDistricts = computed(() => districtOptionsByCity[filters.city] || fallbackDistrictOptions);
const resultSubtitle = computed(() => {
  const location = [filters.city, filters.district].filter(Boolean).join(" · ") || "全部区域";
  return `${location} · ${filters.layout || "不限户型"} · ${formatRentRange(filters.min_rent, filters.max_rent)}`;
});
const activeFilterLabels = computed(() =>
  [
    { key: "city", label: filters.city && `城市：${filters.city}` },
    { key: "district", label: filters.district && `区域：${filters.district}` },
    { key: "keyword", label: filters.keyword && `关键词：${filters.keyword}` },
    { key: "layout", label: filters.layout && `户型：${filters.layout}` },
    { key: "rent", label: rentRange.value && `租金：${formatRentRange(filters.min_rent, filters.max_rent)}` },
  ].filter((item) => item.label)
);

function submitSearch() {
  page.value = 1;
  applyRentRange();
  loadHouses();
}

function buildParams() {
  return {
    ...filters,
    page: page.value,
    page_size: pageSize.value,
  };
}

async function loadHouses() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const response = await fetchHouseList(buildParams());
    const payload = response.data.data;
    houses.value = payload.items;
    total.value = payload.pagination.total;
  } catch (error) {
    errorMessage.value = error.message || "房源加载失败。";
    houses.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.city = "";
  filters.district = "";
  filters.layout = "";
  filters.keyword = "";
  filters.min_rent = "";
  filters.max_rent = "";
  rentRange.value = "";
  page.value = 1;
  loadHouses();
}

function changePage(nextPage) {
  page.value = nextPage;
  loadHouses();
}

function applyBudget(minRent, maxRent) {
  filters.min_rent = minRent;
  filters.max_rent = maxRent;
  rentRange.value = formatRentInput(minRent, maxRent);
  page.value = 1;
  loadHouses();
}

function applyLayout(layout) {
  filters.layout = layout;
  page.value = 1;
  loadHouses();
}

function clearFilter(key) {
  if (key === "rent") {
    filters.min_rent = "";
    filters.max_rent = "";
    rentRange.value = "";
  } else {
    filters[key] = "";
    if (key === "city") {
      filters.district = "";
    }
  }
  page.value = 1;
  loadHouses();
}

function handleCityChange() {
  if (filters.district && !availableDistricts.value.includes(filters.district)) {
    filters.district = "";
  }
}

function formatLocation(house) {
  return [house.city, house.district, house.community, house.address_detail].filter(Boolean).join(" · ") || "地址待补充";
}

function formatArea(area) {
  return area ? `${Number(area).toLocaleString("zh-CN")} 平方米` : "面积待补充";
}

function formatMoney(value) {
  if (value === "" || value === null || value === undefined) return "不限";
  return `¥${Number(value).toLocaleString("zh-CN", { maximumFractionDigits: 0 })}`;
}

function formatRentRange(minRent, maxRent) {
  if (minRent !== "" && maxRent !== "") return `${formatMoney(minRent)}-${formatMoney(maxRent)}`;
  if (minRent !== "") return `${formatMoney(minRent)}以上`;
  if (maxRent !== "") return `${formatMoney(maxRent)}以下`;
  return "不限预算";
}

function formatRentInput(minRent, maxRent) {
  if (minRent !== "" && maxRent !== "") return `${minRent}-${maxRent}`;
  if (minRent !== "") return `${minRent}以上`;
  if (maxRent !== "") return `${maxRent}以下`;
  return "";
}

function applyRentRange() {
  const normalized = rentRange.value.replace(/\s/g, "");
  if (!normalized) {
    filters.min_rent = "";
    filters.max_rent = "";
    return;
  }

  const betweenMatch = normalized.match(/^(\d+)(?:-|~|至|到)(\d+)$/);
  if (betweenMatch) {
    filters.min_rent = Number(betweenMatch[1]);
    filters.max_rent = Number(betweenMatch[2]);
    rentRange.value = `${filters.min_rent}-${filters.max_rent}`;
    return;
  }

  const belowMatch = normalized.match(/^(\d+)(?:以下|以内|内)$/);
  if (belowMatch) {
    filters.min_rent = "";
    filters.max_rent = Number(belowMatch[1]);
    rentRange.value = `${filters.max_rent}以下`;
    return;
  }

  const aboveMatch = normalized.match(/^(\d+)(?:以上|起)$/);
  if (aboveMatch) {
    filters.min_rent = Number(aboveMatch[1]);
    filters.max_rent = "";
    rentRange.value = `${filters.min_rent}以上`;
    return;
  }

  const exactMatch = normalized.match(/^(\d+)$/);
  if (exactMatch) {
    filters.min_rent = "";
    filters.max_rent = Number(exactMatch[1]);
    rentRange.value = `${filters.max_rent}以下`;
  }
}

function formatHouseStatus(status) {
  return {
    draft: "草稿",
    available: "可租",
    rented: "已出租",
    repairing: "维修中",
    offline: "已下架",
  }[status] || status || "状态待补充";
}

onMounted(() => {
  for (const key of ["keyword", "city", "district", "layout", "min_rent", "max_rent"]) {
    if (typeof route.query[key] === "string") {
      filters[key] = route.query[key];
    }
  }
  rentRange.value = formatRentInput(filters.min_rent, filters.max_rent);
  loadHouses();
});
</script>
