import { useState, useEffect, useMemo } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ProductCard } from "@/components/ProductCard";
import { SearchInput } from "@/components/SearchInput";
import { FilterModal, FilterOptions, SortOptions } from "@/components/FilterModal";
import { SortModal } from "@/components/SortModal";
import { Button } from "@/components/ui/button";
import { Search, ArrowLeft, Filter } from "lucide-react";
import { useProductSearch } from "@/hooks/useProducts";
import { Product } from "@/types/product";
import { interactionService } from "@/services/interactionService";

const SearchResults = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [currentQuery, setCurrentQuery] = useState("");

  // Get search query from URL
  const query = searchParams.get("q") || "";

  // Fetch search results
  const { data: searchResults = [], isLoading, error } = useProductSearch({
    query,
    k: 50 // Get more results for search page
  });

  // Filter and sort state
  const [filters, setFilters] = useState<FilterOptions>({
    priceRange: [0, 200000],
    brands: [],
    subcategories: [],
    minRating: 0,
    inStock: false,
    discountRange: [0, 100],
    hasDiscount: false,
  });

  // Track if user has manually changed price range
  const [userModifiedPriceRange, setUserModifiedPriceRange] = useState(false);


  const [sortOptions, setSortOptions] = useState<SortOptions>({
    field: 'name',
    direction: 'asc',
  });

  // Update local state when URL changes
  useEffect(() => {
    setSearchQuery(query);
    setCurrentQuery(query);
    setUserModifiedPriceRange(false); // Reset price range modification flag for new search
  }, [query]);

  // Calculate dynamic filter options from search results
  const filterOptions = useMemo(() => {
    
    if (!searchResults.length) {
      return {
        availableBrands: [],
        availableSubcategories: [],
        priceRange: [0, 200000] as [number, number],
      };
    }

    // Get unique brands from search results
    const brands = Array.from(new Set(
      searchResults
        .map(product => product.brand)
        .filter(Boolean)
    )).sort();

    // Get unique categories from search results
    const categories = Array.from(new Set(
      searchResults
        .map(product => product.category_id)
        .filter(Boolean)
    )).map(id => ({
      id: id!,
      name: searchResults.find(p => p.category_id === id)?.category || 'Unknown'
    }));

    // Calculate price range from search results
    const prices = searchResults.map(p => p.price).filter(p => p > 0);
    const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
    const maxPrice = prices.length > 0 ? Math.max(...prices) : 200000;

    const options = {
      availableBrands: brands,
      availableSubcategories: categories,
      priceRange: [minPrice, maxPrice] as [number, number],
    };
    
    return options;
  }, [searchResults]);

  // Update filters when search results change (to update price range)
  useEffect(() => {
    // Only update price range if user hasn't manually modified it
    if (!userModifiedPriceRange && (filterOptions.priceRange[0] !== filters.priceRange[0] || filterOptions.priceRange[1] !== filters.priceRange[1])) {
      setFilters(prev => ({
        ...prev,
        priceRange: filterOptions.priceRange
      }));
    }
  }, [filterOptions.priceRange, filters.priceRange, userModifiedPriceRange]);

  // Apply filters and sorting to search results
  const filteredAndSortedResults = useMemo(() => {

    const filtered = searchResults.filter(product => {
        // Price range filter - show products from min price up to max slider value
        if (product.price > filters.priceRange[1]) {
          return false;
        }

        // Brand filter
        if (filters.brands && filters.brands.length > 0) {
          if (!product.brand || !filters.brands.includes(product.brand)) {
            return false;
          }
        }

        // Category filter
        if (filters.subcategories && filters.subcategories.length > 0) {
          if (!product.category_id || !filters.subcategories.includes(product.category_id)) {
            return false;
          }
        }

        // Rating filter
        if (filters.minRating > 0) {
          const productRating = product.average_rating ?? product.rating ?? 0; // Use average_rating first, fallback to rating
          if (productRating < filters.minRating) {
            return false;
          }
        }

        // Discount range filter
        const productDiscount = product.discount_percent || 0;
        if (productDiscount < filters.discountRange[0] || productDiscount > filters.discountRange[1]) {
          return false;
        }

        // Has discount filter
        if (filters.hasDiscount && productDiscount === 0) {
          return false;
        }

        // In stock filter (assuming all products are available if they're returned from API)
        if (filters.inStock) {
          // This would need to be implemented based on your product model
          // For now, we'll assume all products are in stock
        }

        return true;
      });

    return filtered
      .sort((a, b) => {
        let comparison = 0;
        
        switch (sortOptions.field) {
          case 'name':
            comparison = a.name.localeCompare(b.name);
            break;
          case 'price':
            comparison = a.price - b.price;
            break;
          case 'rating':
            comparison = ((a.average_rating ?? a.rating) || 0) - ((b.average_rating ?? b.rating) || 0);
            break;
          case 'created_at':
            comparison = new Date(a.product_id).getTime() - new Date(b.product_id).getTime();
            break;
          case 'discount_percent':
            comparison = (a.discount_percent || 0) - (b.discount_percent || 0);
            break;
          case 'discounted_price': {
            const aDiscountedPrice = a.discount_percent ? a.price * (1 - a.discount_percent / 100) : a.price;
            const bDiscountedPrice = b.discount_percent ? b.price * (1 - b.discount_percent / 100) : b.price;
            comparison = aDiscountedPrice - bDiscountedPrice;
            break;
          }
          default:
            comparison = 0;
        }
        
        return sortOptions.direction === 'asc' ? comparison : -comparison;
      });
  }, [searchResults, filters, sortOptions]);


  // Filter handlers
  const applyFilters = (newFilters: FilterOptions) => {
    
    // Check if user modified price range
    const priceRangeChanged = newFilters.priceRange[0] !== filters.priceRange[0] || newFilters.priceRange[1] !== filters.priceRange[1];
    if (priceRangeChanged) {
      setUserModifiedPriceRange(true);
    }
    
    setFilters(newFilters);
  };

  const clearFilters = () => {
    setUserModifiedPriceRange(false);
    
    const defaultFilters: FilterOptions = {
      priceRange: filterOptions.priceRange,
      brands: [],
      subcategories: [],
      minRating: 0,
      inStock: false,
      discountRange: [0, 100],
      hasDiscount: false,
    };
    setFilters(defaultFilters);
  };

  const applySort = (newSort: SortOptions) => {
    setSortOptions(newSort);
  };


  const handleBackToHome = () => {
    navigate("/");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Searching products...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-destructive mb-4">Failed to search products</p>
            <p className="text-muted-foreground text-sm">{error.message}</p>
            <Button onClick={handleBackToHome} className="mt-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1">
        <div className="container px-4 py-8">
          {/* Search Header */}
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-6">
              <Button 
                variant="ghost" 
                onClick={handleBackToHome}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Home
              </Button>
            </div>

            {/* Search Bar */}
            <div className="max-w-2xl">
              <SearchInput
                placeholder="Search products..."
                className="w-full"
                initialValue={searchQuery}
                onSearch={(query) => {
                  setSearchQuery(query);
                  setSearchParams({ q: query });
                  setCurrentQuery(query);
                  
                  // Track search interaction
                  interactionService.trackSessionInteraction('search', undefined, {
                    search_query: query,
                    page: 'search_results',
                    timestamp: new Date().toISOString()
                  });
                }}
                showSubmitButton={false}
              />
            </div>

            {/* Search Results Info and Controls */}
            {currentQuery && (
              <div className="mt-4">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
                  {/* Search Results Info */}
                  <div className="flex-1">
                    <h1 className="text-2xl font-bold text-foreground">
                      Search Results for "{currentQuery}"
                    </h1>
                    <p className="text-muted-foreground mt-2">
                      {filteredAndSortedResults.length} of {searchResults.length} product{searchResults.length !== 1 ? 's' : ''} found
                    </p>
                  </div>

                  {/* Filter and Sort Controls */}
                  {searchResults.length > 0 && (
                    <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
                      <FilterModal
                        onApplyFilters={applyFilters}
                        onClearFilters={clearFilters}
                        currentFilters={filters}
                        productCount={filteredAndSortedResults.length}
                        availableBrands={filterOptions.availableBrands}
                        availableSubcategories={filterOptions.availableSubcategories}
                        priceRange={filterOptions.priceRange}
                      />
                      <SortModal
                        onApplySort={applySort}
                        currentSort={sortOptions}
                        productCount={filteredAndSortedResults.length}
                      />
                    </div>
                  )}
                </div>
                
                {/* Active Filters Display */}
                {(filters.brands.length > 0 || filters.subcategories.length > 0 || filters.minRating > 0 || filters.inStock) && (
                  <div className="flex flex-wrap gap-2 mb-6">
                    {filters.brands.map(brand => (
                      <span key={brand} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary/10 text-primary">
                        {brand}
                      </span>
                    ))}
                    {filters.subcategories.map(categoryId => {
                      const category = filterOptions.availableSubcategories.find(c => c.id === categoryId);
                      return (
                        <span key={categoryId} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary/10 text-primary">
                          {category?.name || 'Unknown'}
                        </span>
                      );
                    })}
                    {filters.minRating > 0 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary/10 text-primary">
                        {filters.minRating}+ ⭐
                      </span>
                    )}
                    {filters.inStock && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary/10 text-primary">
                        In Stock
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Search Results */}
          {!currentQuery ? (
            <div className="text-center py-12">
              <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-foreground mb-2">
                Start searching for products
              </h2>
              <p className="text-muted-foreground">
                Enter a search term above to find products
              </p>
            </div>
          ) : searchResults.length === 0 ? (
            <div className="text-center py-12">
              <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-foreground mb-2">
                No products found
              </h2>
              <p className="text-muted-foreground mb-4">
                Try searching with different keywords or check your spelling
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                <Button 
                  variant="outline" 
                  onClick={() => setSearchQuery("electronics")}
                >
                  Try "electronics"
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setSearchQuery("clothing")}
                >
                  Try "clothing"
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setSearchQuery("accessories")}
                >
                  Try "accessories"
                </Button>
              </div>
            </div>
          ) : filteredAndSortedResults.length === 0 ? (
            <div className="text-center py-12">
              <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-foreground mb-2">
                No products match your filters
              </h2>
              <p className="text-muted-foreground mb-4">
                Try adjusting your filters or clearing them to see more results
              </p>
              <Button 
                variant="outline" 
                onClick={clearFilters}
                className="mt-4"
              >
                Clear Filters
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredAndSortedResults.map((product: Product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          )}

        </div>
      </main>

      <Footer />
    </div>
  );
};

export default SearchResults;
