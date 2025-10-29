/**
 * Optimized User Data Service - Uses existing user_data endpoints
 * This service leverages the optimized backend queries while preserving interaction tracking
 */

import apiClient from './api';
import { authService } from './authService';
import { Product } from '@/types/product';

export interface CartItem extends Product {
  quantity: number;
  last_added?: string;
}

export interface WishlistItem extends Product {
  added_at?: string;
}

export interface PurchaseItem extends Product {
  quantity: number;
  purchase_value: number;
  purchased_at: string;
  order_id?: string;
}

export interface UserStats {
  total_interactions: number;
  event_types: { [key: string]: number };
  platforms: { [key: string]: number };
  last_activity: string | null;
}

export interface UserData {
  cart: CartItem[];
  wishlist: WishlistItem[];
  purchases: PurchaseItem[];
  stats: UserStats | null;
}

class OptimizedUserDataService {
  /**
   * Get user's cart using optimized backend query
   * This uses the user_data endpoint which reconstructs cart from interactions
   */
  async getCartFromDB(userId: string): Promise<CartItem[]> {
    if (!userId) return [];
    try {
      const response = await apiClient.get<CartItem[]>(`/api/user-data/cart/${userId}`, undefined, {
        headers: { 'Authorization': `Bearer ${authService.getToken()}` }
      });
        items: response.length,
        totalQuantity: response.reduce((sum, item) => sum + item.quantity, 0)
      });
      return response;
    } catch (error) {
      console.error('❌ [OPTIMIZED] Failed to fetch cart from DB:', error);
      return [];
    }
  }

  /**
   * Get user's wishlist using optimized backend query
   * This uses the user_data endpoint which reconstructs wishlist from interactions
   */
  async getWishlistFromDB(userId: string): Promise<WishlistItem[]> {
    if (!userId) return [];
    try {
      const response = await apiClient.get<WishlistItem[]>(`/api/user-data/wishlist/${userId}`, undefined, {
        headers: { 'Authorization': `Bearer ${authService.getToken()}` }
      });
        items: response.length
      });
      return response;
    } catch (error) {
      console.error('❌ [OPTIMIZED] Failed to fetch wishlist from DB:', error);
      return [];
    }
  }

  /**
   * Get user's purchase history using optimized backend query
   */
  async getPurchasesFromDB(userId: string, limit: number = 50, offset: number = 0): Promise<PurchaseItem[]> {
    if (!userId) return [];
    try {
      const response = await apiClient.get<PurchaseItem[]>(`/api/user-data/purchases/${userId}`, { limit, offset }, {
        headers: { 'Authorization': `Bearer ${authService.getToken()}` }
      });
        items: response.length,
        totalValue: response.reduce((sum, item) => sum + item.purchase_value, 0)
      });
      return response;
    } catch (error) {
      console.error('❌ [OPTIMIZED] Failed to fetch purchases from DB:', error);
      return [];
    }
  }

  /**
   * Get user interaction statistics
   */
  async getUserStatsFromDB(userId: string): Promise<UserStats | null> {
    if (!userId) return null;
    try {
      const response = await apiClient.get<UserStats>(`/api/user-data/stats/${userId}`, undefined, {
        headers: { 'Authorization': `Bearer ${authService.getToken()}` }
      });
      return response;
    } catch (error) {
      console.error('❌ [OPTIMIZED] Failed to fetch user stats from DB:', error);
      return null;
    }
  }

  /**
   * Get all user data in one call
   */
  async getAllUserData(userId: string): Promise<UserData> {
    try {
      const [cart, wishlist, purchases, stats] = await Promise.all([
        this.getCartFromDB(userId),
        this.getWishlistFromDB(userId),
        this.getPurchasesFromDB(userId),
        this.getUserStatsFromDB(userId)
      ]);

      return {
        cart,
        wishlist,
        purchases,
        stats
      };
    } catch (error) {
      console.error('❌ [OPTIMIZED] Failed to fetch all user data:', error);
      return {
        cart: [],
        wishlist: [],
        purchases: [],
        stats: null
      };
    }
  }

  /**
   * Sync local storage with database
   * This ensures local state matches the database state
   */
  async syncWithDatabase(userId: string): Promise<{
    cart: CartItem[];
    wishlist: WishlistItem[];
    purchases: PurchaseItem[];
    stats: UserStats | null;
  }> {
    
    const dbData = await this.getAllUserData(userId);
    
    // Update local storage
    localStorage.setItem('userCart', JSON.stringify(dbData.cart));
    localStorage.setItem('userWishlist', JSON.stringify(dbData.wishlist));
    localStorage.setItem('userPurchases', JSON.stringify(dbData.purchases));
    localStorage.setItem('userStats', JSON.stringify(dbData.stats));
    
      cart: dbData.cart.length,
      wishlist: dbData.wishlist.length,
      purchases: dbData.purchases.length
    });
    
    return dbData;
  }
}

export const optimizedUserDataService = new OptimizedUserDataService();
export default optimizedUserDataService;
