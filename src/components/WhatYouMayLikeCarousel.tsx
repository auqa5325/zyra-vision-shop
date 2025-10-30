import { Heart } from "lucide-react";
import { Product } from "@/types/product";
import { ProductCard } from "@/components/ProductCard";
import { useContentBasedRecommendations } from "@/hooks/useRecommendations";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

interface WhatYouMayLikeCarouselProps {
  userId: string;
  limit?: number;
}

export const WhatYouMayLikeCarousel = ({ userId, limit = 8 }: WhatYouMayLikeCarouselProps) => {
  const { data: recommendations = [], isLoading, error } = useContentBasedRecommendations(userId, limit);

  // Debug logging
  if (error) {
    console.error('WhatYouMayLikeCarousel error:', error);
  }

  // Show loading state
  if (isLoading) {
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Heart className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">What You May Like</h2>
            <p className="text-muted-foreground">Based on your preferences</p>
          </div>
        </div>

        <div className="relative">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-card rounded-xl border overflow-hidden">
                <div className="aspect-square bg-muted/50 rounded-t-xl animate-pulse"></div>
                <div className="p-3 sm:p-4">
                  <div className="h-4 sm:h-6 bg-muted/50 rounded animate-pulse mb-2"></div>
                  <div className="h-3 sm:h-4 bg-muted/50 rounded animate-pulse mb-2 sm:mb-3"></div>
                  <div className="h-6 sm:h-8 bg-muted/50 rounded animate-pulse"></div>
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
    console.error('WhatYouMayLikeCarousel error:', error);
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Heart className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">What You May Like</h2>
            <p className="text-muted-foreground">Based on your preferences</p>
          </div>
        </div>
        <div className="p-8 text-center">
          <p className="text-muted-foreground">Unable to load recommendations. Please try again later.</p>
          <p className="text-sm text-red-500 mt-2">{error.message}</p>
        </div>
      </section>
    );
  }

  // Show empty state
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <section className="py-12">
      <div className="mb-8 flex items-center gap-3">
        <div className="p-2 bg-primary/10 rounded-lg">
          <Heart className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-foreground">What You May Like</h2>
          <p className="text-muted-foreground">Based on your preferences</p>
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
          <CarouselContent className="-ml-1 sm:-ml-2 md:-ml-4">
            {recommendations.map((product) => (
              <CarouselItem key={product.product_id} className="pl-1 sm:pl-2 md:pl-4 basis-1/2 sm:basis-1/3 md:basis-1/2 lg:basis-1/3 xl:basis-1/4 flex">
                <div className="w-full h-full">
                  <ProductCard product={product} />
                </div>
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

