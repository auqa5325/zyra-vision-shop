import { useQuery } from '@tanstack/react-query';
import { Product } from '../types/product';
import { productService } from '../services/productService';

/**
 * Hook to fetch products for a single category
 * This avoids the hooks-in-loop issue by requiring individual calls
 */
export function useProductsForCategory(categoryId: number, limit: number = 10) {
  return useQuery({
    queryKey: ['products', 'category', categoryId, { limit }],
    queryFn: () => productService.getProductsByCategory(categoryId, { limit }),
    enabled: !!categoryId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
