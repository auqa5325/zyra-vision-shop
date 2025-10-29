/**
 * Cart management hook - Syncs with database on login
 */
import { useState, useEffect } from 'react';
import { Product } from '@/types/product';
import { userDataService } from '@/services/userDataService';
import { useAuth } from '@/contexts/AuthContext';

export interface CartItem extends Product {
  quantity: number;
  last_added?: string;
}

export interface CartState {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
}

export const useCart = () => {
  const { isAuthenticated } = useAuth();
  const [cart, setCart] = useState<CartState>({
    items: [],
    totalItems: 0,
    totalPrice: 0
  });

  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        setCart(parsedCart);
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
      }
    }
  }, []);

  // Sync with database when user logs in
  useEffect(() => {
    if (isAuthenticated) {
      syncWithDatabase();
    }
  }, [isAuthenticated]);

  const syncWithDatabase = async () => {
    try {
      const dbCart = await userDataService.getCartFromDB();
      
      // Convert database format to local format
      const cartItems: CartItem[] = dbCart.map(item => ({
        product_id: item.product_id,
        name: item.product_name,
        description: item.product_name, // Use name as description for now
        price: item.product_price,
        discount_percent: item.product_discount_percent || 0,
        image_url: item.product_image,
        rating: 0, // Default rating
        category: 'General',
        category_id: 0,
        quantity: item.quantity,
        last_added: item.added_at
      }));

      const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = cartItems.reduce((sum, item) => {
        const discountedPrice = item.discount_percent > 0 
          ? item.price * (1 - item.discount_percent / 100)
          : item.price;
        return sum + (discountedPrice * item.quantity);
      }, 0);

      const newCart = {
        items: cartItems,
        totalItems,
        totalPrice
      };

      setCart(newCart);
      localStorage.setItem('cart', JSON.stringify(newCart));
      
    } catch (error) {
      console.error('❌ [CART] Failed to sync with database:', error);
    }
  };

  // Listen for logout events to clear cart
  useEffect(() => {
    const handleLogout = () => {
      clearCart();
    };

    window.addEventListener('userLoggedOut', handleLogout);
    return () => window.removeEventListener('userLoggedOut', handleLogout);
  }, []);

  const addToCart = async (product: Omit<CartItem, 'quantity'>, quantity: number = 1) => {
    
    if (isAuthenticated) {
      try {
        // Add to database first
        await userDataService.addToCart(product.product_id, quantity);
        
        // Immediately sync with database to get updated state
        await syncWithDatabase();
        
        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('cartUpdated'));
        
      } catch (error) {
        console.error('❌ [CART] Failed to add to cart:', error);
        // Still update local state for better UX
        updateLocalCart(product, quantity);
      }
    } else {
      // User not authenticated - just update local storage
      updateLocalCart(product, quantity);
    }
  };

  const updateLocalCart = (product: Omit<CartItem, 'quantity'>, quantity: number) => {
    setCart(prevCart => {
      const existingItem = prevCart.items.find(item => item.product_id === product.product_id);
      
      let newItems: CartItem[];
      if (existingItem) {
        newItems = prevCart.items.map(item =>
          item.product_id === product.product_id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        newItems = [...prevCart.items, { ...product, quantity, last_added: new Date().toISOString() }];
      }

      const totalItems = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

      const newCart = {
        items: newItems,
        totalItems,
        totalPrice
      };

      // Save to localStorage
      localStorage.setItem('cart', JSON.stringify(newCart));
      
      // Dispatch custom event to notify other components
      window.dispatchEvent(new CustomEvent('cartUpdated'));
      
      return newCart;
    });
  };

  const removeFromCart = async (productId: string) => {
    
    if (isAuthenticated) {
      try {
        // Remove from database first
        await userDataService.removeFromCart(productId);
        
        // Immediately sync with database to get updated state
        await syncWithDatabase();
        
        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('cartUpdated'));
        
      } catch (error) {
        console.error('❌ [CART] Failed to remove from cart:', error);
        // Still update local state for better UX
        updateLocalCartRemove(productId);
      }
    } else {
      // User not authenticated - just update local storage
      updateLocalCartRemove(productId);
    }
  };

  const updateLocalCartRemove = (productId: string) => {
    setCart(prevCart => {
      const newItems = prevCart.items.filter(item => item.product_id !== productId);
      const totalItems = newItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = newItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

      const newCart = {
        items: newItems,
        totalItems,
        totalPrice
      };

      // Save to localStorage
      localStorage.setItem('cart', JSON.stringify(newCart));
      
      // Dispatch custom event to notify other components
      window.dispatchEvent(new CustomEvent('cartUpdated'));
      
      return newCart;
    });
  };

  const updateQuantity = async (productId: string, quantity: number) => {
    
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    try {
      // Update in database first
      await userDataService.updateCartQuantity(productId, quantity);
      
      // Immediately sync with database to get updated state
      await syncWithDatabase();
      
      // Dispatch custom event to notify other components
      window.dispatchEvent(new CustomEvent('cartUpdated'));
      
    } catch (error) {
      console.error('❌ [CART] Failed to update quantity:', error);
      // Still update local state for better UX
      setCart(prevCart => {
        const newItems = prevCart.items.map(item =>
          item.product_id === productId
            ? { ...item, quantity }
            : item
        );

        const totalItems = newItems.reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = newItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        return {
          items: newItems,
          totalItems,
          totalPrice
        };
      });
    }
  };

  const clearCart = () => {
    setCart({
      items: [],
      totalItems: 0,
      totalPrice: 0
    });
  };

  const checkout = async () => {
    
    try {
      // Call backend checkout API
      const result = await userDataService.checkoutCart();
      
      // Clear local cart
      clearCart();
      
      // Show success message
      const totalValue = typeof result.total_value === 'number' ? result.total_value : parseFloat(result.total_value) || 0;
      alert(`Checkout successful! Purchased ${result.purchases} items worth ₹${totalValue.toFixed(2)}. Thank you for your purchase!`);
      
    } catch (error) {
      console.error('❌ [CART] Checkout failed:', error);
      alert('Checkout failed. Please try again.');
    }
  };

  const refreshCart = async () => {
    if (isAuthenticated) {
      await syncWithDatabase();
    } else {
      // For guest users, just reload from localStorage
      const savedCart = localStorage.getItem('cart');
      if (savedCart) {
        try {
          const parsedCart = JSON.parse(savedCart);
          setCart(parsedCart);
        } catch (error) {
          console.error('Error loading cart from localStorage:', error);
        }
      }
    }
  };

  return {
    cart,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    checkout,
    refreshCart
  };
};