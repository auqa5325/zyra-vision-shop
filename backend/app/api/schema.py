"""
Database schema and API information endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from typing import Dict, List, Any
import json

from app.database import get_db, engine
from app.models import Base

router = APIRouter(prefix="/api/schema", tags=["schema"])


@router.get("/tables")
async def get_database_schema(db: Session = Depends(get_db)):
    """Get complete database schema information"""
    try:
        inspector = inspect(engine)
        
        schema_info = {
            "tables": {},
            "relationships": [],
            "indexes": {},
            "constraints": {}
        }
        
        # Get all table names
        table_names = inspector.get_table_names()
        
        for table_name in table_names:
            # Get columns
            columns = inspector.get_columns(table_name)
            column_info = []
            
            for col in columns:
                column_info.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col["default"]) if col["default"] is not None else None,
                    "primary_key": col.get("primary_key", False),
                    "autoincrement": col.get("autoincrement", False)
                })
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            fk_info = []
            for fk in foreign_keys:
                fk_info.append({
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                    "name": fk.get("name")
                })
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            index_info = []
            for idx in indexes:
                index_info.append({
                    "name": idx["name"],
                    "columns": idx["column_names"],
                    "unique": idx["unique"],
                    "type": idx.get("type")
                })
            
            schema_info["tables"][table_name] = {
                "columns": column_info,
                "foreign_keys": fk_info,
                "indexes": index_info
            }
        
        # Get table relationships from SQLAlchemy models
        relationships = []
        for mapper in Base.registry.mappers:
            table_name = mapper.class_.__tablename__
            for prop in mapper.iterate_properties:
                if hasattr(prop, 'mapper') and hasattr(prop, 'key'):
                    relationships.append({
                        "table": table_name,
                        "relationship": prop.key,
                        "target_table": prop.mapper.class_.__tablename__,
                        "relationship_type": str(type(prop).__name__)
                    })
        
        schema_info["relationships"] = relationships
        
        return schema_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@router.get("/tables/{table_name}")
async def get_table_details(table_name: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific table"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get columns
        columns = inspector.get_columns(table_name)
        column_info = []
        
        for col in columns:
            column_info.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"],
                "default": str(col["default"]) if col["default"] is not None else None,
                "primary_key": col.get("primary_key", False),
                "autoincrement": col.get("autoincrement", False),
                "comment": col.get("comment")
            })
        
        # Get foreign keys
        foreign_keys = inspector.get_foreign_keys(table_name)
        fk_info = []
        for fk in foreign_keys:
            fk_info.append({
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
                "name": fk.get("name")
            })
        
        # Get indexes
        indexes = inspector.get_indexes(table_name)
        index_info = []
        for idx in indexes:
            index_info.append({
                "name": idx["name"],
                "columns": idx["column_names"],
                "unique": idx["unique"],
                "type": idx.get("type")
            })
        
        # Get sample data (first 5 rows)
        sample_query = text(f"SELECT * FROM {table_name} LIMIT 5")
        sample_result = db.execute(sample_query)
        sample_data = [dict(row._mapping) for row in sample_result]
        
        # Get row count
        count_query = text(f"SELECT COUNT(*) as count FROM {table_name}")
        count_result = db.execute(count_query)
        row_count = count_result.scalar()
        
        return {
            "table_name": table_name,
            "columns": column_info,
            "foreign_keys": fk_info,
            "indexes": index_info,
            "row_count": row_count,
            "sample_data": sample_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table details: {str(e)}")


@router.get("/apis")
async def get_api_endpoints():
    """Get all available API endpoints"""
    try:
        # This would typically be populated from FastAPI's OpenAPI schema
        # For now, we'll return a structured list of known endpoints
        
        api_endpoints = {
            "authentication": {
                "base_path": "/api/auth",
                "endpoints": [
                    {
                        "path": "/api/auth/register",
                        "method": "POST",
                        "description": "Register a new user",
                        "requires_auth": False,
                        "request_schema": "UserCreate",
                        "response_schema": "TokenResponse"
                    },
                    {
                        "path": "/api/auth/login",
                        "method": "POST",
                        "description": "Login user with email and password",
                        "requires_auth": False,
                        "request_schema": "UserLogin",
                        "response_schema": "TokenResponse"
                    },
                    {
                        "path": "/api/auth/refresh",
                        "method": "POST",
                        "description": "Refresh access token",
                        "requires_auth": False,
                        "request_schema": "TokenRefresh",
                        "response_schema": "TokenResponse"
                    },
                    {
                        "path": "/api/auth/logout",
                        "method": "POST",
                        "description": "Logout user",
                        "requires_auth": True
                    },
                    {
                        "path": "/api/auth/me",
                        "method": "GET",
                        "description": "Get current user profile",
                        "requires_auth": True,
                        "response_schema": "UserResponse"
                    }
                ]
            },
            "products": {
                "base_path": "/api/products",
                "endpoints": [
                    {
                        "path": "/api/products/",
                        "method": "GET",
                        "description": "List products with filters",
                        "requires_auth": False,
                        "query_params": ["skip", "limit", "category_id", "min_price", "max_price", "available_only"]
                    },
                    {
                        "path": "/api/products/{product_id}",
                        "method": "GET",
                        "description": "Get product by ID",
                        "requires_auth": False
                    },
                    {
                        "path": "/api/products/categories/",
                        "method": "GET",
                        "description": "List all categories",
                        "requires_auth": False
                    },
                    {
                        "path": "/api/products/categories/{category_id}/products",
                        "method": "GET",
                        "description": "Get products by category",
                        "requires_auth": False
                    },
                    {
                        "path": "/api/products/search",
                        "method": "GET",
                        "description": "Search products",
                        "requires_auth": False,
                        "query_params": ["q", "k"]
                    }
                ]
            },
            "recommendations": {
                "base_path": "/api/recommendations",
                "endpoints": [
                    {
                        "path": "/api/recommendations/top-pick",
                        "method": "GET",
                        "description": "Get top recommendation for homepage",
                        "requires_auth": False,
                        "response_schema": "RecommendationResponse"
                    },
                    {
                        "path": "/api/recommendations/hybrid",
                        "method": "GET",
                        "description": "Get hybrid recommendations",
                        "requires_auth": False,
                        "query_params": ["user_id", "query", "alpha", "k"]
                    },
                    {
                        "path": "/api/recommendations/personalized",
                        "method": "GET",
                        "description": "Get personalized recommendations",
                        "requires_auth": True,
                        "query_params": ["user_id", "k"]
                    },
                    {
                        "path": "/api/recommendations/content",
                        "method": "GET",
                        "description": "Get content-based recommendations",
                        "requires_auth": False,
                        "query_params": ["product_id", "k"]
                    },
                    {
                        "path": "/api/recommendations/collaborative",
                        "method": "GET",
                        "description": "Get collaborative filtering recommendations",
                        "requires_auth": True,
                        "query_params": ["user_id", "k"]
                    }
                ]
            },
            "interactions": {
                "base_path": "/api/interactions",
                "endpoints": [
                    {
                        "path": "/api/interactions/",
                        "method": "POST",
                        "description": "Track user interaction",
                        "requires_auth": False,
                        "request_schema": "InteractionCreate"
                    }
                ]
            },
            "images": {
                "base_path": "/api/images",
                "endpoints": [
                    {
                        "path": "/api/images/proxy/{image_path:path}",
                        "method": "GET",
                        "description": "Proxy external images",
                        "requires_auth": False
                    }
                ]
            },
            "schema": {
                "base_path": "/api/schema",
                "endpoints": [
                    {
                        "path": "/api/schema/tables",
                        "method": "GET",
                        "description": "Get complete database schema",
                        "requires_auth": True
                    },
                    {
                        "path": "/api/schema/tables/{table_name}",
                        "method": "GET",
                        "description": "Get detailed table information",
                        "requires_auth": True
                    },
                    {
                        "path": "/api/schema/apis",
                        "method": "GET",
                        "description": "Get all API endpoints",
                        "requires_auth": False
                    }
                ]
            }
        }
        
        return api_endpoints
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get API endpoints: {str(e)}")


@router.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        stats = {
            "tables": {},
            "total_tables": len(table_names),
            "total_rows": 0
        }
        
        for table_name in table_names:
            # Get row count
            count_query = text(f"SELECT COUNT(*) as count FROM {table_name}")
            count_result = db.execute(count_query)
            row_count = count_result.scalar()
            
            # Get table size
            size_query = text(f"""
                SELECT 
                    pg_size_pretty(pg_total_relation_size('{table_name}')) as size,
                    pg_total_relation_size('{table_name}') as size_bytes
            """)
            size_result = db.execute(size_query)
            size_row = size_result.fetchone()
            
            stats["tables"][table_name] = {
                "row_count": row_count,
                "size": size_row[0] if size_row else "Unknown",
                "size_bytes": size_row[1] if size_row else 0
            }
            stats["total_rows"] += row_count
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")
