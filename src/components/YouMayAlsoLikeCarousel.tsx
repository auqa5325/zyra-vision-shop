import { Sparkles } from "lucide-react";
import { Product } from "@/types/product";
import { ProductCard } from "@/components/ProductCard";
import { useProductYouMayAlsoLike } from "@/hooks/useRecommendations";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { useAuth } from "@/hooks/useAuth";

interface YouMayAlsoLikeCarouselProps {
  productId: string;
  limit?: number;
}

export const YouMayAlsoLikeCarousel = ({ productId, limit = 8 }: YouMayAlsoLikeCarouselProps) => {
  const { user } = useAuth();
  const userId = user?.user_id || null;
  const { data: recommendations = [], isLoading, error } = useProductYouMayAlsoLike(productId, userId, limit);

  console.log('YouMayAlsoLikeCarousel - isLoading:', isLoading, 'error:', error, 'data:', recommendations);

  // Show error state
  if (error) {
    console.error('YouMayAlsoLikeCarousel error:', error);
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">You May Also Like</h2>
            <p className="text-muted-foreground">Personalized recommendations just for you</p>
          </div>
        </div>
        <div className="p-8 text-center">
          <p className="text-muted-foreground">Unable to load recommendations. Please try again later.</p>
          <p className="text-sm text-red-500 mt-2">{error.message}</p>
        </div>
      </section>
    );
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
            <h2 className="text-3xl font-bold text-foreground">You May Also Like</h2>
            <p className="text-muted-foreground">Personalized recommendations just for you</p>
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

  // Show empty state (but still show the section)
  if (!recommendations || recommendations.length === 0) {
    console.log('YouMayAlsoLikeCarousel: No data to display');
    return (
      <section className="py-12">
        <div className="mb-8 flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-foreground">You May Also Like</h2>
            <p className="text-muted-foreground">Personalized recommendations just for you</p>
          </div>
        </div>
        <div className="p-8 text-center">
          <p className="text-muted-foreground">No recommendations available at the moment.</p>
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
          <h2 className="text-3xl font-bold text-foreground">You May Also Like</h2>
          <p className="text-muted-foreground">Personalized recommendations just for you</p>
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
              <CarouselItem key={product.product_id} className="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3 xl:basis-1/4 flex">
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
