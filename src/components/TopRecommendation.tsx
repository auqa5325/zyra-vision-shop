import { Sparkles } from "lucide-react";
import { Product } from "@/types/product";
import { Button } from "@/components/ui/button";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { useAuth } from "@/contexts/AuthContext";

interface TopRecommendationProps {
  topPick?: Product | null;
  isLoading?: boolean;
}

export const TopRecommendation = ({ topPick, isLoading }: TopRecommendationProps) => {
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Don't show recommendation card if user is not logged in or auth is still loading
  if (authLoading || !isAuthenticated) {
    return null;
  }

  // Show loading state
  if (isLoading) {
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">Top Pick for You</h2>
            <p className="text-muted-foreground">AI-powered personalized recommendation</p>
          </div>
        </div>

        <div className="relative bg-gradient-to-br from-primary/10 via-secondary/10 to-background border border-primary/20 rounded-2xl overflow-hidden shadow-glow">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 p-4 sm:p-6 lg:p-8">
            <div className="aspect-square bg-muted/50 rounded-xl animate-pulse order-1 lg:order-1"></div>
            <div className="flex flex-col justify-center order-2 lg:order-2">
              <div className="h-6 sm:h-8 bg-muted/50 rounded animate-pulse mb-3 sm:mb-4"></div>
              <div className="h-4 sm:h-6 bg-muted/50 rounded animate-pulse mb-2 sm:mb-3"></div>
              <div className="h-3 sm:h-4 bg-muted/50 rounded animate-pulse mb-3 sm:mb-4"></div>
              <div className="h-3 sm:h-4 bg-muted/50 rounded animate-pulse mb-4 sm:mb-6"></div>
              <div className="h-8 sm:h-10 bg-muted/50 rounded animate-pulse"></div>
            </div>
          </div>
        </div>
      </section>
    );
  }

  // Show fallback if no top pick available
  if (!topPick) {
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">Top Pick for You</h2>
            <p className="text-muted-foreground">AI-powered personalized recommendation</p>
          </div>
        </div>

        <div className="relative bg-gradient-to-br from-primary/10 via-secondary/10 to-background border border-primary/20 rounded-2xl overflow-hidden shadow-glow">
          <div className="p-8 text-center">
            <p className="text-muted-foreground">No recommendations available at the moment.</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-12">
      <div className="mb-8 flex items-center gap-3">
        <div className="p-2 bg-primary/10 rounded-lg">
          <Sparkles className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-foreground">Top Pick for You</h2>
          <p className="text-muted-foreground">AI-powered personalized recommendation</p>
        </div>
      </div>

      <div className="relative bg-gradient-to-br from-primary/10 via-secondary/10 to-background border border-primary/20 rounded-2xl overflow-hidden shadow-glow">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 p-4 sm:p-6 lg:p-8">
          {/* Image Section */}
          <div className="relative aspect-square bg-muted/50 rounded-xl overflow-hidden order-1 lg:order-1">
            <img
              src={topPick.image_url}
              alt={topPick.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-2 right-2 sm:top-4 sm:right-4 px-2 py-1 sm:px-4 sm:py-2 bg-primary text-primary-foreground text-xs sm:text-sm font-bold rounded-full shadow-glow animate-pulse">
              TOP PICK
            </div>
          </div>

          {/* Content Section */}
          <div className="flex flex-col justify-center order-2 lg:order-2">
            <div className="mb-4">
              <div className="inline-flex items-center gap-2 px-2 py-1 sm:px-3 sm:py-1 bg-secondary/20 text-secondary rounded-full text-xs sm:text-sm font-medium mb-3 sm:mb-4">
                <Sparkles className="h-3 w-3 sm:h-4 sm:w-4" />
                {Math.round((topPick.reason_features?.cf_score || 0.9) * 100)}% AI Match Score
              </div>
              <h3 className="text-xl sm:text-2xl lg:text-3xl font-bold text-foreground mb-2 sm:mb-3">
                {topPick.name}
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-3 sm:mb-4 text-sm sm:text-base">
                {topPick.description}
              </p>
              
              {/* Rating */}
              <div className="flex items-center gap-2 mb-4 sm:mb-6">
                <div className="flex">
                  {[...Array(5)].map((_, i) => {
                    const rating = topPick.average_rating ?? topPick.rating ?? 0;
                    return (
                      <span key={i} className={`text-sm sm:text-base ${i < Math.floor(rating) ? "text-primary" : "text-muted"}`}>
                        ★
                      </span>
                    );
                  })}
                </div>
                <span className="text-xs sm:text-sm text-muted-foreground">
                  {((topPick.average_rating ?? topPick.rating) || 0).toFixed(1)} / 5.0
                </span>
              </div>

              {/* Tags */}
              {topPick.reason_features?.matched_tags && topPick.reason_features.matched_tags.length > 0 && (
                <div className="flex flex-wrap gap-1 sm:gap-2 mb-4 sm:mb-6">
                  {topPick.reason_features.matched_tags.slice(0, 4).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 sm:px-3 sm:py-1 bg-accent/10 text-accent text-xs font-medium rounded-full border border-accent/20"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Price & CTA */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
              <DiscountPrice 
                price={topPick.price}
                discountPercent={topPick.discount_percent}
                size="4xl"
                layout="vertical"
                alignment="left"
              />
              <Button size="lg" className="w-full sm:w-auto bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-opacity">
                Add to Cart
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
