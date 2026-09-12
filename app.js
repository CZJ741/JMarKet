// app.js
const { request } = require('./utils/api');

App({
  globalData: {
    userInfo: null,
    isLoggedIn: false
  },

  onLaunch() {
    const cachedUser = wx.getStorageSync('userInfo');
    if (cachedUser) {
      this.globalData.userInfo = cachedUser;
      this.globalData.isLoggedIn = true;
    } else {
      // 自动静默模拟登录或准备就绪
      this.autoLogin();
    }
  },

  autoLogin() {
    let mockOpenid = wx.getStorageSync('openid');
    if (!mockOpenid) {
      mockOpenid = 'wx_user_' + Math.random().toString(36).substring(2, 10);
      wx.setStorageSync('openid', mockOpenid);
    }

    request({
      url: '/auth/login',
      method: 'POST',
      data: {
        openid: mockOpenid,
        nickname: '黄师同学',
        avatar_url: ''
      }
    }).then(res => {
      this.globalData.userInfo = res;
      this.globalData.isLoggedIn = true;
      wx.setStorageSync('userInfo', res);
    }).catch(err => {
      console.error('自动登录失败:', err);
    });
  }
});
