// utils/api.js
const BASE_URL = "http://127.0.0.1:8000/api/v1";

const request = (options) => {
  return new Promise((resolve, reject) => {
    const userInfo = wx.getStorageSync('userInfo') || {};
    const userId = userInfo.id || '';

    wx.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'X-User-Id': userId,
        ...options.header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          const msg = (res.data && res.data.detail) ? res.data.detail : '请求失败';
          wx.showToast({
            title: msg,
            icon: 'none',
            duration: 2500
          });
          reject(res.data);
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络连接异常，请检查后端服务',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// 敏感词本地预校验（双重防护）
const SENSITIVE_KEYWORDS = [
  "代课", "替课", "刷课", "刷网课", "代考", "替考", "代写作业", "代写论文", "写作业", "作弊", "枪手"
];

const checkSensitive = (text) => {
  if (!text) return false;
  const clean = text.replace(/[\s\-_，。！？\*\#\@\$\%\^\&\(\)]+/g, '').toLowerCase();
  for (let word of SENSITIVE_KEYWORDS) {
    if (text.includes(word) || clean.includes(word)) {
      return word;
    }
  }
  return false;
};

module.exports = {
  request,
  checkSensitive,
  BASE_URL
};
