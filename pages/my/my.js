// pages/my/my.js
const { request } = require('../../utils/api');

Page({
  data: {
    userInfo: {},
    studentId: '',
    realName: '',
    college: '',

    currentTab: 'published',
    publishedList: [],
    acceptedList: [],

    categoryMap: {
      takeout: '代取外卖',
      express: '代取快递',
      market: '卖生活用品',
      nail: '宿舍美甲',
      tutor: '代教辅导',
      exchange: '互换东西'
    },
    statusMap: {
      pending: '待接单',
      accepted: '已接单',
      in_progress: '进行中',
      completed: '已完成',
      cancelled: '已取消'
    }
  },

  onShow() {
    this.refreshUserInfo();
    this.loadMyOrders();
  },

  refreshUserInfo() {
    request({ url: '/user/me' }).then(res => {
      this.setData({ userInfo: res });
      wx.setStorageSync('userInfo', res);
    }).catch(err => {
      console.error(err);
    });
  },

  loadMyOrders() {
    request({ url: '/user/my-published' }).then(res => {
      this.setData({ publishedList: res });
    });

    request({ url: '/user/my-accepted' }).then(res => {
      this.setData({ acceptedList: res });
    });
  },

  onInputStudentId(e) { this.setData({ studentId: e.detail.value }); },
  onInputRealName(e) { this.setData({ realName: e.detail.value }); },
  onInputCollege(e) { this.setData({ college: e.detail.value }); },

  submitVerify() {
    const { studentId, realName, college } = this.data;
    if (!studentId.trim() || !realName.trim()) {
      return wx.showToast({ title: '请填写学号和姓名', icon: 'none' });
    }

    wx.showLoading({ title: '认证中...' });
    request({
      url: '/user/verify',
      method: 'POST',
      data: {
        student_id: studentId.trim(),
        real_name: realName.trim(),
        college: college.trim() || undefined
      }
    }).then(res => {
      wx.hideLoading();
      wx.showToast({ title: '校园信任认证成功！', icon: 'success' });
      this.setData({ userInfo: res });
      wx.setStorageSync('userInfo', res);
    }).catch(() => {
      wx.hideLoading();
    });
  },

  switchTab(e) {
    this.setData({ currentTab: e.currentTarget.dataset.tab });
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    });
  }
});
