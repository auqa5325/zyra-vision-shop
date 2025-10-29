import { apiClient } from './api';

export interface Review {
  review_id: string;
  user_id: string;
  product_id: string;
  rating: number;
  title?: string;
  comment?: string;
  verified_purchase: boolean;
  helpful_count: number;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
  user?: {
    username: string;
    is_anonymous: boolean;
  };
}

export interface ReviewWithUser extends Review {
  user: {
    username: string;
    is_anonymous: boolean;
  };
  product_name?: string;
}

export interface ReviewCreate {
  product_id: string;
  rating: number;
  title?: string;
  comment?: string;
}

export interface RatingSummary {
  average_rating: number;
  total_reviews: number;
  rating_distribution: Record<number, number>;
}

export const reviewService = {
  async getProductReviews(productId: string, page = 1, limit = 10, sort = 'newest'): Promise<ReviewWithUser[]> {
    const response = await apiClient.get<ReviewWithUser[]>(`/api/reviews/product/${productId}`, {
      params: { page, limit, sort }
    });
    return response;
  },

  async getProductRatingSummary(productId: string): Promise<RatingSummary> {
    const response = await apiClient.get<RatingSummary>(`/api/reviews/product/${productId}/summary`);
    return response;
  },

  async createReview(reviewData: ReviewCreate): Promise<Review> {
    const response = await apiClient.post<Review>('/api/reviews', reviewData);
    return response;
  },

  async updateReview(reviewId: string, updates: Partial<ReviewCreate>): Promise<Review> {
    const response = await apiClient.put<Review>(`/api/reviews/${reviewId}`, updates);
    return response;
  },

  async deleteReview(reviewId: string): Promise<void> {
    await apiClient.delete(`/api/reviews/${reviewId}`);
  },

  async markHelpful(reviewId: string) {
    const response = await apiClient.post(`/api/reviews/${reviewId}/helpful`);
    return response;
  },

  async getUserReviews(userId: string, page = 1, limit = 10): Promise<ReviewWithUser[]> {
    const response = await apiClient.get<ReviewWithUser[]>(`/api/reviews/user/${userId}`, {
      params: { page, limit }
    });
    return response;
  },
};