import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from datetime import datetime
from app.core.database import SessionLocal, Base, engine
from app.models.entities import User, Order, OrderCategory, OrderStatus

db = SessionLocal()

# 清空已有旧测试数据重新插入6大板块
db.query(Order).delete()
db.commit()

# 查询或创建初始模拟用户
users = []
mock_profiles = [
    ("mock_user_1", "南区-陈同学", "20230501", "陈志豪", "计算机学院", True, "13871380001", "chen_hg_2023"),
    ("mock_user_2", "西区-王学姐", "20220312", "王舒雅", "文学院", True, "13971380002", "wang_hgnu"),
    ("mock_user_3", "北区-张同学", "", "", "生农学院", False, "13771380003", "zhang_bio"),
    ("mock_user_4", "求实楼-小李", "20240815", "李嘉豪", "数统学院", True, "13671380004", "li_math_hg"),
]

for openid, nick, sid, rname, col, ver, phone, wx_id in mock_profiles:
    u = db.query(User).filter(User.openid == openid).first()
    if not u:
        u = User(openid=openid, nickname=nick, student_id=sid, real_name=rname, college=col, is_verified=ver, phone=phone, wechat_id=wx_id)
        db.add(u)
        db.commit()
        db.refresh(u)
    users.append(u)

orders_data = [
    {
        "category": OrderCategory.TAKEOUT,
        "title": "二食堂一楼黄焖鸡米饭代送到南区7栋楼下",
        "description": "午高峰求帮忙带一份无辣黄焖鸡+可乐，送到南区7栋宿管门口微信联系，感谢同学！",
        "price": 3.0,
        "location": "南区7栋",
        "contact_info": "微信: chen_hg_2023",
        "status": OrderStatus.PENDING,
        "publisher_id": users[0].id
    },
    {
        "category": OrderCategory.EXPRESS,
        "title": "南区菜鸟驿站代取中通大件包裹(约3kg)",
        "description": "取件码 5-2-3012，是个电风扇箱子，送到南区11栋502宿舍门口，放在门口拍照即可。",
        "price": 4.0,
        "location": "南区11栋",
        "contact_info": "微信: wang_hgnu",
        "status": OrderStatus.PENDING,
        "publisher_id": users[1].id
    },
    {
        "category": OrderCategory.MARKET,
        "title": "九成新考研英语一黄皮书+单词书打包出",
        "description": "2025版考研英语真题试卷全套未做笔记，送张剑历年真题解析，西区或图书馆当面交易。",
        "price": 25.0,
        "location": "西区图书馆",
        "contact_info": "电话/微信: 13971380002",
        "status": OrderStatus.PENDING,
        "publisher_id": users[1].id
    },
    {
        "category": OrderCategory.NAIL,
        "title": "宿舍手作美甲穿戴甲定制，附赠果冻胶工具包",
        "description": "课余爱好手作穿戴甲，法式猫眼/腮红甲都有，支持提供甲围尺寸定制，西区宿舍支持上门贴甲！",
        "price": 18.0,
        "location": "西区4栋宿舍",
        "contact_info": "微信: zhang_bio",
        "status": OrderStatus.PENDING,
        "publisher_id": users[2].id
    },
    {
        "category": OrderCategory.TUTOR,
        "title": "大一高等数学A上册微积分期中辅导答疑",
        "description": "大三数统学长，高数满绩，可在线或在求实楼自习室一对一答疑2小时，理清极限与导数考点。",
        "price": 30.0,
        "location": "南区求实楼",
        "contact_info": "微信: li_math_hg",
        "status": OrderStatus.PENDING,
        "publisher_id": users[3].id
    },
    {
        "category": OrderCategory.EXCHANGE,
        "title": "多出一盆健康绿萝/多肉，想换一本东野圭吾的小说",
        "description": "宿舍养的绿萝很茂盛，带陶瓷盆，想交换一本看过的推理小说，北区宿舍随时当面换。",
        "price": 0.0,
        "location": "北区3栋",
        "contact_info": "微信: zhang_bio",
        "status": OrderStatus.PENDING,
        "publisher_id": users[2].id
    }
]

for od in orders_data:
    o = Order(**od)
    db.add(o)

db.commit()
print(f"成功注入 {len(orders_data)} 条初始校园互助需求！")
db.close()
