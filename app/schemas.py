"""
Pydantic schemas for request/response validation and serialization.
Demonstrates type annotations, inheritance, and data transformation.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from app.models import UserRole, OrderStatus


# ============== Base Schemas ==============

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============== User Schemas ==============

class UserBase(BaseSchema):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=72)
    role: Optional[UserRole] = UserRole.CUSTOMER

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: str) -> str:
        """bcrypt accepts at most 72 bytes, not 72 Unicode characters."""
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return value


class UserUpdate(BaseSchema):
    """Schema for user profile updates."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: Optional[str]) -> Optional[str]:
        """bcrypt accepts at most 72 bytes, not 72 Unicode characters."""
        if value is not None and len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return value


class UserResponse(UserBase):
    """Schema for user responses (excludes password)."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime


class UserInDB(UserResponse):
    """Schema for internal user representation."""
    hashed_password: str


# ============== Token Schemas ==============

class Token(BaseSchema):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseSchema):
    """Schema for decoded token payload."""
    username: Optional[str] = None
    role: Optional[UserRole] = None


# ============== Category Schemas ==============

class CategoryBase(BaseSchema):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    slug: str = Field(..., min_length=1, max_length=100)


class CategoryCreate(CategoryBase):
    """Schema for creating categories."""
    pass


class CategoryUpdate(BaseSchema):
    """Schema for updating categories."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category responses."""
    id: int
    is_active: bool
    created_at: datetime


# ============== Product Schemas ==============

class ProductBase(BaseSchema):
    """Base product schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock_quantity: int = Field(..., ge=0)
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    """Schema for creating products."""
    pass


class ProductUpdate(BaseSchema):
    """Schema for updating products."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product responses."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryResponse] = None


class ProductListResponse(BaseSchema):
    """Schema for paginated product list."""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int


# ============== Order Item Schemas ==============

class OrderItemBase(BaseSchema):
    """Base order item schema."""
    product_id: int
    quantity: int = Field(..., ge=1)


class OrderItemCreate(OrderItemBase):
    """Schema for creating order items."""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema for order item responses."""
    id: int
    unit_price: Decimal
    product: Optional[ProductResponse] = None


# ============== Order Schemas ==============

class OrderBase(BaseSchema):
    """Base order schema."""
    shipping_address: Optional[str] = None


class OrderCreate(OrderBase):
    """Schema for creating orders."""
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseSchema):
    """Schema for updating orders."""
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None


class OrderResponse(OrderBase):
    """Schema for order responses."""
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    user: Optional[UserResponse] = None


# ============== Review Schemas ==============

class ReviewBase(BaseSchema):
    """Base review schema."""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Schema for creating reviews."""
    product_id: int


class ReviewUpdate(BaseSchema):
    """Schema for updating reviews."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    """Schema for review responses."""
    id: int
    product_id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None


# ============== Statistics Schemas ==============

class InventoryStats(BaseSchema):
    """Schema for inventory statistics."""
    total_products: int
    total_categories: int
    low_stock_items: int
    total_inventory_value: Decimal
    average_product_price: Decimal


class SalesStats(BaseSchema):
    """Schema for sales statistics."""
    total_orders: int
    total_revenue: Decimal
    average_order_value: Decimal
    orders_by_status: dict


class HealthCheck(BaseSchema):
    """Schema for API health check response."""
    status: str
    version: str
    timestamp: datetime
    database: str
