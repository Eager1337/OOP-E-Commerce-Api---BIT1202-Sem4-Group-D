"""
Order router with full CRUD and business logic.
"""
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth import get_current_user, require_manager
from app.models import Order, OrderItem, Product, OrderStatus, User
from app.schemas import OrderCreate, OrderUpdate, OrderResponse, SalesStats

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order for the authenticated user.

    - **items**: List of products with quantities
    - **shipping_address**: Delivery address
    """
    # Calculate total and validate stock
    total_amount = Decimal("0")
    order_items = []

    for item in order_data.items:
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
            )

        # Deduct stock
        product.stock_quantity -= item.quantity
        total_amount += Decimal(str(product.price)) * item.quantity

        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": product.price
        })

    # Create order
    db_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        status=OrderStatus.PENDING
    )
    db.add(db_order)
    await db.flush()  # Get order ID

    # Create order items
    for item_data in order_items:
        db_item = OrderItem(order_id=db_order.id, **item_data)
        db.add(db_item)

    await db.commit()

    # Return with relationships loaded
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.user)
        )
        .where(Order.id == db_order.id)
    )
    return result.scalar_one()


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: OrderStatus = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List orders. Users see their own; Managers see all.
    """
    query = select(Order).options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.user)
    )

    # Role-based filtering
    if current_user.role == UserRole.CUSTOMER:
        query = query.where(Order.user_id == current_user.id)

    if status:
        query = query.where(Order.status == status)

    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific order by ID."""
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.user)
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Check ownership
    if current_user.role == UserRole.CUSTOMER and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )

    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Update order status (Manager/Admin only)."""
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.user)
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    update_data = order_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    await db.commit()
    await db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Delete an order (Manager/Admin only)."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    await db.delete(order)
    await db.commit()
    return None


@router.get("/stats/sales", response_model=SalesStats)
async def get_sales_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Get sales statistics (Manager/Admin only)."""
    # Total orders
    total_result = await db.execute(select(func.count(Order.id)))
    total_orders = total_result.scalar()

    # Total revenue
    revenue_result = await db.execute(select(func.sum(Order.total_amount)))
    total_revenue = revenue_result.scalar() or Decimal("0")

    # Average order value
    avg_result = await db.execute(select(func.avg(Order.total_amount)))
    avg_order = avg_result.scalar() or Decimal("0")

    # Orders by status
    status_result = await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    orders_by_status = {status.value: count for status, count in status_result.all()}

    return SalesStats(
        total_orders=total_orders,
        total_revenue=total_revenue,
        average_order_value=avg_order,
        orders_by_status=orders_by_status
    )
