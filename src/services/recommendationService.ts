/**
 * Recommendation API service
 */

import apiClient from './api';
import { Product } from '../types/product';

export interface RecommendationParams {
  user_id?: string;
  query?: string;
  alpha?: number;
  k?: number;
}

export interface BackendRecommendation {
  product_id: string;
  name: string;
  price: number | string; // Can be string from API or number
  discount_percent?: number | string; // Can be string from API or number
  image_url?: string;
  hybrid_score: number;
  reason_features?: {
    matched_tags?: string[];
    cf_score?: number;
    content_score?: number;
    source?: string;
    hybrid?: boolean;
  };
}

class RecommendationService {
  /**
   * Get top pick recommendation for homepage
   */
  async getTopPick(): Promise<Product | null> {
    try {
      const backendRec = await apiClient.get<BackendRecommendation>('/api/recommendations/top-pick');
      return this.transformRecommendation(backendRec);
    } catch (error) {
      console.warn('Failed to get top pick:', error);
      return null;
    }
  }

  /**
   * Get hybrid recommendations
   */
  async getRecommendations(params: RecommendationParams = {}): Promise<Product[]> {
    try {
      const backendRecs = await apiClient.get<BackendRecommendation[]>('/api/recommendations/hybrid', params);
      
      if (!Array.isArray(backendRecs)) {
        throw new Error('Invalid response format: expected array');
      }
      
      const transformed = backendRecs.map((rec, index) => {
        try {
          return this.transformRecommendation(rec);
        } catch (error) {
          throw new Error(`Failed to transform recommendation ${index}: ${error.message}`);
        }
      });
      return transformed;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get personalized recommendations for logged-in user
   */
  async getPersonalizedRecommendations(userId: string, k: number = 10): Promise<Product[]> {
    const backendRecs = await apiClient.get<BackendRecommendation[]>('/api/recommendations/personalized', {
      user_id: userId,
      k
    });
    return backendRecs.map(this.transformRecommendation);
  }

  /**
   * Get similar products for a given product
   */
  async getSimilarProducts(productId: string, k: number = 10): Promise<Product[]> {
    const backendRecs = await apiClient.get<BackendRecommendation[]>('/api/recommendations/content', {
      product_id: productId,
      k
    });
    return backendRecs.map(this.transformRecommendation);
  }

  /**
   * Get collaborative filtering recommendations
   */
  async getCollaborativeRecommendations(userId: string, k: number = 10): Promise<Product[]> {
    try {
      console.log('Fetching collaborative recommendations for user:', userId, 'with k=', k);
      const backendRecs = await apiClient.get<BackendRecommendation[]>('/api/recommendations/collaborative', {
        user_id: userId,
        k
      });
      console.log('Collaborative recommendations response:', backendRecs);
      if (!Array.isArray(backendRecs)) {
        console.error('Invalid response format, expected array:', backendRecs);
        return [];
      }
      const transformed: Product[] = [];
      for (let i = 0; i < backendRecs.length; i++) {
        try {
          const product = this.transformRecommendation(backendRecs[i]);
          transformed.push(product);
        } catch (err) {
          console.error(`Error transforming recommendation ${i}:`, err, backendRecs[i]);
          // Continue with other items instead of failing completely
        }
      }
      console.log('Transformed collaborative recommendations:', transformed, 'count:', transformed.length);
      return transformed;
    } catch (error) {
      console.error('Failed to get collaborative recommendations:', error);
      return [];
    }
  }

  /**
   * Get user-item similarity score for a product
   */
  async getUserItemSimilarity(userId: string, productId: string): Promise<number> {
    try {
      const response = await apiClient.get<{
        user_id: string;
        product_id: string;
        similarity_score: number;
        normalized_score: number;
      }>("/api/recommendations/user-item-similarity", {
        user_id: userId,
        product_id: productId
      });
      return response.normalized_score;
    } catch (error) {
      console.error("Failed to get user-item similarity:", error);
      return 0;
    }
  }

  /**
   * Get hybrid recommendations for a product page ("You may also like")
   * - Content-based: Similar to current product
   * - Collaborative: User preferences within parent category (alpha=0.4)
   */
  async getProductYouMayAlsoLike(
    productId: string,
    userId: string | null,
    k: number = 8
  ): Promise<Product[]> {
    try {
      console.log('Fetching product recommendations for:', productId, 'user:', userId, 'k=', k);
      const params: Record<string, string | number> = {
        product_id: productId,
        k
      };
      if (userId) {
        params.user_id = userId;
      }
      const backendRecs = await apiClient.get<BackendRecommendation[]>('/api/recommendations/product-you-may-also-like', params);
      console.log('Product recommendations response:', backendRecs);
      if (!Array.isArray(backendRecs)) {
        console.error('Invalid response format, expected array:', backendRecs);
        return [];
      }
      const transformed: Product[] = [];
      for (let i = 0; i < backendRecs.length; i++) {
        try {
          const product = this.transformRecommendation(backendRecs[i]);
          transformed.push(product);
        } catch (err) {
          console.error(`Error transforming recommendation ${i}:`, err, backendRecs[i]);
          // Continue with other items instead of failing completely
        }
      }
      console.log('Transformed product recommendations:', transformed, 'count:', transformed.length);
      return transformed;
    } catch (error) {
      console.error('Failed to get product recommendations:', error);
      return [];
    }
  }

  /**
   * Get top sellers (most purchased products) for non-logged-in users
   */
  async getTopSellers(k: number = 10): Promise<Product[]> {
    try {
      console.log('Fetching top sellers with k=', k);
      const backendRecs = await apiClient.get<BackendRecommendation[]>('/api/recommendations/top-sellers', {
        k
      });
      console.log('Top sellers response:', backendRecs);
      if (!Array.isArray(backendRecs)) {
        console.error('Invalid response format, expected array:', backendRecs);
        return [];
      }
      const transformed: Product[] = [];
      for (let i = 0; i < backendRecs.length; i++) {
        try {
          const product = this.transformRecommendation(backendRecs[i]);
          transformed.push(product);
        } catch (err) {
          console.error(`Error transforming recommendation ${i}:`, err, backendRecs[i]);
          // Continue with other items instead of failing completely
        }
      }
      console.log('Transformed top sellers:', transformed, 'count:', transformed.length);
      return transformed;
    } catch (error) {
      console.error('Failed to get top sellers:', error);
      return [];
    }
  }

  /**
   * Get content-based recommendations using aggregated user data (purchase history, wishlist, cart)
   */
  async getContentBasedRecommendations(userId: string, k: number = 10): Promise<Product[]> {
    try {
      console.log('Fetching content-based recommendations for user:', userId, 'with k=', k);
      const backendRecs = await apiClient.get<BackendRecommendation[]>('/api/recommendations/content-based', {
        user_id: userId,
        k
      });
      console.log('Content-based recommendations response:', backendRecs);
      if (!Array.isArray(backendRecs)) {
        console.error('Invalid response format, expected array:', backendRecs);
        return [];
      }
      const transformed: Product[] = [];
      for (let i = 0; i < backendRecs.length; i++) {
        try {
          const product = this.transformRecommendation(backendRecs[i]);
          transformed.push(product);
        } catch (err) {
          console.error(`Error transforming recommendation ${i}:`, err, backendRecs[i]);
          // Continue with other items instead of failing completely
        }
      }
      console.log('Transformed content-based recommendations:', transformed, 'count:', transformed.length);
      return transformed;
    } catch (error) {
      console.error('Failed to get content-based recommendations:', error);
      return [];
    }
  }

  /**
   * Transform backend recommendation to frontend Product format
   */
  private transformRecommendation(backendRec: BackendRecommendation): Product {
    try {
      if (!backendRec || !backendRec.product_id || !backendRec.name) {
        console.error('Invalid recommendation data:', backendRec);
        throw new Error('Invalid recommendation data');
      }

      const price = typeof backendRec.price === 'string' 
        ? parseFloat(backendRec.price) 
        : (typeof backendRec.price === 'number' ? backendRec.price : 0);
      
      const discountPercent = backendRec.discount_percent 
        ? (typeof backendRec.discount_percent === 'string' 
           ? parseFloat(backendRec.discount_percent) 
           : (typeof backendRec.discount_percent === 'number' ? backendRec.discount_percent : 0))
        : 0;

      const hybridScore = backendRec.hybrid_score || 0.8;

      const product: Product = {
        product_id: String(backendRec.product_id),
        name: backendRec.name,
        description: '', // Not provided in recommendation response
        price: price,
        discount_percent: discountPercent,
        image_url: backendRec.image_url || '/placeholder.svg',
        rating: this.scoreToRating(hybridScore),
        reason_features: {
          ...(backendRec.reason_features || {}),
          hybrid_score: hybridScore,
          matched_tags: backendRec.reason_features?.matched_tags || [],
          cf_score: backendRec.reason_features?.cf_score || (backendRec.reason_features?.source === "collaborative" ? hybridScore : undefined),
          content_score: backendRec.reason_features?.content_score || (backendRec.reason_features?.source === "content_only" ? hybridScore : undefined),
          source: backendRec.reason_features?.source || 'unknown',
          hybrid: (backendRec.reason_features as any)?.hybrid || (backendRec.reason_features?.source?.startsWith("hybrid") || false)
        }
      };

      return product;
    } catch (error) {
      console.error('Error transforming recommendation:', error, backendRec);
      throw error;
    }
  }

  /**
   * Convert recommendation score to rating (4.0-5.0)
   */
  private scoreToRating(score: number): number {
    // Normalize score to 4.0-5.0 range
    return Math.max(4.0, Math.min(5.0, 4.0 + score));
  }
}

export const recommendationService = new RecommendationService();
export default recommendationService;
