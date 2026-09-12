// pages/publish/publish.js
const { request, checkSensitive } = require('../../utils/api');

Page({
  data: {
    categories: [
      { key: 'takeout', name: '代取外卖', icon: '🍔' },
      { key: 'express', name: '代取快递', icon: '📦' },
      { key: 'market', name: '卖生活用品', icon: '🛒' },
      { key: 'nail', name: '宿舍美甲', icon: '💅' },
      { key: 'tutor', name: '代教辅导', icon: '📚' },
      { key: 'exchange', name: '互换东西', icon: '🔄' }
    ],
    category: 'express',
    title: '',
    description: '',
    price: '',
    location: '',
    contact_info: '',

    showShareModal: false,
    shareText: '',
    createdOrderId: null
  },

  onSelectCat(e) {
    this.setData({ category: e.currentTarget.dataset.key });
  },

  onInputTitle(e) { this.setData({ title: e.detail.value }); },
  onInputDesc(e) { this.setData({ description: e.detail.value }); },
  onInputPrice(e) { this.setData({ price: e.detail.value }); },
  onInputLocation(e) { this.setData({ location: e.detail.value }); },
  onInputContact(e) { this.setData({ contact_info: e.detail.value }); },

  onSubmit() {
    const { category, title, description, price, location, contact_info } = this.data;

    if (!title.trim()) {
      return wx.showToast({ title: '请输入标题', icon: 'none' });
    }
    if (!description.trim()) {
      return wx.showToast({ title: '请填写详细描述', icon: 'none' });
    }
    if (!location.trim()) {
      return wx.showToast({ title: '请填写地点/楼栋', icon: 'none' });
    }
    if (!contact_info.trim()) {
      return wx.showToast({ title: '请填写联系方式', icon: 'none' });
    }

    // 本地快速敏感词预过滤
    const fullText = `${title} ${description} ${location}`;
    const hit = checkSensitive(fullText);
    if (hit) {
      return wx.showModal({
        title: '发布受限',
        content: `发布内容包含受限关键词【${hit}】，黄师互助严禁发布代课、代考、刷课、写作业等违纪违规信息！`,
        showCancel: false,
        confirmColor: '#ff4d4f'
      });
    }

    const payload = {
      category,
      title: title.trim(),
      description: description.trim(),
      price: parseFloat(price) || 0.0,
      location: location.trim(),
      contact_info: contact_info.trim()
    };

    wx.showLoading({ title: '发布中...' });

    request({
      url: '/orders',
      method: 'POST',
      data: payload
    }).then(res => {
      wx.hideLoading();
      this.setData({
        showShareModal: true,
        shareText: res.share_text,
        createdOrderId: res.id,
        // 清空表单
        title: '',
        description: '',
        price: '',
        location: '',
        contact_info: ''
      });
    }).catch(() => {
      wx.hideLoading();
    });
  },

  copyShareText() {
    wx.setClipboardData({
      data: this.data.shareText,
      success: () => {
        wx.showToast({ title: '文案已复制到剪贴板！', icon: 'success' });
      }
    });
  },

  closeShareModal() {
    const id = this.data.createdOrderId;
    this.setData({ showShareModal: false });
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    });
  }
});
