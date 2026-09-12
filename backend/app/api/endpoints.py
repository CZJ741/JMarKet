from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.sensitive import check_sensitive_content
from app.models.entities import User, Order, OrderCategory, OrderStatus, Report
from app.schemas.schemas import (
    UserLoginRequest, UserResponse, UserProfileUpdate, StudentVerificationRequest,
    OrderCreate, OrderBriefResponse, OrderDetailResponse, ReportCreate
)

router = APIRouter()

# 辅助函数：根据 Header 中的 X-User-Id 获取当前用户
def get_current_user(x_user_id: Optional[int] = Header(None, alias="X-User-Id"), db: Session = Depends(get_db)) -> User:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="请先在微信端完成登录授权")
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在或未授权")
    return user

# 辅助函数：生成全员禁言微信群标准化推单文案
def generate_share_text(order: Order) -> str:
    category_names = {
        OrderCategory.TAKEOUT: "【代取外卖】",
        OrderCategory.EXPRESS: "【代取快递】",
        OrderCategory.MARKET: "【二手闲置】",
        OrderCategory.NAIL: "【宿舍美甲】",
        OrderCategory.TUTOR: "【代教辅导】",
        OrderCategory.EXCHANGE: "【互换东西】"
    }
    cat_label = category_names.get(order.category, "【黄师互助】")
    price_str = f"¥{order.price:.1f}" if order.price > 0 else "免费/互助"
    text = (
        f"📢 黄师互助新单提醒！\n"
        f"{cat_label} {order.title}\n"
        f"💰 报酬/价格：{price_str}\n"
        f"📍 地点/楼栋：{order.location}\n"
        f"📝 说明：{order.description}\n"
        f"👉 进入小程序搜索订单号 #{order.id} 立即抢单！\n"
        f"（本群禁言，请在小程序内自助完成接单）"
    )
    return text

# ----------------- 用户/认证 API -----------------

@router.post("/auth/login", response_model=UserResponse, summary="微信登录/注册")
def wx_login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """模拟/实际微信登录，若用户不存在则创建，返回用户信息"""
    user = db.query(User).filter(User.openid == login_data.openid).first()
    if not user:
        user = User(
            openid=login_data.openid,
            nickname=login_data.nickname or "黄师同学",
            avatar_url=login_data.avatar_url or ""
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("/user/verify", response_model=UserResponse, summary="提交学号认证（增加信任标识，不强校验）")
def verify_student(
    req: StudentVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.student_id = req.student_id
    current_user.real_name = req.real_name
    current_user.college = req.college
    current_user.is_verified = True
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/user/me", response_model=UserResponse, summary="获取当前用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/user/profile", response_model=UserResponse, summary="更新用户联系方式及资料")
def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_data.nickname is not None:
        current_user.nickname = profile_data.nickname
    if profile_data.avatar_url is not None:
        current_user.avatar_url = profile_data.avatar_url
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    if profile_data.wechat_id is not None:
        current_user.wechat_id = profile_data.wechat_id
    db.commit()
    db.refresh(current_user)
    return current_user

# ----------------- 订单管理 API -----------------

@router.post("/orders", response_model=OrderDetailResponse, summary="发布新需求")
def create_order(
    req: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. 敏感词拦截（代课、刷网课、代写作业、替考等高危词）
    all_content = f"{req.title} {req.description} {req.location}"
    is_blocked, hit_word = check_sensitive_content(all_content)
    if is_blocked:
        raise HTTPException(
            status_code=400,
            detail=f"发布失败：内容中含有涉嫌违规或高风险敏感词【{hit_word}】，黄师互助严禁代课、刷网课、代写作业等行为！"
        )

    order = Order(
        category=req.category,
        title=req.title,
        description=req.description,
        price=req.price,
        location=req.location,
        contact_info=req.contact_info,
        status=OrderStatus.PENDING,
        publisher_id=current_user.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return OrderDetailResponse(
        id=order.id,
        category=order.category,
        title=order.title,
        description=order.description,
        price=order.price,
        location=order.location,
        contact_info=order.contact_info,
        status=order.status,
        created_at=order.created_at,
        publisher_id=current_user.id,
        publisher_nickname=current_user.nickname,
        publisher_avatar=current_user.avatar_url,
        publisher_is_verified=current_user.is_verified,
        share_text=generate_share_text(order)
    )

@router.get("/orders", response_model=List[OrderBriefResponse], summary="需求大厅列表（支持分类筛选）")
def list_orders(
    category: Optional[OrderCategory] = Query(None, description="分类筛选"),
    status: Optional[OrderStatus] = Query(OrderStatus.PENDING, description="状态筛选，默认仅看待接单"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if category:
        query = query.filter(Order.category == category)
    if status:
        query = query.filter(Order.status == status)

    orders = query.order_by(desc(Order.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    results = []
    for o in orders:
        results.append(OrderBriefResponse(
            id=o.id,
            category=o.category,
            title=o.title,
            price=o.price,
            location=o.location,
            status=o.status,
            created_at=o.created_at,
            publisher_nickname=o.publisher.nickname if o.publisher else "匿名同学",
            publisher_is_verified=o.publisher.is_verified if o.publisher else False
        ))
    return results

@router.get("/orders/{order_id}", response_model=OrderDetailResponse, summary="获取订单详情")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="需求订单不存在")

    acceptor_contact = None
    if order.acceptor:
        acceptor_contact = order.acceptor.wechat_id or order.acceptor.phone or "接单人已接单"

    return OrderDetailResponse(
        id=order.id,
        category=order.category,
        title=order.title,
        description=order.description,
        price=order.price,
        location=order.location,
        contact_info=order.contact_info,
        status=order.status,
        created_at=order.created_at,
        accepted_at=order.accepted_at,
        completed_at=order.completed_at,
        publisher_id=order.publisher.id,
        publisher_nickname=order.publisher.nickname,
        publisher_avatar=order.publisher.avatar_url,
        publisher_is_verified=order.publisher.is_verified,
        acceptor_id=order.acceptor.id if order.acceptor else None,
        acceptor_nickname=order.acceptor.nickname if order.acceptor else None,
        acceptor_is_verified=order.acceptor.is_verified if order.acceptor else None,
        acceptor_contact=acceptor_contact,
        share_text=generate_share_text(order)
    )

@router.post("/orders/{order_id}/accept", response_model=OrderDetailResponse, summary="接单（不可重复接单）")
def accept_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.publisher_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能接自己发布的需求")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="手慢啦！该需求已被接单或已关闭")

    order.status = OrderStatus.ACCEPTED
    order.acceptor_id = current_user.id
    order.accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    return get_order_detail(order_id, db)

@router.post("/orders/{order_id}/progress", response_model=OrderDetailResponse, summary="置为进行中")
def progress_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if current_user.id not in [order.publisher_id, order.acceptor_id]:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    if order.status != OrderStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="只有已接单状态可以更新为进行中")

    order.status = OrderStatus.IN_PROGRESS
    db.commit()
    db.refresh(order)
    return get_order_detail(order_id, db)

@router.post("/orders/{order_id}/complete", response_model=OrderDetailResponse, summary="确认完成（完成后不可修改）")
def complete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if current_user.id not in [order.publisher_id, order.acceptor_id]:
        raise HTTPException(status_code=403, detail="仅发布者或接单者可确认完成")
    if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="该订单已结束，不可修改")

    order.status = OrderStatus.COMPLETED
    order.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return get_order_detail(order_id, db)

@router.post("/orders/{order_id}/cancel", response_model=OrderDetailResponse, summary="取消订单（仅待接单时发布者可取消）")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.publisher_id != current_user.id:
        raise HTTPException(status_code=403, detail="仅发布者有权取消未接单的需求")
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="该订单已被接单或已流转，无法直接取消")

    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return get_order_detail(order_id, db)

# ----------------- 个人中心列表 -----------------

@router.get("/user/my-published", response_model=List[OrderBriefResponse], summary="我发布的需求")
def get_my_published(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.publisher_id == current_user.id).order_by(desc(Order.created_at)).all()
    return [
        OrderBriefResponse(
            id=o.id,
            category=o.category,
            title=o.title,
            price=o.price,
            location=o.location,
            status=o.status,
            created_at=o.created_at,
            publisher_nickname=current_user.nickname,
            publisher_is_verified=current_user.is_verified
        ) for o in orders
    ]

@router.get("/user/my-accepted", response_model=List[OrderBriefResponse], summary="我接单的需求")
def get_my_accepted(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.acceptor_id == current_user.id).order_by(desc(Order.created_at)).all()
    return [
        OrderBriefResponse(
            id=o.id,
            category=o.category,
            title=o.title,
            price=o.price,
            location=o.location,
            status=o.status,
            created_at=o.created_at,
            publisher_nickname=o.publisher.nickname if o.publisher else "同学",
            publisher_is_verified=o.publisher.is_verified if o.publisher else False
        ) for o in orders
    ]

# ----------------- 举报与安全 API -----------------

@router.post("/reports", summary="提交举报处理违规或诈骗")
def create_report(
    req: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == req.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="被举报订单不存在")

    report = Report(
        order_id=req.order_id,
        reporter_id=current_user.id,
        reason=req.reason,
        detail=req.detail or ""
    )
    db.add(report)
    db.commit()
    return {"code": 200, "message": "举报已提交，管理员将尽快核实并处理违规内容及账号"}
