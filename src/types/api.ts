/**
 * Additional type definitions for API integration
 */

export interface Category {
  category_id: number;
  name: string;
  slug: string;
  parent_id?: number;
}

export interface CategoryHierarchy {
  category_id: number;
  name: string;
  slug: string;
  parent_id?: number;
  product_count: number;
  children: CategoryHierarchy[];
}

export interface ProductImage {
  image_id: string;
  product_id: string;
  s3_key: string;
  cdn_url?: string;
  width?: number;
  height?: number;
  format?: string;
  variant?: string;
  alt_text?: string;
  is_primary: boolean;
  created_at: string;
}

export interface BackendProduct {
  product_id: string;
  sku?: string;
  name: string;
  short_description?: string;
  long_description?: string;
  category_id?: number;
  tags?: string[];
  price?: number;
  discount_percent?: number;
  currency: string;
  brand?: string;
  available: boolean;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  images: ProductImage[];
  image_url?: string;
  rating?: number;
}

export interface ProductDetail extends BackendProduct {
  category?: Category;
}

export interface RecommendationResponse {
  product_id: string;
  name: string;
  price: number;
  image_url?: string;
  hybrid_score: number;
  reason_features?: {
    matched_tags?: string[];
    cf_score?: number;
    content_score?: number;
    source?: string;
  };
}

export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface ProductListParams extends PaginationParams {
  category_id?: number;
  min_price?: number;
  max_price?: number;
  available_only?: boolean;
}

export interface SearchParams {
  query: string;
  k?: number;
}

export interface RecommendationParams {
  user_id?: string;
  query?: string;
  alpha?: number;
  k?: number;
}

// Re-export the main Product interface for convenience
export type { Product, CartItem } from './product';
