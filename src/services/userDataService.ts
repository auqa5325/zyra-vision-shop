/**
 * Simple User Data Service - Fast API calls without complex syncing
 */
import apiClient from './api';
import { authService } from './authService';

export interface UserStats {
  total_interactions: number;
  event_types: Record<string, number>;
  platforms: Record<string, number>;
  last_activity: string | null;
  totalSpent: number;
  purchases: number;
}

export interface CartItem {
  id: number;
  product_id: string;
  product_name: string;
  product_price: number;
  product_discount_percent?: number;
  quantity: number;
  added_at: string;
  updated_at: string;
  product_image: string;
}

export interface WishlistItem {
  product_id: string;
  name: string;
  price: number;
  discount_percent?: number;
  added_at: string;
  image_url: string;
}

export interface PurchaseItem {
  product_id: string;
  name: string;
  price: number;
  discount_percent?: number;
  purchase_value: number;
  purchased_at: string;
  image_url: string;
}

class UserDataService {
  private getAuthHeaders(): Record<string, string> {
    const token = authService.getToken();
    if (!token) {
      console.warn('⚠️ [USER DATA SERVICE] No token available');
      return {};
    }
    return { 'Authorization': `Bearer ${token}` };
  }

  async getUserStats(): Promise<UserStats> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      const response = await apiClient.get<UserStats>(`/api/user-data/stats/${user.user_id}`, undefined, {
        headers: this.getAuthHeaders()
      });
      
      return response;
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to fetch stats:', error);
      throw error;
    }
  }

  async getCartFromDB(): Promise<CartItem[]> {
    if (!authService.isAuthenticated()) {
      return [];
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      return [];
    }

    try {
      const response = await apiClient.get<{items: CartItem[]}>(`/api/user-states/cart/${user.user_id}`, undefined, {
        headers: this.getAuthHeaders()
      });
      
      return response.items || [];
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to fetch cart:', error);
      return [];
    }
  }

  async getWishlistFromDB(): Promise<WishlistItem[]> {
    if (!authService.isAuthenticated()) {
      return [];
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      return [];
    }

    try {
      const response = await apiClient.get<WishlistItem[]>(`/api/user-data/wishlist/${user.user_id}`, undefined, {
        headers: this.getAuthHeaders()
      });
      
      return response;
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to fetch wishlist:', error);
      return [];
    }
  }

  async getPurchaseHistoryFromDB(): Promise<PurchaseItem[]> {
    if (!authService.isAuthenticated()) {
      return [];
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      return [];
    }

    try {
      const response = await apiClient.get<{items: any[]}>(`/api/user-states/purchases/${user.user_id}`, undefined, {
        headers: this.getAuthHeaders()
      });
      
      // Transform the response to match the expected format
      const purchases: PurchaseItem[] = response.items.map(item => ({
        product_id: item.product_id,
        name: item.product_name,
        price: parseFloat(item.unit_price),
        purchase_value: parseFloat(item.total_price),
        purchased_at: item.purchased_at,
        image_url: item.product_image
      }));
      
      return purchases;
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to fetch purchases:', error);
      return [];
    }
  }

  async checkoutCart(): Promise<{message: string, purchases: number, total_value: number}> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      
      // First, get current cart items
      const cartItems = await this.getCartFromDB();
      
      if (cartItems.length === 0) {
        return { message: "Cart is empty", purchases: 0, total_value: 0 };
      }
      
      // Create order data
      const orderData = {
        items: cartItems.map(item => {
          const discountedPrice = item.product_discount_percent > 0 
            ? item.product_price * (1 - item.product_discount_percent / 100)
            : item.product_price;
          return {
            product_id: item.product_id,
            quantity: item.quantity,
            unit_price: discountedPrice,
            total_price: discountedPrice * item.quantity
          };
        }),
        payment_method: "credit_card",
        payment_status: "completed"
      };
      
      // Call the correct checkout endpoint
      const response = await apiClient.post<{order_id: string, total_amount: number}>(`/api/user-states/purchases/${user.user_id}/checkout`, orderData, {
        headers: this.getAuthHeaders()
      });
      
      
      return {
        message: "Checkout successful",
        purchases: cartItems.length,
        total_value: response.total_amount
      };
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Checkout failed:', error);
      throw error;
    }
  }

  async addToCart(productId: string, quantity: number = 1): Promise<void> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      await apiClient.post(`/api/user-states/cart/${user.user_id}/add`, {
        product_id: productId,
        quantity: quantity
      }, {
        headers: this.getAuthHeaders()
      });
      
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to add to cart:', error);
      throw error;
    }
  }

  async addToWishlist(productId: string): Promise<void> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      await apiClient.post(`/api/user-states/wishlist/${user.user_id}/add`, {
        product_id: productId
      }, {
        headers: this.getAuthHeaders()
      });
      
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to add to wishlist:', error);
      throw error;
    }
  }

  async removeFromCart(productId: string): Promise<void> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      await apiClient.delete(`/api/user-states/cart/${user.user_id}/remove/${productId}`, {
        headers: this.getAuthHeaders()
      });
      
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to remove from cart:', error);
      throw error;
    }
  }

  async updateCartQuantity(productId: string, quantity: number): Promise<void> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      
      // First, get the cart item ID from the database
      const cartItems = await this.getCartFromDB();
      const cartItem = cartItems.find(item => item.product_id === productId);
      
      if (!cartItem) {
        throw new Error('Cart item not found');
      }

      // Update quantity using the cart item ID
      await apiClient.put(
        `/api/user-states/cart/${user.user_id}/update/${cartItem.id}`,
        { quantity: quantity },
        this.getAuthHeaders()
      );

    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to update cart quantity:', error);
      throw error;
    }
  }

  async removeFromWishlist(productId: string): Promise<void> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      await apiClient.delete(`/api/user-states/wishlist/${user.user_id}/remove/${productId}`, {
        headers: this.getAuthHeaders()
      });
      
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to remove from wishlist:', error);
      throw error;
    }
  }

  async moveFromWishlistToCart(productId: string, quantity: number = 1): Promise<void> {
    if (!authService.isAuthenticated()) {
      throw new Error('User not authenticated');
    }

    const user = authService.getCurrentUserSync();
    if (!user) {
      throw new Error('User not found');
    }

    try {
      
      // First add to cart
      await this.addToCart(productId, quantity);
      
      // Then remove from wishlist
      await this.removeFromWishlist(productId);
      
    } catch (error) {
      console.error('❌ [USER DATA SERVICE] Failed to move from wishlist to cart:', error);
      throw error;
    }
  }
}

export const userDataService = new UserDataService();
export default userDataService;