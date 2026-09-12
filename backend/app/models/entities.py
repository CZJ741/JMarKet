import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class OrderCategory(str, enum.Enum):
    TAKEOUT = "takeout"       # 代取外卖
    EXPRESS = "express"       # 代取快递
    MARKET = "market"         # 卖生活用品
    NAIL = "nail"             # 宿舍美甲
    TUTOR = "tutor"           # 代教辅导
    EXCHANGE = "exchange"     # 互换东西

class OrderStatus(str, enum.Enum):
    PENDING = "pending"         # 待接单
    ACCEPTED = "accepted"       # 已接单
    IN_PROGRESS = "in_progress" # 进行中
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(64), unique=True, index=True, nullable=False)
    nickname = Column(String(64), default="黄师同学")
    avatar_url = Column(String(255), default="")

    # 可选填写的实名认证信息（不强制校验，只做信任标识）
    student_id = Column(String(32), default="", nullable=True) # 学号
    real_name = Column(String(32), default="", nullable=True)  # 真实姓名
    college = Column(String(64), default="", nullable=True)    # 学院
    is_verified = Column(Boolean, default=False)               # 认证标识

    phone = Column(String(20), default="")
    wechat_id = Column(String(64), default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联
    published_orders = relationship("Order", foreign_keys="[Order.publisher_id]", back_populates="publisher")
    accepted_orders = relationship("Order", foreign_keys="[Order.acceptor_id]", back_populates="acceptor")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum(OrderCategory), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, default=0.0) # 报酬/价格，0表示互换或免费
    location = Column(String(128), nullable=False) # 地点/宿舍楼号
    contact_info = Column(String(128), nullable=False) # 联系方式（微信号/手机号）

    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)

    publisher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    acceptor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    publisher = relationship("User", foreign_keys=[publisher_id], back_populates="published_orders")
    acceptor = relationship("User", foreign_keys=[acceptor_id], back_populates="accepted_orders")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(String(255), nullable=False) # 举报原因（如诈骗、发布违规内容、骚扰、失联）
    detail = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
