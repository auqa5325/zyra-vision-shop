/**
 * Custom hooks for product data fetching with React Query
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { Product, ProductListParams, SearchParams, CategoryHierarchy, Category } from '../types/api';
import { productService } from '../services/productService';

// Query keys
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (params: ProductListParams) => [...productKeys.lists(), params] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (id: string) => [...productKeys.details(), id] as const,
  categories: () => [...productKeys.all, 'categories'] as const,
  search: (params: SearchParams) => [...productKeys.all, 'search', params] as const,
};

/**
 * Hook to fetch products with optional filters
 */
export function useProducts(params: ProductListParams = {}): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: productKeys.list(params),
    queryFn: () => productService.getProducts(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch a single product by ID
 */
export function useProduct(productId: string): UseQueryResult<Product, Error> {
  return useQuery({
    queryKey: productKeys.detail(productId),
    queryFn: () => productService.getProductById(productId),
    enabled: !!productId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch categories with hierarchical structure
 */
export function useCategoriesHierarchy(): UseQueryResult<CategoryHierarchy[], Error> {
  return useQuery({
    queryKey: [...productKeys.categories(), 'hierarchy'],
    queryFn: () => productService.getCategoriesHierarchy(),
    staleTime: 10 * 60 * 1000, // 10 minutes - categories don't change often
  });
}

/**
 * Hook to fetch all categories
 */
export function useCategories(): UseQueryResult<Category[], Error> {
  return useQuery({
    queryKey: productKeys.categories(),
    queryFn: () => productService.getCategories(),
    staleTime: 10 * 60 * 1000, // 10 minutes - categories don't change often
  });
}

/**
 * Hook to search products
 */
export function useProductSearch(params: SearchParams): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: productKeys.search(params),
    queryFn: () => productService.searchProducts(params.query, params.k),
    enabled: !!params.query && params.query.length > 0,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

/**
 * Hook to fetch products by category
 */
export function useProductsByCategory(
  categoryId: number, 
  params: Omit<ProductListParams, 'category_id'> = {}
): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: productKeys.list({ ...params, category_id: categoryId }),
    queryFn: () => productService.getProductsByCategory(categoryId, params),
    enabled: !!categoryId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}
