import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { productService } from '@/services/productService';
import { Product } from '@/types/product';

interface SearchSuggestion {
  type: 'product' | 'category' | 'brand';
  text: string;
  product?: Product;
  categoryId?: number;
  brand?: string;
}

interface UseSearchSuggestionsProps {
  query: string;
  enabled?: boolean;
  debounceMs?: number;
}

export function useSearchSuggestions({ 
  query, 
  enabled = true, 
  debounceMs = 300 
}: UseSearchSuggestionsProps) {
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  // Debounce the query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs]);

  // Fetch suggestions
  const { data: suggestions = [], isLoading, error } = useQuery({
    queryKey: ['search-suggestions', debouncedQuery],
    queryFn: async (): Promise<SearchSuggestion[]> => {
      if (!debouncedQuery.trim() || debouncedQuery.length < 2) {
        return [];
      }

      try {
        // Get product search results
        const products = await productService.searchProducts(debouncedQuery, 5);
        
        const suggestions: SearchSuggestion[] = [];
        
        // Add product suggestions
        products.forEach(product => {
          suggestions.push({
            type: 'product',
            text: product.name,
            product
          });
        });

        // Add category suggestions based on products found
        const categories = new Set<string>();
        products.forEach(product => {
          if (product.category) {
            categories.add(product.category);
          }
        });

        categories.forEach(category => {
          suggestions.push({
            type: 'category',
            text: category,
            categoryId: undefined // We'll need to find the category ID differently
          });
        });

        // Add brand suggestions
        const brands = new Set<string>();
        products.forEach(product => {
          // Extract brand from product name or use a simple heuristic
          const words = product.name.split(' ');
          if (words.length > 1) {
            brands.add(words[0]); // First word is often the brand
          }
        });

        brands.forEach(brand => {
          suggestions.push({
            type: 'brand',
            text: brand,
            brand
          });
        });

        return suggestions.slice(0, 8); // Limit to 8 suggestions
      } catch (error) {
        console.error('Error fetching search suggestions:', error);
        return [];
      }
    },
    enabled: enabled && debouncedQuery.trim().length >= 2,
    staleTime: 30 * 1000, // 30 seconds
  });

  return {
    suggestions,
    isLoading,
    error,
    hasSuggestions: suggestions.length > 0
  };
}
