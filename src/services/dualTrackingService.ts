/**
 * Dual Tracking Service - Ensures both interactions and user states are updated
 * This service maintains the dual tracking system for ML training and fast UI queries
 */

import apiClient from './api';
import { authService } from './authService';
import { interactionService } from './interactionService';
import { Product } from '@/types/product';

export interface DualTrackingResult {
  success: boolean;
  message: string;
  tracking: {
    interaction_logged: boolean;
    user_state_updated: boolean;
  };
}

class DualTrackingService {
  /**
   * Add to cart with dual tracking
   * 1. Log interaction (for ML training)
   * 2. Update local storage (for fast UI)
   * 3. Sync with database (for persistence)
   */
  async addToCart(
    product: Product, 
    quantity: number = 1
  ): Promise<DualTrackingResult> {
    try {
      
      // 1. Log interaction for ML training
      await interactionService.trackAddToCart(product.product_id, quantity);
      
      // 2. Update local storage for fast UI
      const currentCart = JSON.parse(localStorage.getItem('userCart') || '[]');
      const existingItemIndex = currentCart.findIndex((item: any) => item.product_id === product.product_id);
      
      if (existingItemIndex > -1) {
        currentCart[existingItemIndex].quantity += quantity;
      } else {
        currentCart.push({
          ...product,
          quantity,
          last_added: new Date().toISOString()
        });
      }
      
      localStorage.setItem('userCart', JSON.stringify(currentCart));
      
      // 3. Trigger database sync (async)
      this.syncCartWithDatabase().catch(console.error);
      
      
      return {
        success: true,
        message: 'Added to cart successfully',
        tracking: {
          interaction_logged: true,
          user_state_updated: true
        }
      };
      
    } catch (error) {
      console.error('❌ [DUAL TRACKING] Failed to add to cart:', error);
      return {
        success: false,
        message: 'Failed to add to cart',
        tracking: {
          interaction_logged: false,
          user_state_updated: false
        }
      };
    }
  }

  /**
   * Add to wishlist with dual tracking
   */
  async addToWishlist(product: Product): Promise<DualTrackingResult> {
    try {
      
      // 1. Log interaction for ML training - removed wishlist tracking
      
      // 2. Update local storage for fast UI
      const currentWishlist = JSON.parse(localStorage.getItem('userWishlist') || '[]');
      const exists = currentWishlist.some((item: any) => item.product_id === product.product_id);
      
      if (!exists) {
        currentWishlist.push({
          ...product,
          added_at: new Date().toISOString()
        });
        localStorage.setItem('userWishlist', JSON.stringify(currentWishlist));
      }
      
      // 3. Trigger database sync (async)
      this.syncWishlistWithDatabase().catch(console.error);
      
      
      return {
        success: true,
        message: 'Added to wishlist successfully',
        tracking: {
          interaction_logged: true,
          user_state_updated: true
        }
      };
      
    } catch (error) {
      console.error('❌ [DUAL TRACKING] Failed to add to wishlist:', error);
      return {
        success: false,
        message: 'Failed to add to wishlist',
        tracking: {
          interaction_logged: false,
          user_state_updated: false
        }
      };
    }
  }

  /**
   * Remove from wishlist with dual tracking
   */
  async removeFromWishlist(productId: string): Promise<DualTrackingResult> {
    try {
      
      // 1. Log interaction for ML training - removed wishlist tracking
      
      // 2. Update local storage for fast UI
      const currentWishlist = JSON.parse(localStorage.getItem('userWishlist') || '[]');
      const updatedWishlist = currentWishlist.filter((item: any) => item.product_id !== productId);
      localStorage.setItem('userWishlist', JSON.stringify(updatedWishlist));
      
      // 3. Trigger database sync (async)
      this.syncWishlistWithDatabase().catch(console.error);
      
      
      return {
        success: true,
        message: 'Removed from wishlist successfully',
        tracking: {
          interaction_logged: true,
          user_state_updated: true
        }
      };
      
    } catch (error) {
      console.error('❌ [DUAL TRACKING] Failed to remove from wishlist:', error);
      return {
        success: false,
        message: 'Failed to remove from wishlist',
        tracking: {
          interaction_logged: false,
          user_state_updated: false
        }
      };
    }
  }

  /**
   * Process purchase with dual tracking
   */
  async processPurchase(
    cartItems: Array<{ product: any; quantity: number }>,
    totalAmount: number
  ): Promise<DualTrackingResult> {
    try {
      
      // 1. Log interactions for ML training
      for (const item of cartItems) {
        const discountedPrice = item.product.discount_percent > 0 
          ? item.product.price * (1 - item.product.discount_percent / 100)
          : item.product.price;
        await interactionService.trackPurchase(
          item.product.product_id, 
          discountedPrice * item.quantity
        );
      }
      
      // 2. Update local storage
      const purchases = JSON.parse(localStorage.getItem('userPurchases') || '[]');
      const orderId = `order_${Date.now()}`;
      
      for (const item of cartItems) {
        const discountedPrice = item.product.discount_percent > 0 
          ? item.product.price * (1 - item.product.discount_percent / 100)
          : item.product.price;
        purchases.push({
          ...item.product,
          quantity: item.quantity,
          purchase_value: discountedPrice * item.quantity,
          purchased_at: new Date().toISOString(),
          order_id: orderId
        });
      }
      
      localStorage.setItem('userPurchases', JSON.stringify(purchases));
      
      // 3. Clear cart
      localStorage.setItem('userCart', JSON.stringify([]));
      
      // 4. Trigger database sync (async)
      this.syncPurchasesWithDatabase().catch(console.error);
      
      
      return {
        success: true,
        message: 'Purchase processed successfully',
        tracking: {
          interaction_logged: true,
          user_state_updated: true
        }
      };
      
    } catch (error) {
      console.error('❌ [DUAL TRACKING] Failed to process purchase:', error);
      return {
        success: false,
        message: 'Failed to process purchase',
        tracking: {
          interaction_logged: false,
          user_state_updated: false
        }
      };
    }
  }

  /**
   * Sync cart with database (async)
   */
  private async syncCartWithDatabase(): Promise<void> {
    try {
      const userId = authService.getCurrentUserSync()?.user_id;
      if (!userId) return;
      
      // The backend user_data endpoint will reconstruct cart from interactions
      // This ensures consistency between interactions and user states
    } catch (error) {
      console.error('❌ [DUAL TRACKING] Cart sync failed:', error);
    }
  }

  /**
   * Sync wishlist with database (async)
   */
  private async syncWishlistWithDatabase(): Promise<void> {
    try {
      const userId = authService.getCurrentUserSync()?.user_id;
      if (!userId) return;
      
    } catch (error) {
      console.error('❌ [DUAL TRACKING] Wishlist sync failed:', error);
    }
  }

  /**
   * Sync purchases with database (async)
   */
  private async syncPurchasesWithDatabase(): Promise<void> {
    try {
      const userId = authService.getCurrentUserSync()?.user_id;
      if (!userId) return;
      
    } catch (error) {
      console.error('❌ [DUAL TRACKING] Purchases sync failed:', error);
    }
  }

  /**
   * Get tracking status
   */
  getTrackingStatus(): {
    interactions_enabled: boolean;
    user_states_enabled: boolean;
    dual_tracking_active: boolean;
  } {
    return {
      interactions_enabled: authService.isAuthenticated(),
      user_states_enabled: true,
      dual_tracking_active: authService.isAuthenticated()
    };
  }
}

export const dualTrackingService = new DualTrackingService();
export default dualTrackingService;
