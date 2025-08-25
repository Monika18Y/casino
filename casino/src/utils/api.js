import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器，添加 token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器，处理错误
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // 判断是否是登录或注册请求
    const isAuthRequest = error.config && (
      error.config.url.includes('/accounts/login/') ||
      error.config.url.includes('/accounts/register/')
    );

    if (error.response && error.response.status === 401 && !isAuthRequest) {
      // 未授权且不是登录/注册请求，清除 token 并重定向到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('currentUser');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// 用户相关 API
export const userApi = {
  // 用户注册
  register: (userData) => {
    return api.post('/accounts/register/', userData);
  },
  
  // 用户登录
  login: (credentials) => {
    return api.post('/accounts/login/', credentials);
  },
  
  // 刷新 token
  refreshToken: (refreshToken) => {
    return api.post('/accounts/token/refresh/', { refresh: refreshToken });
  },
  
  // 获取用户信息
  getUserProfile: () => {
    return api.get('/accounts/profile/');
  },
  
  // 获取用户余额
  getBalance: () => {
    return api.get('/accounts/balance/');
  },
};

// 交易相关 API
export const transactionApi = {
  // 获取交易记录
  getTransactions: () => {
    return api.get('/accounts/transactions/');
  },
  
  // 充值
  deposit: (amount) => {
    return api.post('/accounts/deposit/', { amount });
  },
  
  // 提现
  withdraw: (amount) => {
    return api.post('/accounts/withdraw/', { amount });
  },
};

// 投注记录相关 API
export const betApi = {
  // 获取投注记录
  getBetRecords: () => {
    return api.get('/bets/records/');
  },
  
  // 创建投注记录
  createBetRecord: (betData) => {
    return api.post('/bets/create/', betData);
  },
  
  // 获取投注统计
  getBetStatistics: () => {
    return api.get('/bets/statistics/');
  },
};

// 幸运快三相关 API
export const luckyThreeApi = {
  getStatus: () => api.get('/bets/luckythree/status/'),
  placeBet: (bet_types, bet_amount) => api.post('/bets/luckythree/place_bet/', { bet_types, bet_amount }),
};

export default api; 