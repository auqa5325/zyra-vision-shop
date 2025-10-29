/**
 * Product API service
 */

import apiClient from './api';
import { Product } from '../types/product';
import { CategoryHierarchy, Category } from '../types/api';

export interface ProductListParams {
  skip?: number;
  limit?: number;
  category_id?: number;
  min_price?: number;
  max_price?: number;
  available_only?: boolean;
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
  price?: number | string; // Can be number or string from API
  discount_percent?: number | string; // Can be number or string from API
  currency: string;
  brand?: string;
  available: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  images: ProductImage[];
  image_url?: string;
  rating?: number;
}

export interface ProductDetail extends BackendProduct {
  category?: Category;
}

class ProductService {
  private categoryCache: Map<number, string> = new Map();

  /**
   * Get list of products with optional filters
   */
  async getProducts(params: ProductListParams = {}): Promise<Product[]> {
    const backendProducts = await apiClient.get<BackendProduct[]>('/api/products/', params);
    return backendProducts.map(this.transformProduct);
  }

  /**
   * Get a single product by ID
   */
  async getProductById(id: string): Promise<Product> {
    const backendProduct = await apiClient.get<ProductDetail>(`/api/products/${id}`);
    return this.transformProduct(backendProduct);
  }

  /**
   * Get categories with hierarchical structure
   */
  async getCategoriesHierarchy(): Promise<CategoryHierarchy[]> {
    const hierarchy = await apiClient.get<CategoryHierarchy[]>('/api/products/categories/hierarchy');
    // Update category cache
    this.updateCategoryCache(hierarchy);
    return hierarchy;
  }

  /**
   * Get all categories
   */
  async getCategories(): Promise<Category[]> {
    const categories = await apiClient.get<Category[]>('/api/products/categories/');
    // Update category cache
    categories.forEach(cat => this.categoryCache.set(cat.category_id, cat.name));
    return categories;
  }

  /**
   * Search products by query
   */
  async searchProducts(query: string, k: number = 10): Promise<Product[]> {
    const backendProducts = await apiClient.get<BackendProduct[]>('/api/products/search', {
      q: query,
      k
    });
    return backendProducts.map(this.transformProduct);
  }

  /**
   * Get products by category (handles both parent and subcategories)
   */
  async getProductsByCategory(categoryId: number, params: Omit<ProductListParams, 'category_id'> = {}): Promise<Product[]> {
    const backendProducts = await apiClient.get<BackendProduct[]>(`/api/products/categories/${categoryId}/products`, params);
    return backendProducts.map(this.transformProduct);
  }

  /**
   * Update category cache from hierarchy data
   */
  private updateCategoryCache(hierarchy: CategoryHierarchy[]): void {
    hierarchy.forEach(category => {
      this.categoryCache.set(category.category_id, category.name);
      category.children.forEach(child => {
        this.categoryCache.set(child.category_id, child.name);
      });
    });
  }

  /**
   * Transform backend product to frontend Product format
   */
  private transformProduct = (backendProduct: BackendProduct | ProductDetail): Product => {
    // Get primary image URL
    let imageUrl = backendProduct.image_url;
    if (!imageUrl && backendProduct.images && backendProduct.images.length > 0) {
      const primaryImage = backendProduct.images.find(img => img.is_primary) || backendProduct.images[0];
      imageUrl = primaryImage.cdn_url || '';
    }

    // Use actual rating from database (defaults to 0 if no reviews)
    const rating = backendProduct.rating || 0;

    return {
      product_id: backendProduct.product_id,
      name: backendProduct.name,
      description: backendProduct.short_description || backendProduct.long_description || '',
      price: typeof backendProduct.price === 'string' ? parseFloat(backendProduct.price) : (backendProduct.price || 0),
      discount_percent: typeof backendProduct.discount_percent === 'string' ? parseFloat(backendProduct.discount_percent) : (backendProduct.discount_percent || 0),
      image_url: imageUrl || '/placeholder.svg',
      rating,
      category: this.getCategoryName(backendProduct.category_id),
      category_id: backendProduct.category_id,
      brand: backendProduct.brand,
      reason_features: {
        matched_tags: backendProduct.tags || [],
        cf_score: 0.8, // Mock collaborative filtering score
        content_score: 0.9, // Mock content-based score
      }
    };
  }



  /**
   * Get category name by ID using dynamic cache
   */
  private getCategoryName = (categoryId?: number): string => {
    return categoryId ? this.categoryCache.get(categoryId) || 'Other' : 'Other';
  }
}

export const productService = new ProductService();
export default productService;
