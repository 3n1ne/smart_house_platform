import { API_BASE_URL } from "./client";


function inferAssetBaseUrl() {
  const configuredBaseUrl = import.meta.env.VITE_ASSET_BASE_URL;
  if (configuredBaseUrl) {
    return configuredBaseUrl.replace(/\/$/, "");
  }

  if (/^https?:\/\//i.test(API_BASE_URL)) {
    return new URL(API_BASE_URL).origin;
  }

  return "";
}


const ASSET_BASE_URL = inferAssetBaseUrl();


export function resolveAssetUrl(url) {
  if (!url || /^(https?:|data:|blob:)/i.test(url)) {
    return url;
  }

  if (url.startsWith("/")) {
    return ASSET_BASE_URL ? `${ASSET_BASE_URL}${url}` : url;
  }

  return url;
}
