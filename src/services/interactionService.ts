/**
 * Interaction API service for tracking user behavior
 */

import apiClient from './api';
import { authService } from './authService';

export interface InteractionData {
  product_id: string;
  event_type: 'view' | 'click' | 'add_to_cart' | 'purchase' | 'wishlist' | 'review';
  event_value?: number;
  platform?: string;
  device?: {
    type?: string;
    os?: string;
    browser?: string;
    [key: string]: any; // Allow additional fields
  };
  page?: string;
  product_name?: string;
  price?: number;
  quantity?: number;
  action?: string;
  search_query?: string;
  timestamp?: string;
  previous_quantity?: number;
  new_quantity?: number;
  cart_quantity?: number;
  unit_price?: number;
  total_item_value?: number;
  total_cart_value?: number;
  cart_items_count?: number;
  wishlist_items_count?: number;
  [key: string]: any; // Allow additional fields
}

export interface SessionData {
  user_id?: string;
  context?: Record<string, any>;
}

class InteractionService {
  /**
   * Track a product view
   */
  async trackView(productId: string, additionalData?: Partial<InteractionData>): Promise<void> {
    try {
      await this.trackSessionInteraction('view', productId, additionalData);
    } catch (error) {
      console.warn('Failed to track view:', error);
    }
  }

  /**
   * Track a product click
   */
  async trackClick(productId: string, additionalData?: Partial<InteractionData>): Promise<void> {
    try {
      await this.trackSessionInteraction('click', productId, additionalData);
    } catch (error) {
      console.warn('Failed to track click:', error);
    }
  }

  /**
   * Track add to cart
   */
  async trackAddToCart(productId: string, quantity: number = 1, additionalData?: Partial<InteractionData>): Promise<void> {
    try {
      await this.trackSessionInteraction('add_to_cart', productId, {
        ...additionalData,
        quantity
      });
    } catch (error) {
      console.warn('Failed to track add to cart:', error);
    }
  }

  /**
   * Track purchase
   */
  async trackPurchase(productId: string, value: number, additionalData?: Partial<InteractionData>): Promise<void> {
    try {
      await this.trackSessionInteraction('purchase', productId, {
        ...additionalData,
        value
      });
    } catch (error) {
      console.warn('Failed to track purchase:', error);
    }
  }

  /**
   * Track wishlist add/remove
   */
  async trackWishlist(productId: string, added: boolean = true, additionalData?: Partial<InteractionData>): Promise<void> {
    try {
      await this.trackSessionInteraction('wishlist', productId, {
        ...additionalData,
        added
      });
    } catch (error) {
      console.warn('Failed to track wishlist:', error);
    }
  }

  /**
   * Track product review/rating
   */
  async trackReview(productId: string, rating: number, reviewText?: string, additionalData?: Partial<InteractionData>): Promise<void> {
    try {
      console.log('⭐ [REVIEW] Logging review interaction:', {
        productId,
        rating,
        reviewText: reviewText?.substring(0, 50) + (reviewText && reviewText.length > 50 ? '...' : ''),
        timestamp: new Date().toISOString()
      });

      await this.trackSessionInteraction('review', productId, {
        ...additionalData,
        rating,
        reviewText,
        event_value: rating
      });
    } catch (error) {
      console.warn('Failed to track review:', error);
    }
  }

  /**
   * Track a session-based interaction using the new session tracking API
   */
  async trackSessionInteraction(eventType: string, productId?: string, additionalData?: any): Promise<void> {
    // Only track if user is authenticated
    if (!authService.isAuthenticated()) {
      // Silent return for guest users - no console warnings
      return;
    }

    try {
      // Send as query parameters instead of JSON body
      const params = new URLSearchParams();
      params.append('event_type', eventType);
      if (productId) {
        params.append('product_id', productId);
      }
      if (additionalData) {
        params.append('additional_data', JSON.stringify(additionalData));
      }

      const response = await apiClient.post(`/api/session/log-interaction?${params.toString()}`);
      
      // Console log for frontend verification
      console.log('👆 [FRONTEND_INTERACTION] User interaction logged:', {
        eventType,
        productId,
        timestamp: new Date().toISOString(),
        response: response
      });
      
    } catch (error) {
      console.error('❌ [SESSION_INTERACTION] FAILED:', {
        eventType,
        productId,
        error: error instanceof Error ? error.message : String(error),
        timestamp: new Date().toISOString()
      });
      // Don't re-throw the error to prevent UI issues
    }
  }

  /**
   * Track a generic interaction (legacy method - kept for compatibility)
   */
  async trackInteraction(data: InteractionData): Promise<void> {
    // Only track if user is authenticated
    if (!authService.isAuthenticated()) {
      console.warn('🚫 [INTERACTION] Cannot track: user not authenticated');
      return;
    }

    // Add default device/platform info
    const interactionData = {
      ...data,
      user_id: authService.getCurrentUserSync()?.user_id,
      platform: data.platform || 'web',
      device: {
        type: 'desktop', // Could be enhanced to detect mobile
        os: navigator.platform,
        browser: this.getBrowserName(),
        ...data.device
      }
    };

    try {
      const response = await apiClient.post('/api/interactions/', interactionData, {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      
    } catch (error) {
      // Log error but don't throw to avoid breaking the UI
      console.error('❌ [INTERACTION] FAILED:', {
        eventType: data.event_type,
        productId: data.product_id,
        error: error,
        timestamp: new Date().toISOString()
      });
      // Don't re-throw the error to prevent UI issues
    }
  }

  /**
   * Get user interaction history
   */
  async getUserInteractions(userId: string, limit: number = 50): Promise<any[]> {
    return apiClient.get('/api/interactions/history', {
      user_id: userId,
      limit
    });
  }

  /**
   * Get product interaction stats
   */
  async getProductStats(productId: string): Promise<any> {
    return apiClient.get(`/api/interactions/product/${productId}/stats`);
  }

  /**
   * Create or update user session
   */
  async createSession(data: SessionData): Promise<any> {
    return apiClient.post('/api/interactions/sessions/', data);
  }

  /**
   * End user session
   */
  async endSession(sessionId: string): Promise<void> {
    await apiClient.put(`/api/interactions/sessions/${sessionId}/end`);
  }

  /**
   * Get browser name from user agent
   */
  private getBrowserName(): string {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Chrome')) return 'Chrome';
    if (userAgent.includes('Firefox')) return 'Firefox';
    if (userAgent.includes('Safari')) return 'Safari';
    if (userAgent.includes('Edge')) return 'Edge';
    return 'Unknown';
  }
}

export const interactionService = new InteractionService();
export default interactionService;
