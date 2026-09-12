// pages/report/report.js
const { request } = require('../../utils/api');

Page({
  data: {
    orderId: null,
    reasons: [
      '发布违规内容 (代课/刷网课/代考/代写)',
      '涉嫌虚假信息或诈骗',
      '恶意拖延或接单后失联',
      '言语骚扰或不文明行为',
      '其他违规违约'
    ],
    selectedReason: '发布违规内容 (代课/刷网课/代考/代写)',
    detail: ''
  },

  onLoad(options) {
    if (options.orderId) {
      this.setData({ orderId: options.orderId });
    }
  },

  onSelectReason(e) {
    this.setData({ selectedReason: e.currentTarget.dataset.reason });
  },

  onInputDetail(e) {
    this.setData({ detail: e.detail.value });
  },

  submitReport() {
    const { orderId, selectedReason, detail } = this.data;
    if (!orderId) {
      return wx.showToast({ title: '订单ID无效', icon: 'none' });
    }

    wx.showLoading({ title: '提交中...' });
    request({
      url: '/reports',
      method: 'POST',
      data: {
        order_id: parseInt(orderId, 10),
        reason: selectedReason,
        detail: detail.trim()
      }
    }).then(res => {
      wx.hideLoading();
      wx.showModal({
        title: '举报提交成功',
        content: res.message || '我们已收到您的举报，将尽快介入核实并处置违规内容与账号。',
        showCancel: false,
        confirmColor: '#1890ff',
        success: () => {
          wx.navigateBack();
        }
      });
    }).catch(() => {
      wx.hideLoading();
    });
  }
});
