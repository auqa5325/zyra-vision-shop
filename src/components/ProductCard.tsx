import { Star, ShoppingCart, Info, Heart, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Product } from "@/types/product";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { interactionService } from "@/services/interactionService";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { useAuth } from "@/contexts/AuthContext";
import { AuthModal } from "@/components/AuthModal";

interface ProductCardProps {
  product: Product;
}

export const ProductCard = ({ product }: ProductCardProps) => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { toggleWishlist, isInWishlist } = useWishlist();
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authAction, setAuthAction] = useState<"cart" | "wishlist">("cart");
  
  const isWishlisted = isInWishlist(product.product_id);
  
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <Star key={i} className="h-4 w-4 fill-primary text-primary" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <Star key={i} className="h-4 w-4 fill-primary/50 text-primary" />
        );
      } else {
        stars.push(
          <Star key={i} className="h-4 w-4 text-muted-foreground" />
        );
      }
    }
    return stars;
  };

  const handleCardClick = () => {
    interactionService.trackClick(product.product_id);
    navigate(`/product/${product.product_id}`);
  };

  const handleAddToCart = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!user) {
      setAuthAction("cart");
      setShowAuthModal(true);
      return;
    }
    addToCart(product);
    // Track add to cart interaction
    interactionService.trackAddToCart(product.product_id, 1, {
      page: 'recommendation_card',
      product_name: product.name,
      price: product.price,
      source: product.reason_features?.source || 'unknown',
      timestamp: new Date().toISOString()
    });
  };

  const handleWishlistToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!user) {
      setAuthAction("wishlist");
      setShowAuthModal(true);
      return;
    }
    const wasInWishlist = isWishlisted;
    toggleWishlist(product);
    // Track wishlist interaction
    interactionService.trackWishlist(product.product_id, !wasInWishlist, {
      page: 'recommendation_card',
      product_name: product.name,
      price: product.price,
      source: product.reason_features?.source || 'unknown',
      timestamp: new Date().toISOString()
    });
  };

  return (
    <div 
      className="group relative bg-card rounded-xl border overflow-hidden hover:shadow-card transition-all duration-300 hover:-translate-y-1 animate-fade-in-up cursor-pointer h-full flex flex-col"
      onClick={handleCardClick}
    >
      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden bg-muted flex-shrink-0">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {/* AI Score Badge for Collaborative Filtering and Hybrid Recommendations - Top Left */}
        {((product.reason_features?.cf_score && product.reason_features?.source === "collaborative") ||
          (product.reason_features?.hybrid && product.reason_features?.source?.startsWith("hybrid"))) && (
          <div className="absolute top-1 left-1 sm:top-2 sm:left-2 z-10 max-w-[calc(100%-2rem)] sm:max-w-[calc(100%-4rem)]">
            <Badge 
              variant="default" 
              className="bg-gradient-to-r from-primary to-purple-600 text-white border-0 shadow-lg flex items-center gap-0.5 sm:gap-1 text-[9px] sm:text-xs px-1.5 sm:px-2.5 py-0.5 sm:py-1 whitespace-nowrap"
            >
              <Sparkles className="h-2 w-2 sm:h-3 sm:w-3 flex-shrink-0" />
              <span className="truncate">
                AI: {Math.round(
                  (product.reason_features?.hybrid && product.reason_features?.hybrid_score)
                    ? (product.reason_features.hybrid_score * 100)
                    : (product.reason_features?.cf_score ? (product.reason_features.cf_score * 100) : 0)
                )}%
              </span>
            </Badge>
          </div>
        )}
        
        {/* Wishlist Button - Top Right (moved to avoid overlap) */}
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button 
                className="absolute top-1 right-1 sm:top-2 sm:right-2 p-1.5 sm:p-2 bg-background/80 backdrop-blur-sm rounded-full hover:bg-background transition-colors z-10"
                onClick={handleWishlistToggle}
              >
                <Heart 
                  className={`h-3 w-3 sm:h-4 sm:w-4 transition-colors ${
                    isWishlisted 
                      ? "fill-red-500 text-red-500" 
                      : "text-muted-foreground hover:text-red-500"
                  }`} 
                />
              </button>
            </TooltipTrigger>
            <TooltipContent side="left">
              <p className="text-xs">{isWishlisted ? "Remove from wishlist" : "Add to wishlist"}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        {/* Info Button - Bottom Right (moved to avoid overlap) */}
        {product.reason_features && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <button className="absolute bottom-1 right-1 sm:bottom-2 sm:right-2 p-1.5 sm:p-2 bg-background/80 backdrop-blur-sm rounded-full hover:bg-background transition-colors z-10">
                  <Info className="h-3 w-3 sm:h-4 sm:w-4 text-primary" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="left" className="max-w-xs">
                <p className="font-semibold mb-1 text-sm">Why this?</p>
                {product.reason_features.matched_tags && (
                  <p className="text-xs text-muted-foreground">
                    Matches: {product.reason_features.matched_tags.join(", ")}
                  </p>
                )}
                {product.reason_features.cf_score && (
                  <p className="text-xs text-muted-foreground">
                    Recommendation score: {(product.reason_features.cf_score * 100).toFixed(0)}%
                  </p>
                )}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>

      {/* Product Info */}
      <div className="p-3 sm:p-4 flex flex-col flex-grow">
        <h3 className="font-semibold text-foreground mb-1 line-clamp-2 min-h-[2.5rem] sm:min-h-[3rem] group-hover:text-primary transition-colors text-sm sm:text-base">
          {product.name}
        </h3>
        <p className="text-xs sm:text-sm text-muted-foreground mb-2 sm:mb-3 line-clamp-2 min-h-[2rem] sm:min-h-[2.5rem]">
          {product.description || "\u00A0"}
        </p>

        {/* Rating */}
        <div className="flex items-center gap-1 sm:gap-2 mb-2 sm:mb-3 min-h-[1.25rem] sm:min-h-[1.5rem]">
          {(product.average_rating !== undefined || product.rating !== undefined) && (
            <>
              <div className="flex gap-0.5">
                {renderStars(product.average_rating ?? product.rating ?? 0)}
              </div>
              <span className="text-xs sm:text-sm text-muted-foreground">
                ({((product.average_rating ?? product.rating) || 0).toFixed(1)})
                {product.total_reviews !== undefined && product.total_reviews > 0 && (
                  <span className="ml-1">({product.total_reviews})</span>
                )}
              </span>
            </>
          )}
        </div>

        {/* Price and CTA */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mt-auto gap-2 sm:gap-0">
          <DiscountPrice 
            price={product.price}
            discountPercent={product.discount_percent}
            size="2xl"
            layout="vertical"
            alignment="left"
            className="flex-1"
          />
          <Button 
            size="sm" 
            variant="gradient" 
            className="gap-1 sm:gap-2 flex-shrink-0 w-full sm:w-auto text-xs sm:text-sm"
            onClick={handleAddToCart}
          >
            <ShoppingCart className="h-3 w-3 sm:h-4 sm:w-4" />
            <span className="hidden sm:inline">Add</span>
            <span className="sm:hidden">Add to Cart</span>
          </Button>
        </div>
      </div>
      
      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        action={authAction}
      />
    </div>
  );
};
