# 黄师互助 (JMarKet) - 校园C2C互助服务平台

服务于黄冈师范学院的校园C2C即时需求对接平台。采用原生微信小程序 + Python FastAPI 后端架构，支持需求发布、接单响应、订单流转与社群推单。

## 目录结构
```text
JMarKet/
├── app.js / app.json / app.wxss  # 根目录小程序全局入口与配置
├── pages/
│   ├── index/                    # 需求大厅（分类筛选、列表、接单）
│   ├── publish/                  # 需求发布（表单、敏感词检测、群推单文案生成）
│   ├── detail/                   # 订单详情（接单、联系方式展示、举报入口、取消/完成）
│   ├── my/                       # 个人中心（发布历史、接单记录、学号认证）
│   └── report/                   # 订单举报页面
├── utils/                        # 请求封装与工具函数
├── project.config.json           # 微信开发者工具配置文件（miniprogramRoot: "./"）
├── backend/                      # Python FastAPI 后端服务
│   ├── app/
│   │   ├── api/                  # API 路由 (auth, orders, reports, user)
│   │   ├── core/                 # 配置、敏感词过滤、数据库会话
│   │   ├── models/               # SQLAlchemy 数据模型
│   │   ├── schemas/              # Pydantic 数据验证契约
│   │   └── main.py               # 启动主入口
│   ├── requirements.txt          # 后端依赖
│   └── test_api.py               # 自动化测试用例
└── README.md
```

## 核心设计与规范
1. **初期板块（6大分类）**：
   - `takeout`: 代取外卖
   - `express`: 代取快递
   - `market`: 卖生活用品
   - `nail`: 宿舍美甲
   - `tutor`: 代教辅导
   - `exchange`: 互换东西
   - *（严格过滤并拦截代课、刷课、代写作业等违规违纪内容）*
2. **轻量认证体系**：微信授权快速登录；可选填姓名学号生成认证徽章，但不强实名，未认证也可使用完整功能。
3. **零门槛试跑机制**：不做内置支付（线下/当面结算）、不抽成、不做内置聊天（展示微信/QQ/电话对接），最低成本验证市场可行性。
4. **社群联动**：新订单发布成功即生成标准化群推送文案，支持一键复制，配合全员禁言互助微信群快速推单与抢单。

## 启动后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API 文档访问：http://127.0.0.1:8000/docs

## 微信开发者工具导入
1. 打开微信开发者工具，选择“导入项目”。
2. 项目目录直接选择根目录 `D:\czj_project\JMarKet`。
3. 微信开发者工具会自动识别根目录下的 `app.json` 和 `project.config.json` 并直接启动。
4. AppID 填入测试号或个人小程序 AppID 即可。
