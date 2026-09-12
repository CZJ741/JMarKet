// pages/index/index.js
const { request } = require('../../utils/api');

Page({
  data: {
    selectedCategory: '',
    categories: [
      { key: 'takeout', name: '代取外卖', icon: '🍔' },
      { key: 'express', name: '代取快递', icon: '📦' },
      { key: 'market', name: '卖生活用品', icon: '🛒' },
      { key: 'nail', name: '宿舍美甲', icon: '💅' },
      { key: 'tutor', name: '代教辅导', icon: '📚' },
      { key: 'exchange', name: '互换东西', icon: '🔄' }
    ],
    categoryMap: {
      takeout: '代取外卖',
      express: '代取快递',
      market: '卖生活用品',
      nail: '宿舍美甲',
      tutor: '代教辅导',
      exchange: '互换东西'
    },
    orders: [],
    page: 1,
    pageSize: 20,
    hasMore: true
  },

  onLoad() {
    this.fetchOrders();
  },

  onPullDownRefresh() {
    this.setData({ page: 1, orders: [], hasMore: true }, () => {
      this.fetchOrders(() => {
        wx.stopPullDownRefresh();
      });
    });
  },

  onSelectCategory(e) {
    const cat = e.currentTarget.dataset.cat;
    this.setData({
      selectedCategory: cat,
      page: 1,
      orders: [],
      hasMore: true
    }, () => {
      this.fetchOrders();
    });
  },

  fetchOrders(callback) {
    const { selectedCategory, page, pageSize } = this.data;
    let url = `/orders?status=pending&page=${page}&page_size=${pageSize}`;
    if (selectedCategory) {
      url += `&category=${selectedCategory}`;
    }

    request({ url }).then(res => {
      this.setData({
        orders: page === 1 ? res : this.data.orders.concat(res),
        hasMore: res.length === pageSize
      });
      if (callback) callback();
    }).catch(err => {
      console.error(err);
      if (callback) callback();
    });
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    });
  },

  quickAccept(e) {
    const id = e.currentTarget.dataset.id;
    wx.showModal({
      title: '确认接单',
      content: '接单后请及时与发布者联系，诚信互助，确定接单吗？',
      confirmColor: '#1890ff',
      success: (res) => {
        if (res.confirm) {
          request({
            url: `/orders/${id}/accept`,
            method: 'POST'
          }).then(() => {
            wx.showToast({ title: '接单成功！', icon: 'success' });
            setTimeout(() => {
              wx.navigateTo({ url: `/pages/detail/detail?id=${id}` });
            }, 800);
          });
        }
      }
    });
  }
});
