import { Sparkles } from "lucide-react";
import { Product } from "@/types/product";
import { ProductCard } from "@/components/ProductCard";
import { useAuth } from "@/contexts/AuthContext";
import { useRecommendations } from "@/hooks/useRecommendations";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

interface TopPicksCarouselProps {
  limit?: number;
}

export const TopPicksCarousel = ({ limit = 8 }: TopPicksCarouselProps) => {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { data: recommendations = [], isLoading, error } = useRecommendations({ k: limit });

  // Show general recommendations for non-authenticated users, personalized for authenticated users
  // if (authLoading || !isAuthenticated) {
  //   return null;
  // }

  // Show loading state
  if (isLoading) {
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">
              {isAuthenticated ? "Top Picks for You" : "Top Picks"}
            </h2>
            <p className="text-muted-foreground">
              {isAuthenticated ? "AI-powered personalized recommendations" : "AI-powered recommendations"}
            </p>
          </div>
        </div>

        <div className="relative">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-card rounded-xl border overflow-hidden">
                <div className="aspect-square bg-muted/50 rounded-t-xl animate-pulse"></div>
                <div className="p-4">
                  <div className="h-6 bg-muted/50 rounded animate-pulse mb-2"></div>
                  <div className="h-4 bg-muted/50 rounded animate-pulse mb-3"></div>
                  <div className="h-8 bg-muted/50 rounded animate-pulse"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  }

  // Show error state
  if (error) {
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">
              {isAuthenticated ? "Top Picks for You" : "Top Picks"}
            </h2>
            <p className="text-muted-foreground">
              {isAuthenticated ? "AI-powered personalized recommendations" : "AI-powered recommendations"}
            </p>
          </div>
        </div>

        <div className="relative bg-gradient-to-br from-primary/10 via-secondary/10 to-background border border-primary/20 rounded-2xl overflow-hidden shadow-glow">
          <div className="p-8 text-center">
            <p className="text-muted-foreground">Unable to load recommendations at the moment.</p>
            <p className="text-sm text-muted-foreground mt-2">Please try again later.</p>
          </div>
        </div>
      </section>
    );
  }

  // Show fallback if no recommendations available
  if (!recommendations || recommendations.length === 0) {
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">
              {isAuthenticated ? "Top Picks for You" : "Top Picks"}
            </h2>
            <p className="text-muted-foreground">
              {isAuthenticated ? "AI-powered personalized recommendations" : "AI-powered recommendations"}
            </p>
          </div>
        </div>

        <div className="relative bg-gradient-to-br from-primary/10 via-secondary/10 to-background border border-primary/20 rounded-2xl overflow-hidden shadow-glow">
          <div className="p-8 text-center">
            <p className="text-muted-foreground">No recommendations available at the moment.</p>
            <p className="text-sm text-muted-foreground mt-2">Check back later for personalized picks!</p>
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
          <h2 className="text-3xl font-bold text-foreground">Top Picks for You</h2>
          <p className="text-muted-foreground">AI-powered personalized recommendations</p>
        </div>
      </div>

      <div className="relative">
        <Carousel
          opts={{
            align: "start",
            loop: true,
            skipSnaps: false,
            dragFree: true,
          }}
          className="w-full"
        >
          <CarouselContent className="-ml-2 md:-ml-4">
            {recommendations.map((product) => (
              <CarouselItem key={product.product_id} className="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3 xl:basis-1/4">
                <ProductCard product={product} />
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious className="hidden md:flex" />
          <CarouselNext className="hidden md:flex" />
        </Carousel>

        {/* Mobile navigation dots */}
        <div className="flex justify-center mt-6 md:hidden">
          <div className="flex gap-2">
            {[...Array(Math.ceil(recommendations.length / 2))].map((_, i) => (
              <div
                key={i}
                className="w-2 h-2 rounded-full bg-primary/30"
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
