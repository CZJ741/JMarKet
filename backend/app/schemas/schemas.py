from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.entities import OrderCategory, OrderStatus

# 用户相关契约
class UserBase(BaseModel):
    nickname: Optional[str] = "黄师同学"
    avatar_url: Optional[str] = ""

class UserLoginRequest(BaseModel):
    openid: str
    nickname: Optional[str] = "黄师同学"
    avatar_url: Optional[str] = ""

class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    wechat_id: Optional[str] = None

class StudentVerificationRequest(BaseModel):
    student_id: str = Field(..., min_length=4, max_length=32, description="学号")
    real_name: str = Field(..., min_length=2, max_length=32, description="真实姓名")
    college: Optional[str] = Field(None, max_length=64, description="学院")

class UserResponse(UserBase):
    id: int
    openid: str
    student_id: Optional[str] = None
    real_name: Optional[str] = None
    college: Optional[str] = None
    is_verified: bool = False
    phone: Optional[str] = ""
    wechat_id: Optional[str] = ""
    created_at: datetime

    class Config:
        from_attributes = True

# 订单相关契约
class OrderCreate(BaseModel):
    category: OrderCategory
    title: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=2, max_length=1000)
    price: float = Field(0.0, ge=0.0)
    location: str = Field(..., min_length=2, max_length=100)
    contact_info: str = Field(..., min_length=2, max_length=100)

class OrderBriefResponse(BaseModel):
    id: int
    category: OrderCategory
    title: str
    price: float
    location: str
    status: OrderStatus
    created_at: datetime
    publisher_nickname: str
    publisher_is_verified: bool

    class Config:
        from_attributes = True

class OrderDetailResponse(BaseModel):
    id: int
    category: OrderCategory
    title: str
    description: str
    price: float
    location: str
    contact_info: str
    status: OrderStatus
    created_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    publisher_id: int
    publisher_nickname: str
    publisher_avatar: str
    publisher_is_verified: bool

    acceptor_id: Optional[int] = None
    acceptor_nickname: Optional[str] = None
    acceptor_is_verified: Optional[bool] = None
    acceptor_contact: Optional[str] = None

    share_text: Optional[str] = None # 用于微信群一键推单复制的文案

    class Config:
        from_attributes = True

# 举报契约
class ReportCreate(BaseModel):
    order_id: int
    reason: str = Field(..., min_length=2, max_length=100)
    detail: Optional[str] = Field("", max_length=500)
