// pages/detail/detail.js
const { request } = require('../../utils/api');

Page({
  data: {
    orderId: null,
    order: null,
    isPublisher: false,
    isAcceptor: false,
    isRelated: false,

    categoryNames: {
      takeout: '代取外卖',
      express: '代取快递',
      market: '卖生活用品',
      nail: '宿舍美甲',
      tutor: '代教辅导',
      exchange: '互换东西'
    },
    statusNames: {
      pending: '待接单',
      accepted: '已接单',
      in_progress: '进行中',
      completed: '已完成',
      cancelled: '已取消'
    }
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ orderId: options.id });
      this.loadOrderDetail(options.id);
    }
  },

  onPullDownRefresh() {
    if (this.data.orderId) {
      this.loadOrderDetail(this.data.orderId, () => {
        wx.stopPullDownRefresh();
      });
    }
  },

  loadOrderDetail(id, cb) {
    request({
      url: `/orders/${id}`
    }).then(res => {
      const myUser = wx.getStorageSync('userInfo') || {};
      const isPublisher = (myUser.id === res.publisher_id);
      const isAcceptor = (myUser.id === res.acceptor_id);
      const isRelated = isPublisher || isAcceptor;

      this.setData({
        order: res,
        isPublisher,
        isAcceptor,
        isRelated
      });
      if (cb) cb();
    }).catch(err => {
      console.error(err);
      if (cb) cb();
    });
  },

  onAccept() {
    wx.showModal({
      title: '确认接单',
      content: '确定接下此单吗？接单后请尽快通过微信号或电话联系对方。',
      confirmColor: '#1890ff',
      success: (res) => {
        if (res.confirm) {
          request({
            url: `/orders/${this.data.orderId}/accept`,
            method: 'POST'
          }).then(() => {
            wx.showToast({ title: '接单成功！', icon: 'success' });
            this.loadOrderDetail(this.data.orderId);
          });
        }
      }
    });
  },

  onCancel() {
    wx.showModal({
      title: '取消需求',
      content: '确定要取消该需求发布吗？',
      confirmColor: '#ff4d4f',
      success: (res) => {
        if (res.confirm) {
          request({
            url: `/orders/${this.data.orderId}/cancel`,
            method: 'POST'
          }).then(() => {
            wx.showToast({ title: '需求已取消', icon: 'none' });
            this.loadOrderDetail(this.data.orderId);
          });
        }
      }
    });
  },

  onProgress() {
    request({
      url: `/orders/${this.data.orderId}/progress`,
      method: 'POST'
    }).then(() => {
      wx.showToast({ title: '已进入进行中状态', icon: 'success' });
      this.loadOrderDetail(this.data.orderId);
    });
  },

  onComplete() {
    wx.showModal({
      title: '确认完成',
      content: '请确认双方已完成对接互助。一旦确认完成，订单状态不可再修改！',
      confirmColor: '#52c41a',
      success: (res) => {
        if (res.confirm) {
          request({
            url: `/orders/${this.data.orderId}/complete`,
            method: 'POST'
          }).then(() => {
            wx.showToast({ title: '订单已圆满完成！', icon: 'success' });
            this.loadOrderDetail(this.data.orderId);
          });
        }
      }
    });
  },

  copyContact(e) {
    const val = e.currentTarget.dataset.val;
    if (!val) return;
    wx.setClipboardData({
      data: val,
      success: () => {
        wx.showToast({ title: '联系方式已复制', icon: 'success' });
      }
    });
  },

  copyShareText() {
    if (!this.data.order || !this.data.order.share_text) return;
    wx.setClipboardData({
      data: this.data.order.share_text,
      success: () => {
        wx.showToast({ title: '推单文案已复制', icon: 'success' });
      }
    });
  },

  goReport() {
    wx.navigateTo({
      url: `/pages/report/report?orderId=${this.data.orderId}`
    });
  }
});
