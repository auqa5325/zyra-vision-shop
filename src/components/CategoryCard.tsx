import { Card, CardContent } from "./ui/card";
import { ArrowRight, ChevronDown } from "lucide-react";
import { Product } from "@/types/product";
import { CategoryHierarchy } from "@/types/api";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

interface CategoryCardProps {
  category: string;
  categoryId: number;
  products: Product[];
  productCount: number;
  subcategories: CategoryHierarchy[];
}

export const CategoryCard = ({ category, categoryId, products, productCount, subcategories }: CategoryCardProps) => {
  const navigate = useNavigate();
  const [showSubcategories, setShowSubcategories] = useState(false);
  const topProducts = products.slice(0, 4);

  const handleCategoryClick = () => {
    navigate(`/category/${categoryId}`);
  };

  const handleSubcategoryClick = (subcategoryId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    navigate(`/category/${subcategoryId}`);
  };

  return (
    <Card 
      className="group cursor-pointer overflow-hidden transition-all duration-300 hover:shadow-glow"
      onClick={handleCategoryClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-foreground">
            {category}
          </h3>
          <div className="flex items-center gap-2">
            {subcategories.length > 0 && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowSubcategories(!showSubcategories);
                }}
                className="p-1 hover:bg-muted rounded"
              >
                <ChevronDown 
                  className={`w-4 h-4 text-muted-foreground transition-transform ${
                    showSubcategories ? 'rotate-180' : ''
                  }`} 
                />
              </button>
            )}
            <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
          </div>
        </div>

        {/* Subcategories dropdown */}
        {showSubcategories && subcategories.length > 0 && (
          <div className="mb-4 p-3 bg-muted/30 rounded-lg">
            <p className="text-sm font-medium text-foreground mb-2">Subcategories:</p>
            <div className="grid grid-cols-1 gap-1">
              {subcategories.map((subcategory) => (
                <button
                  key={subcategory.category_id}
                  onClick={(e) => handleSubcategoryClick(subcategory.category_id, e)}
                  className="text-left text-sm text-muted-foreground hover:text-primary transition-colors py-1 px-2 rounded hover:bg-muted/50"
                >
                  {subcategory.name} ({subcategory.product_count})
                </button>
              ))}
            </div>
          </div>
        )}
        
        <div className="grid grid-cols-2 gap-3">
          {topProducts.length > 0 ? (
            topProducts.map((product) => (
              <div 
                key={product.product_id}
                className="relative aspect-square rounded-lg overflow-hidden bg-muted/30 group/item"
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/product/${product.product_id}`);
                }}
              >
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover/item:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover/item:opacity-100 transition-opacity">
                  <div className="absolute bottom-2 left-2 right-2">
                    <p className="text-xs text-white font-medium truncate">{product.name}</p>
                    <p className="text-xs text-white/80">₹{product.price}</p>
                  </div>
                </div>
              </div>
            ))
          ) : (
            // Show placeholder when no products available
            Array.from({ length: 4 }).map((_, index) => (
              <div 
                key={`placeholder-${index}`}
                className="aspect-square rounded-lg bg-muted/20 border-2 border-dashed border-muted-foreground/30 flex items-center justify-center"
              >
                <div className="text-center">
                  <div className="w-8 h-8 mx-auto mb-2 bg-muted-foreground/20 rounded-full flex items-center justify-center">
                    <span className="text-muted-foreground/50 text-xs">+</span>
                  </div>
                  <p className="text-xs text-muted-foreground/50">Coming Soon</p>
                </div>
              </div>
            ))
          )}
        </div>
        
        <p className="mt-3 text-sm text-muted-foreground">
          {productCount} products available
        </p>
      </CardContent>
    </Card>
  );
};
