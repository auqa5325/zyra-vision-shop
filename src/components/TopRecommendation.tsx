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
          <div className="grid md:grid-cols-2 gap-8 p-8">
            <div className="aspect-square bg-muted/50 rounded-xl animate-pulse"></div>
            <div className="flex flex-col justify-center">
              <div className="h-8 bg-muted/50 rounded animate-pulse mb-4"></div>
              <div className="h-6 bg-muted/50 rounded animate-pulse mb-3"></div>
              <div className="h-4 bg-muted/50 rounded animate-pulse mb-4"></div>
              <div className="h-4 bg-muted/50 rounded animate-pulse mb-6"></div>
              <div className="h-8 bg-muted/50 rounded animate-pulse"></div>
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
        <div className="grid md:grid-cols-2 gap-8 p-8">
          {/* Image Section */}
          <div className="relative aspect-square bg-muted/50 rounded-xl overflow-hidden">
            <img
              src={topPick.image_url}
              alt={topPick.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-4 right-4 px-4 py-2 bg-primary text-primary-foreground text-sm font-bold rounded-full shadow-glow animate-pulse">
              TOP PICK
            </div>
          </div>

          {/* Content Section */}
          <div className="flex flex-col justify-center">
            <div className="mb-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-secondary/20 text-secondary rounded-full text-sm font-medium mb-4">
                <Sparkles className="h-4 w-4" />
                {Math.round((topPick.reason_features?.cf_score || 0.9) * 100)}% AI Match Score
              </div>
              <h3 className="text-3xl font-bold text-foreground mb-3">
                {topPick.name}
              </h3>
              <p className="text-muted-foreground leading-relaxed mb-4">
                {topPick.description}
              </p>
              
              {/* Rating */}
              <div className="flex items-center gap-2 mb-6">
                <div className="flex">
                  {[...Array(5)].map((_, i) => {
                    const rating = topPick.average_rating ?? topPick.rating ?? 0;
                    return (
                      <span key={i} className={i < Math.floor(rating) ? "text-primary" : "text-muted"}>
                        ★
                      </span>
                    );
                  })}
                </div>
                <span className="text-sm text-muted-foreground">
                  {((topPick.average_rating ?? topPick.rating) || 0).toFixed(1)} / 5.0
                </span>
              </div>

              {/* Tags */}
              {topPick.reason_features?.matched_tags && topPick.reason_features.matched_tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {topPick.reason_features.matched_tags.slice(0, 4).map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-accent/10 text-accent text-xs font-medium rounded-full border border-accent/20"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Price & CTA */}
            <div className="flex items-center gap-4">
              <DiscountPrice 
                price={topPick.price}
                discountPercent={topPick.discount_percent}
                size="4xl"
                layout="vertical"
                alignment="left"
              />
              <Button size="lg" className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-opacity">
                Add to Cart
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
