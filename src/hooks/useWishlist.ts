/**
 * Wishlist management hook - Syncs with database on login
 */
import { useState, useEffect } from 'react';
import { Product } from '@/types/product';
import { userDataService } from '@/services/userDataService';
import { useAuth } from '@/contexts/AuthContext';

export interface WishlistItem extends Product {
  added_at: string;
}

export const useWishlist = () => {
  const { isAuthenticated } = useAuth();
  const [wishlist, setWishlist] = useState<WishlistItem[]>([]);

  // Load wishlist from localStorage on mount
  useEffect(() => {
    const savedWishlist = localStorage.getItem('wishlist');
    if (savedWishlist) {
      try {
        const parsedWishlist = JSON.parse(savedWishlist);
        setWishlist(parsedWishlist);
      } catch (error) {
        console.error('Error loading wishlist from localStorage:', error);
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
      const dbWishlist = await userDataService.getWishlistFromDB();
      
      // Convert database format to local format
      const wishlistItems: WishlistItem[] = dbWishlist.map(item => ({
        product_id: item.product_id,
        name: item.name,
        description: item.name, // Use name as description for now
        price: item.price,
        discount_percent: item.discount_percent || 0,
        image_url: item.image_url,
        rating: 0, // Default rating
        category: 'General',
        category_id: 0,
        added_at: item.added_at
      }));

      setWishlist(wishlistItems);
      localStorage.setItem('wishlist', JSON.stringify(wishlistItems));
      
    } catch (error) {
      console.error('❌ [WISHLIST] Failed to sync with database:', error);
    }
  };

  // Listen for logout events to clear wishlist
  useEffect(() => {
    const handleLogout = () => {
      clearWishlist();
    };

    window.addEventListener('userLoggedOut', handleLogout);
    return () => window.removeEventListener('userLoggedOut', handleLogout);
  }, []);

  const addToWishlist = async (product: Omit<WishlistItem, 'added_at'>) => {
    
    if (isAuthenticated) {
      try {
        // Add to database first
        await userDataService.addToWishlist(product.product_id);
        
        // Immediately sync with database to get updated state
        await syncWithDatabase();
        
        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('wishlistUpdated'));
        
      } catch (error) {
        console.error('❌ [WISHLIST] Failed to add to wishlist:', error);
        // Still update local state for better UX
        updateLocalWishlist(product, true);
      }
    } else {
      // User not authenticated - just update local storage
      updateLocalWishlist(product, true);
    }
  };

  const updateLocalWishlist = (product: Omit<WishlistItem, 'added_at'>, add: boolean) => {
    if (add) {
      const wishlistItem: WishlistItem = {
        ...product,
        added_at: new Date().toISOString()
      };

      setWishlist(prevWishlist => {
        const exists = prevWishlist.some(item => item.product_id === product.product_id);
        if (exists) {
          return prevWishlist;
        }

        const newWishlist = [...prevWishlist, wishlistItem];
        localStorage.setItem('wishlist', JSON.stringify(newWishlist));
        window.dispatchEvent(new CustomEvent('wishlistUpdated'));
        return newWishlist;
      });
    } else {
      setWishlist(prevWishlist => {
        const newWishlist = prevWishlist.filter(item => item.product_id !== product.product_id);
        localStorage.setItem('wishlist', JSON.stringify(newWishlist));
        window.dispatchEvent(new CustomEvent('wishlistUpdated'));
        return newWishlist;
      });
    }
  };

  const removeFromWishlist = async (productId: string) => {
    
    if (isAuthenticated) {
      try {
        // Remove from database first
        await userDataService.removeFromWishlist(productId);
        
        // Immediately sync with database to get updated state
        await syncWithDatabase();
        
        // Dispatch custom event to notify other components
        window.dispatchEvent(new CustomEvent('wishlistUpdated'));
        
      } catch (error) {
        console.error('❌ [WISHLIST] Failed to remove from wishlist:', error);
        // Still update local state for better UX
        updateLocalWishlist({ product_id: productId } as any, false);
      }
    } else {
      // User not authenticated - just update local storage
      updateLocalWishlist({ product_id: productId } as any, false);
    }
  };

  const moveToCart = async (product: Omit<WishlistItem, 'added_at'>, quantity: number = 1) => {
    
    try {
      // Move from wishlist to cart in database
      await userDataService.moveFromWishlistToCart(product.product_id, quantity);
      
      // Immediately sync both wishlist and cart with database
      await syncWithDatabase();
      
      // Dispatch custom events to notify other components
      window.dispatchEvent(new CustomEvent('wishlistUpdated'));
      window.dispatchEvent(new CustomEvent('cartUpdated'));
      
    } catch (error) {
      console.error('❌ [WISHLIST] Failed to move to cart:', error);
      // Still update local state for better UX
      setWishlist(prevWishlist => 
        prevWishlist.filter(item => item.product_id !== product.product_id)
      );
    }
  };

  const toggleWishlist = (product: Omit<WishlistItem, 'added_at'>) => {
    const isInWishlist = wishlist.some(item => item.product_id === product.product_id);
    
    if (isInWishlist) {
      removeFromWishlist(product.product_id);
    } else {
      addToWishlist(product);
    }
  };

  const isInWishlist = (productId: string): boolean => {
    return wishlist.some(item => item.product_id === productId);
  };

  const clearWishlist = () => {
    setWishlist([]);
  };

  const refreshWishlist = async () => {
    if (isAuthenticated) {
      await syncWithDatabase();
    } else {
      // For guest users, just reload from localStorage
      const savedWishlist = localStorage.getItem('wishlist');
      if (savedWishlist) {
        try {
          const parsedWishlist = JSON.parse(savedWishlist);
          setWishlist(parsedWishlist);
        } catch (error) {
          console.error('Error loading wishlist from localStorage:', error);
        }
      }
    }
  };

  return {
    wishlist,
    addToWishlist,
    removeFromWishlist,
    moveToCart,
    toggleWishlist,
    isInWishlist,
    clearWishlist,
    refreshWishlist
  };
};