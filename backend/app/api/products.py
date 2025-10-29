"""
Product API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.models import Product, Category, ProductImage
from app.schemas import (
    ProductResponse, ProductDetail, ProductSearch, 
    CategoryResponse, ProductImageResponse
)
from app.services import ContentBasedService
from sqlalchemy import func

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    available_only: bool = True,
    db: Session = Depends(get_db)
):
    """List products with pagination and filters"""
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price:
        query = query.filter(Product.price >= min_price)
    
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    if available_only:
        query = query.filter(Product.available == True)
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add computed fields
    for product in products:
        # Set image_url from primary image
        primary_image = None
        for img in product.images:
            if img.is_primary:
                primary_image = img.cdn_url
                break
        if not primary_image and product.images:
            primary_image = product.images[0].cdn_url
        
        # Set computed fields
        product.image_url = primary_image
        # Set rating for backward compatibility (use average_rating if available)
        if product.average_rating is not None:
            product.rating = float(product.average_rating)
            # Also convert average_rating to float for frontend
            product.average_rating = float(product.average_rating)
        elif product.rating is None:
            product.rating = 0.0
    
    return products


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., min_length=1),
    k: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search products using semantic similarity"""
    try:
        content_service = ContentBasedService()
        results = content_service.search_products(q, k=k)
        
        # Get product details
        product_ids = [result[0] for result in results]
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        
        # Create mapping for ordering
        product_map = {p.product_id: p for p in products}
        ordered_products = [product_map[pid] for pid in product_ids if pid in product_map]
        
        # Add computed fields (same as list_products)
        for product in ordered_products:
            # Set image_url from primary image
            primary_image = None
            for img in product.images:
                if img.is_primary:
                    primary_image = img.cdn_url
                    break
            if not primary_image and product.images:
                primary_image = product.images[0].cdn_url
            
            # Set computed fields
            product.image_url = primary_image
            # Set rating for backward compatibility (use average_rating if available)
            if product.average_rating is not None:
                product.rating = float(product.average_rating)
            elif product.rating is None:
                product.rating = 0.0
        
        return ordered_products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Get product details with images and category"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Add computed fields
    primary_image = None
    for img in product.images:
        if img.is_primary:
            primary_image = img.cdn_url
            break
    if not primary_image and product.images:
        primary_image = product.images[0].cdn_url
    
    product.image_url = primary_image
    # Set rating for backward compatibility (use average_rating if available)
    if product.average_rating is not None:
        product.rating = float(product.average_rating)
    elif product.rating is None:
        product.rating = 0.0
    
    return product


@router.get("/categories/", response_model=List[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    categories = db.query(Category).all()
    return categories


@router.get("/categories/hierarchy")
async def get_categories_hierarchy(db: Session = Depends(get_db)):
    """Get categories with hierarchical structure and product counts"""
    from sqlalchemy import func
    
    # Get all categories with product counts
    categories_with_counts = db.query(
        Category,
        func.count(Product.product_id).label('product_count')
    ).outerjoin(
        Product, Category.category_id == Product.category_id
    ).group_by(Category.category_id).all()
    
    # Build hierarchy
    hierarchy = []
    category_map = {}
    
    # First pass: create category objects
    for category, product_count in categories_with_counts:
        category_obj = {
            "category_id": category.category_id,
            "name": category.name,
            "slug": category.slug,
            "parent_id": category.parent_id,
            "product_count": product_count,
            "children": []
        }
        category_map[category.category_id] = category_obj
    
    # Second pass: build hierarchy
    for category_id, category_obj in category_map.items():
        if category_obj["parent_id"] is None:
            # This is a parent category
            hierarchy.append(category_obj)
        else:
            # This is a child category
            parent = category_map.get(category_obj["parent_id"])
            if parent:
                parent["children"].append(category_obj)
    
    # Third pass: calculate total product counts for parent categories
    for parent_category in hierarchy:
        if parent_category["children"]:
            # Sum up product counts from all children
            total_count = sum(child["product_count"] for child in parent_category["children"])
            parent_category["product_count"] = total_count
    
    return hierarchy


@router.get("/categories/{category_id}/products", response_model=List[ProductResponse])
async def get_products_by_category(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get products by category (including subcategories if it's a parent category)"""
    # Check if this is a parent category
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.parent_id is None:
        # This is a parent category - get products from all subcategories
        subcategories = db.query(Category).filter(Category.parent_id == category_id).all()
        subcategory_ids = [subcat.category_id for subcat in subcategories]
        category_ids = [category_id] + subcategory_ids
    else:
        # This is a subcategory - get products only from this category
        category_ids = [category_id]
    
    products = db.query(Product).filter(
        Product.category_id.in_(category_ids),
        Product.available == True
    ).offset(skip).limit(limit).all()
    
    # Add computed fields
    for product in products:
        # Set image_url from primary image
        primary_image = None
        for img in product.images:
            if img.is_primary:
                primary_image = img.cdn_url
                break
        if not primary_image and product.images:
            primary_image = product.images[0].cdn_url
        
        # Set computed fields
        product.image_url = primary_image
        # Set rating for backward compatibility (use average_rating if available)
        if product.average_rating is not None:
            product.rating = float(product.average_rating)
            # Also convert average_rating to float for frontend
            product.average_rating = float(product.average_rating)
        elif product.rating is None:
            product.rating = 0.0
    
    return products


@router.post("/{product_id}/images", response_model=ProductImageResponse)
async def upload_product_image(
    product_id: UUID,
    file: bytes,
    variant: str = "original",
    content_type: str = "image/jpeg",
    db: Session = Depends(get_db)
):
    """Upload product image to S3"""
    # Check if product exists
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        from app.services.hybrid_storage import HybridStorageService
        storage_service = HybridStorageService()
        
        result = storage_service.upload_image(
            file_content=file,
            product_id=str(product_id),
            variant=variant,
            content_type=content_type
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Upload failed: {result.get('error')}")
        
        # Save to database
        image = ProductImage(
            product_id=product_id,
            s3_key=result["s3_key"],
            cdn_url=result["url"],
            variant=variant,
            format=content_type.split('/')[-1],
            alt_text=f"{product.name} - {variant} image"
        )
        
        db.add(image)
        db.commit()
        db.refresh(image)
        
        return image
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

