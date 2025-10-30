import { ProductCard } from "@/components/ProductCard";
import { Product } from "@/types/product";
import { CategoryHierarchy } from "@/types/api";
import { Button } from "@/components/ui/button";
import { ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

interface SubcategorySectionProps {
  subcategory: CategoryHierarchy;
  products: Product[];
}

export const SubcategorySection = ({ subcategory, products }: SubcategorySectionProps) => {
  const navigate = useNavigate();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const handleScroll = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -300, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 300, behavior: 'smooth' });
    }
  };

  return (
    <div className="mb-8 sm:mb-12">
      {/* Subcategory Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4 mb-4 sm:mb-6">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-foreground">{subcategory.name}</h2>
          <p className="text-sm sm:text-base text-muted-foreground">{subcategory.product_count} products available</p>
        </div>
        <Button
          variant="outline"
          onClick={() => navigate(`/category/${subcategory.category_id}`)}
          className="flex items-center gap-2 w-full sm:w-auto"
          size="sm"
        >
          <span className="hidden sm:inline">Explore {subcategory.name}</span>
          <span className="sm:hidden">Explore</span>
          <ArrowRight className="w-4 h-4" />
        </Button>
      </div>

      {/* Products Carousel */}
      <div className="relative">
        {/* Scroll Left Button */}
        {canScrollLeft && (
          <Button
            variant="outline"
            size="icon"
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-background/80 backdrop-blur-sm hidden sm:flex"
            onClick={scrollLeft}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
        )}

        {/* Products Container */}
        <div
          ref={scrollContainerRef}
          className="flex gap-3 sm:gap-4 overflow-x-auto scrollbar-hide pb-4"
          onScroll={handleScroll}
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {products.slice(0, 10).map((product) => (
            <div key={product.product_id} className="flex-shrink-0 w-48 sm:w-56 lg:w-64">
              <ProductCard product={product} />
            </div>
          ))}
          
          {/* Explore More Card */}
          <div className="flex-shrink-0 w-48 sm:w-56 lg:w-64">
            <div className="h-full bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-dashed border-primary/30 rounded-lg p-4 sm:p-6 flex flex-col items-center justify-center text-center hover:border-primary/50 transition-colors cursor-pointer"
                 onClick={() => navigate(`/category/${subcategory.category_id}`)}>
              <div className="w-12 h-12 sm:w-16 sm:h-16 bg-primary/20 rounded-full flex items-center justify-center mb-3 sm:mb-4">
                <ArrowRight className="w-6 h-6 sm:w-8 sm:h-8 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground mb-2 text-sm sm:text-base">Explore All</h3>
              <p className="text-xs sm:text-sm text-muted-foreground mb-3">
                View all {subcategory.product_count} products in {subcategory.name}
              </p>
              <Button size="sm" className="w-full text-xs sm:text-sm">
                Browse Collection
              </Button>
            </div>
          </div>
        </div>

        {/* Scroll Right Button */}
        {canScrollRight && (
          <Button
            variant="outline"
            size="icon"
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-background/80 backdrop-blur-sm hidden sm:flex"
            onClick={scrollRight}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
};
