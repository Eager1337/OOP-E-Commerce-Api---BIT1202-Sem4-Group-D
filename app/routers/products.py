"""
Product router with full CRUD operations and async I/O demonstration.
"""
import asyncio
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth import require_manager, get_current_user
from app.models import Product, Category, User
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ProductListResponse, InventoryStats
)

router = APIRouter(prefix="/products", tags=["Products"])


async def send_low_stock_notification(product_name: str, stock: int) -> None:
    """
    Async I/O-bound task: Simulate sending notification for low stock.
    Demonstrates async/await for I/O-bound operations.
    """
    await asyncio.sleep(0.5)  # Simulate network delay
    print(f"[NOTIFICATION] Low stock alert: {product_name} (Qty: {stock})")


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Create a new product (Manager/Admin only).

    - **name**: Product name
    - **sku**: Unique stock keeping unit
    - **price**: Product price (must be > 0)
    - **stock_quantity**: Available stock
    - **category_id**: Associated category
    """
    # Check for duplicate SKU
    result = await db.execute(select(Product).where(Product.sku == product_data.sku))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )

    # Validate category exists
    if product_data.category_id:
        result = await db.execute(select(Category).where(Category.id == product_data.category_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

    db_product = Product(**product_data.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    # Eager load category for response
    result = await db.execute(
        select(Product).options(selectinload(Product.category)).where(Product.id == db_product.id)
    )
    return result.scalar_one()


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    search: Optional[str] = None,
    in_stock: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List products with filtering and pagination.

    - **skip/limit**: Pagination
    - **category_id**: Filter by category
    - **min_price/max_price**: Price range filter
    - **search**: Search by name
    - **in_stock**: Filter by stock availability
    """
    query = select(Product).options(selectinload(Product.category))
    count_query = select(func.count(Product.id))

    filters = []

    if category_id:
        filters.append(Product.category_id == category_id)
    if min_price is not None:
        filters.append(Product.price >= min_price)
    if max_price is not None:
        filters.append(Product.price <= max_price)
    if search:
        filters.append(Product.name.ilike(f"%{search}%"))
    if in_stock is not None:
        if in_stock:
            filters.append(Product.stock_quantity > 0)
        else:
            filters.append(Product.stock_quantity == 0)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Product.created_at.desc())
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListResponse(
        items=products,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit
    )


@router.get("/stats/inventory", response_model=InventoryStats)
async def get_inventory_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Get inventory statistics (Manager/Admin only).
    Demonstrates aggregation queries.
    """
    # Total products
    total_result = await db.execute(select(func.count(Product.id)).where(Product.is_active == True))
    total_products = total_result.scalar()

    # Total categories
    cat_result = await db.execute(select(func.count(Category.id)))
    total_categories = cat_result.scalar()

    # Low stock items (< 10)
    low_stock_result = await db.execute(
        select(func.count(Product.id)).where(Product.stock_quantity < 10)
    )
    low_stock_items = low_stock_result.scalar()

    # Total inventory value
    value_result = await db.execute(
        select(func.sum(Product.price * Product.stock_quantity)).where(Product.is_active == True)
    )
    total_value = value_result.scalar() or Decimal("0")

    # Average price
    avg_result = await db.execute(
        select(func.avg(Product.price)).where(Product.is_active == True)
    )
    avg_price = avg_result.scalar() or Decimal("0")

    return InventoryStats(
        total_products=total_products,
        total_categories=total_categories,
        low_stock_items=low_stock_items,
        total_inventory_value=total_value,
        average_product_price=avg_price
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific product by ID with category details."""
    result = await db.execute(
        select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Update a product (Manager/Admin only)."""
    result = await db.execute(
        select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    # Validate category if provided
    if "category_id" in update_data and update_data["category_id"]:
        cat_result = await db.execute(select(Category).where(Category.id == update_data["category_id"]))
        if not cat_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    # Check for low stock and trigger async notification
    if product.stock_quantity < 10:
        await send_low_stock_notification(product.name, product.stock_quantity)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """Delete a product (Manager/Admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    await db.delete(product)
    await db.commit()
    return None
