import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_and_disclaimer():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "黄师互助" in data["app"]
    assert "免责声明" in data["disclaimer"]

def test_full_order_flow():
    # 1. 登录两个用户：用户A（发布者），用户B（接单者）
    res_a = client.post("/api/v1/auth/login", json={"openid": "user_a_openid", "nickname": "南区小张"})
    assert res_a.status_code == 200
    user_a = res_a.json()
    uid_a = user_a["id"]

    res_b = client.post("/api/v1/auth/login", json={"openid": "user_b_openid", "nickname": "西区小李"})
    assert res_b.status_code == 200
    user_b = res_b.json()
    uid_b = user_b["id"]

    # 2. 用户A完善联系方式并做轻量认证
    client.put("/api/v1/user/profile", headers={"X-User-Id": str(uid_a)}, json={"phone": "13800000001", "wechat_id": "wx_zhang"})
    res_ver = client.post("/api/v1/user/verify", headers={"X-User-Id": str(uid_a)}, json={
        "student_id": "2023010101",
        "real_name": "张三",
        "college": "计算机学院"
    })
    assert res_ver.status_code == 200
    assert res_ver.json()["is_verified"] is True

    # 3. 敏感词拦截测试：尝试发布代课违规内容
    bad_order = {
        "category": "takeout",
        "title": "急求明天上午高数代课",
        "description": "求替课两节，有酬劳",
        "price": 30.0,
        "location": "南区求实楼",
        "contact_info": "wx_zhang"
    }
    res_bad = client.post("/api/v1/orders", headers={"X-User-Id": str(uid_a)}, json=bad_order)
    assert res_bad.status_code == 400
    assert "违规" in res_bad.json()["detail"] or "敏感词" in res_bad.json()["detail"]

    # 4. 正常发布合规需求（代取快递）
    good_order = {
        "category": "express",
        "title": "菜鸟驿站代取中通大件包裹",
        "description": "送至南区11栋宿舍楼下，重量约2kg",
        "price": 3.0,
        "location": "南区11栋",
        "contact_info": "wx_zhang"
    }
    res_order = client.post("/api/v1/orders", headers={"X-User-Id": str(uid_a)}, json=good_order)
    assert res_order.status_code == 200
    order_data = res_order.json()
    order_id = order_data["id"]
    assert order_data["status"] == "pending"
    assert "📢 黄师互助新单提醒！" in order_data["share_text"]

    # 5. 需求大厅浏览筛选
    res_list = client.get("/api/v1/orders?category=express&status=pending")
    assert res_list.status_code == 200
    items = res_list.json()
    assert any(item["id"] == order_id for item in items)

    # 6. 用户B接单
    res_accept = client.post(f"/api/v1/orders/{order_id}/accept", headers={"X-User-Id": str(uid_b)})
    assert res_accept.status_code == 200
    assert res_accept.json()["status"] == "accepted"
    assert res_accept.json()["acceptor_id"] == uid_b

    # 7. 重复接单应被拦截
    res_reaccept = client.post(f"/api/v1/orders/{order_id}/accept", headers={"X-User-Id": str(uid_a)})
    assert res_reaccept.status_code == 400

    # 8. 状态更新为进行中，并确认完成
    client.post(f"/api/v1/orders/{order_id}/progress", headers={"X-User-Id": str(uid_b)})
    res_complete = client.post(f"/api/v1/orders/{order_id}/complete", headers={"X-User-Id": str(uid_a)})
    assert res_complete.status_code == 200
    assert res_complete.json()["status"] == "completed"

    # 9. 完成后不可再修改
    res_after = client.post(f"/api/v1/orders/{order_id}/cancel", headers={"X-User-Id": str(uid_a)})
    assert res_after.status_code == 400

    # 10. 举报功能测试
    res_report = client.post("/api/v1/reports", headers={"X-User-Id": str(uid_b)}, json={
        "order_id": order_id,
        "reason": "联系方式有误/诈骗排查",
        "detail": "测试举报流程"
    })
    assert res_report.status_code == 200
    assert res_report.json()["code"] == 200
