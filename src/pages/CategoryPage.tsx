import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect, useMemo } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ProductCard } from "@/components/ProductCard";
import { SubcategorySection } from "@/components/SubcategorySection";
import { FilterModal, FilterOptions, SortOptions } from "@/components/FilterModal";
import { SortModal } from "@/components/SortModal";
import { Product } from "@/types/product";
import { ArrowLeft, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useProductsByCategory, useCategoriesHierarchy } from "@/hooks/useProducts";
import { CategoryHierarchy } from "@/types/api";

const CategoryPage = () => {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  
  // Convert categoryId to number for API call
  const categoryIdNum = categoryId ? parseInt(categoryId) : undefined;
  
  const [sortOptions, setSortOptions] = useState<SortOptions>({
    field: 'name',
    direction: 'asc',
  });
  
  const { data: categoryProducts = [], isLoading, error } = useProductsByCategory(categoryIdNum || 0, { limit: 500 });
  const { data: categoriesHierarchy = [] } = useCategoriesHierarchy();
  
  // Find category info from hierarchy
  const findCategoryInHierarchy = (hierarchy: CategoryHierarchy[], id: number): CategoryHierarchy | null => {
    for (const category of hierarchy) {
      if (category.category_id === id) return category;
      const found = findCategoryInHierarchy(category.children, id);
      if (found) return found;
    }
    return null;
  };
  
  const category = findCategoryInHierarchy(categoriesHierarchy, categoryIdNum || 0);
  const categoryName = category?.name || categoryId || 'Unknown Category';
  const isParentCategory = category?.children && category.children.length > 0;
  
  // Fetch all subcategory products using a single API call
  // This avoids the hooks-in-loop issue by using a single query
  const { data: allSubcategoryProducts = [], isLoading: isLoadingSubcategoryProducts } = useProductsByCategory(
    categoryIdNum || 0, 
    { limit: 500 } // Maximum allowed by backend API
  );
  
  // Group products by subcategory
  const subcategoryProductsMap = category?.children?.reduce((acc, subcategory) => {
    const subcategoryProducts = allSubcategoryProducts.filter(product => 
      product.category_id === subcategory.category_id
    ).slice(0, 10); // Limit to 10 products per subcategory
    acc[subcategory.category_id] = subcategoryProducts;
    return acc;
  }, {} as Record<number, Product[]>) || {};

  // Calculate dynamic filter options
  // Get actual brands from current subcategory products only (not parent category)
  const availableBrands = !isParentCategory && categoryProducts.length > 0 ? Array.from(new Set(
    categoryProducts
      .map(product => product.brand)  // ✅ Use actual brand field from database
      .filter(Boolean)  // Remove null/undefined brands
  )).sort() : [];

  // Get available subcategories for parent categories
  const availableSubcategories = isParentCategory && category?.children 
    ? category.children.map(child => ({ id: child.category_id, name: child.name }))
    : [];

  // Calculate price range first - only for subcategory pages
  const priceRange: [number, number] = useMemo(() => {
    return !isParentCategory && categoryProducts.length > 0 
      ? [
          Math.floor(Math.min(...categoryProducts.map(p => p.price))),
          Math.ceil(Math.max(...categoryProducts.map(p => p.price)))
        ]
      : [0, 1000];
  }, [isParentCategory, categoryProducts]);

  // Track if user has manually changed price range
  const [userModifiedPriceRange, setUserModifiedPriceRange] = useState(false);

  // Initialize filters with dynamic price range
  const [filters, setFilters] = useState<FilterOptions>(() => ({
    priceRange: priceRange,
    brands: [],
    subcategories: [],
    minRating: 0,
    inStock: false,
    discountRange: [0, 100],
    hasDiscount: false,
  }));

  // Reset userModifiedPriceRange when category changes
  useEffect(() => {
    setUserModifiedPriceRange(false);
  }, [categoryId]);

  // Update filters when categoryProducts change (to update price range)
  useEffect(() => {
    // Only update price range if user hasn't manually modified it
    if (!userModifiedPriceRange && (priceRange[0] !== filters.priceRange[0] || priceRange[1] !== filters.priceRange[1])) {
      setFilters(prev => ({
        ...prev,
        priceRange: priceRange
      }));
    }
  }, [priceRange, filters.priceRange, userModifiedPriceRange]);

  // Filter functions
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
      priceRange: priceRange,
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

  // Apply filters and sorting to products
  const filteredAndSortedProducts = categoryProducts
    .filter(product => {
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
    })
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
  
  if (isLoading || isLoadingSubcategoryProducts) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading products...</p>
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
            <h1 className="text-2xl font-bold mb-4">Category not found</h1>
            <p className="text-muted-foreground mb-4">{error.message}</p>
            <Button onClick={() => navigate("/")}>Back to Home</Button>
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
        <div className="container px-4 py-4 sm:py-6 lg:py-8">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="mb-4 sm:mb-6"
            size="sm"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>

          <div className="mb-6 sm:mb-8">
            {/* Header with title and controls */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4 mb-4">
              <div className="flex-1">
                <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground mb-2">
                  {categoryName}
                </h1>
                <p className="text-sm sm:text-base text-muted-foreground">
                  {isParentCategory ? categoryProducts.length : filteredAndSortedProducts.length} products available
                  {isParentCategory && (
                    <span className="ml-2 text-xs sm:text-sm">
                      (including {category?.children.length} subcategories)
                    </span>
                  )}
                </p>
              </div>
              
              {/* Controls - Different for parent vs subcategory pages */}
              <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
                {isParentCategory ? (
                  /* Subcategory Dropdown for Parent Categories */
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="flex items-center gap-2 w-full sm:w-auto" size="sm">
                        <span className="hidden sm:inline">Browse Subcategories</span>
                        <span className="sm:hidden">Browse</span>
                        <ChevronDown className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      {category?.children?.map((subcategory) => (
                        <DropdownMenuItem
                          key={subcategory.category_id}
                          onClick={() => navigate(`/category/${subcategory.category_id}`)}
                        >
                          {subcategory.name} ({subcategory.product_count} products)
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                ) : (
                  /* Filter and Sort Buttons for Subcategory Pages */
                  <div className="flex gap-2 w-full sm:w-auto">
                    <FilterModal
                      onApplyFilters={applyFilters}
                      onClearFilters={clearFilters}
                      currentFilters={filters}
                      productCount={filteredAndSortedProducts.length}
                      availableBrands={availableBrands}
                      availableSubcategories={[]}
                      priceRange={priceRange}
                    />
                    <SortModal
                      onApplySort={applySort}
                      currentSort={sortOptions}
                      productCount={filteredAndSortedProducts.length}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Show subcategories in linear layout if this is a parent category */}
          {isParentCategory && category?.children && (
            <div className="space-y-6 sm:space-y-8">
              {category.children
                .filter((subcategory) => {
                  const products = subcategoryProductsMap[subcategory.category_id] || [];
                  return (subcategory.product_count && subcategory.product_count > 0) || products.length > 0;
                })
                .map((subcategory) => {
                  const products = subcategoryProductsMap[subcategory.category_id] || [];
                  return (
                    <SubcategorySection
                      key={subcategory.category_id}
                      subcategory={subcategory}
                      products={products}
                    />
                  );
                })}
            </div>
          )}

          {/* Show regular product grid for subcategories or if no subcategories */}
          {!isParentCategory && (
            <>
              {filteredAndSortedProducts.length === 0 ? (
                <div className="text-center py-8 sm:py-12">
                  <p className="text-muted-foreground text-base sm:text-lg">
                    {categoryProducts.length === 0 
                      ? "No products found in this category." 
                      : "No products match your current filters."}
                  </p>
                  {categoryProducts.length > 0 && (
                    <Button 
                      variant="outline" 
                      onClick={clearFilters}
                      className="mt-4"
                      size="sm"
                    >
                      Clear Filters
                    </Button>
                  )}
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
                  {filteredAndSortedProducts.map((product) => (
                    <ProductCard key={product.product_id} product={product} />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default CategoryPage;
