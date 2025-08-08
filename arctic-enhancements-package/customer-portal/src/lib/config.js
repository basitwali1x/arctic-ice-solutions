export const API_ENDPOINT = "https://api.arcticicesolutions.com/v2";
export const BASE_URL = "https://arcticicesolutions.com";

export const config = {
  api: {
    baseURL: API_ENDPOINT,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    }
  },
  auth: {
    tokenKey: 'arctic_auth_token',
    refreshTokenKey: 'arctic_refresh_token',
  },
  features: {
    orderTracking: true,
    paymentPortal: true,
    feedbackSystem: true,
    mobileApp: true,
  }
};

export default config;
