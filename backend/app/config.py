from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database - Primary method (full connection string)
    database_url: Optional[str] = None
    
    # Database - Alternative method (individual components)
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    
    # AWS (Optional - will use local storage if not provided)
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    
    # Application Settings
    debug: bool = False
    environment: str = "development"
    
    # JWT Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # ML Models
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    faiss_index_path: str = "artifacts/faiss_products.index"
    embeddings_path: str = "artifacts/product_embeddings.npy"
    als_factors_path: str = "artifacts/item_factors.npy"
    
    # Recommendation
    default_alpha: float = 0.6
    default_top_k: int = 10
    
    # Gemini AI
    gemini_api_key: Optional[str] = None
    
    def get_database_url(self) -> str:
        """Get database URL, building from components if needed"""
        if self.database_url:
            return self.database_url
        
        # Build from individual components
        if all([self.db_host, self.db_port, self.db_name, self.db_user]):
            password_part = f":{self.db_password}" if self.db_password else ""
            return f"postgresql+psycopg2://{self.db_user}{password_part}@{self.db_host}:{self.db_port}/{self.db_name}"
        
        raise ValueError("Either DATABASE_URL or all individual DB components must be provided")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
