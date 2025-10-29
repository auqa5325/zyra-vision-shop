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
    <div className="mb-12">
      {/* Subcategory Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground">{subcategory.name}</h2>
          <p className="text-muted-foreground">{subcategory.product_count} products available</p>
        </div>
        <Button
          variant="outline"
          onClick={() => navigate(`/category/${subcategory.category_id}`)}
          className="flex items-center gap-2"
        >
          Explore {subcategory.name}
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
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-background/80 backdrop-blur-sm"
            onClick={scrollLeft}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
        )}

        {/* Products Container */}
        <div
          ref={scrollContainerRef}
          className="flex gap-4 overflow-x-auto scrollbar-hide pb-4"
          onScroll={handleScroll}
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {products.slice(0, 10).map((product) => (
            <div key={product.product_id} className="flex-shrink-0 w-64">
              <ProductCard product={product} />
            </div>
          ))}
          
          {/* Explore More Card */}
          <div className="flex-shrink-0 w-64">
            <div className="h-full bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-dashed border-primary/30 rounded-lg p-6 flex flex-col items-center justify-center text-center hover:border-primary/50 transition-colors cursor-pointer"
                 onClick={() => navigate(`/category/${subcategory.category_id}`)}>
              <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mb-4">
                <ArrowRight className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground mb-2">Explore All</h3>
              <p className="text-sm text-muted-foreground mb-3">
                View all {subcategory.product_count} products in {subcategory.name}
              </p>
              <Button size="sm" className="w-full">
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
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-background/80 backdrop-blur-sm"
            onClick={scrollRight}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
};
