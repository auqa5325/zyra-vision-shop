/**
 * Custom hooks for recommendation data fetching with React Query
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { Product, RecommendationParams } from '../types/api';
import { recommendationService } from '../services/recommendationService';

// Query keys
export const recommendationKeys = {
  all: ['recommendations'] as const,
  topPick: () => [...recommendationKeys.all, 'topPick'] as const,
  hybrid: (params: RecommendationParams) => [...recommendationKeys.all, 'hybrid', params] as const,
  personalized: (userId: string, k: number) => [...recommendationKeys.all, 'personalized', userId, k] as const,
  similar: (productId: string, k: number) => [...recommendationKeys.all, 'similar', productId, k] as const,
  collaborative: (userId: string, k: number) => [...recommendationKeys.all, 'collaborative', userId, k] as const,
};

/**
 * Hook to fetch top pick recommendation for homepage
 */
export function useTopPick(): UseQueryResult<Product | null, Error> {
  return useQuery({
    queryKey: recommendationKeys.topPick(),
    queryFn: () => recommendationService.getTopPick(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1, // Don't retry too much for top pick
  });
}

/**
 * Hook to fetch hybrid recommendations
 */
export function useRecommendations(params: RecommendationParams = {}): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: recommendationKeys.hybrid(params),
    queryFn: () => recommendationService.getRecommendations(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch personalized recommendations for logged-in user
 */
export function usePersonalizedRecommendations(
  userId: string, 
  k: number = 10
): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: recommendationKeys.personalized(userId, k),
    queryFn: () => recommendationService.getPersonalizedRecommendations(userId, k),
    enabled: !!userId,
    staleTime: 3 * 60 * 1000, // 3 minutes
  });
}

/**
 * Hook to fetch similar products for a given product
 */
export function useSimilarProducts(
  productId: string, 
  k: number = 10
): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: recommendationKeys.similar(productId, k),
    queryFn: () => recommendationService.getSimilarProducts(productId, k),
    enabled: !!productId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch collaborative filtering recommendations
 */
export function useCollaborativeRecommendations(
  userId: string, 
  k: number = 10
): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: recommendationKeys.collaborative(userId, k),
    queryFn: () => recommendationService.getCollaborativeRecommendations(userId, k),
    enabled: !!userId,
    staleTime: 3 * 60 * 1000, // 3 minutes
  });
}

/**
 * Hook to fetch top sellers (most purchased products) for non-logged-in users
 */
export function useTopSellers(k: number = 10): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: [...recommendationKeys.all, 'top-sellers', k] as const,
    queryFn: () => recommendationService.getTopSellers(k),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch content-based recommendations using aggregated user data
 */
export function useContentBasedRecommendations(
  userId: string, 
  k: number = 10
): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: [...recommendationKeys.all, 'content-based', userId, k] as const,
    queryFn: () => recommendationService.getContentBasedRecommendations(userId, k),
    enabled: !!userId,
    staleTime: 3 * 60 * 1000, // 3 minutes
  });
}

/**
 * Hook to fetch user-item similarity score
 */
export function useUserItemSimilarity(
  userId: string | null,
  productId: string
): UseQueryResult<number, Error> {
  return useQuery({
    queryKey: [...recommendationKeys.all, 'user-item-similarity', userId, productId] as const,
    queryFn: () => recommendationService.getUserItemSimilarity(userId!, productId),
    enabled: !!userId && !!productId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch hybrid recommendations for a product page ("You may also like")
 */
export function useProductYouMayAlsoLike(
  productId: string | null,
  userId: string | null,
  k: number = 8
): UseQueryResult<Product[], Error> {
  return useQuery({
    queryKey: [...recommendationKeys.all, 'product-you-may-also-like', productId, userId, k] as const,
    queryFn: () => recommendationService.getProductYouMayAlsoLike(productId!, userId, k),
    enabled: !!productId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
