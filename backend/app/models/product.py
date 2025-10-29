from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, Numeric, ForeignKey, BigInteger, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[category_id])


class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    long_description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    discount_percent = Column(Numeric(5, 2), nullable=True, default=0)
    currency = Column(String, default="INR")
    brand = Column(String, nullable=True)
    available = Column(Boolean, default=True)
    # Rating fields
    average_rating = Column(Numeric(3, 2), nullable=True, default=0)  # 0.00 to 5.00
    total_reviews = Column(Integer, nullable=False, default=0)
    rating_distribution = Column(JSON, nullable=True)  # {1: count, 2: count, 3: count, 4: count, 5: count}
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="product")
    
    # New user state relationships
    cart_items = relationship("UserCart", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("UserWishlist", back_populates="product", cascade="all, delete-orphan")
    purchase_history = relationship("PurchaseHistory", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"
    
    image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    s3_key = Column(String, nullable=False)
    cdn_url = Column(String, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    format = Column(String, nullable=True)
    variant = Column(String, nullable=True)  # original, thumb, small, webp
    alt_text = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")

