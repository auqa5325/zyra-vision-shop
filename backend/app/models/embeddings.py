from sqlalchemy import Column, String, DateTime, JSON, BigInteger, ForeignKey, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class EmbeddingsMeta(Base):
    __tablename__ = "embeddings_meta"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    object_type = Column(String, nullable=False)  # product, user, query
    object_id = Column(UUID(as_uuid=True), nullable=False)
    embedding_file = Column(String, nullable=True)  # path or S3 key
    vector_index = Column(Integer, nullable=True)  # row index in embedding file
    dim = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint
    __table_args__ = (
        {"extend_existing": True}
    )


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"
    
    rec_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    request_context = Column(JSON, nullable=True)  # query, filters, alpha, k, etc.
    candidate_products = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # ordered list of product_ids
    returned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recommendation_logs")


class ABTest(Base):
    __tablename__ = "ab_tests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_name = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    cohort = Column(String, nullable=True)  # control, variantA, etc.
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ab_tests")


class SystemAudit(Base):
    __tablename__ = "system_audit"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    component = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    message = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

