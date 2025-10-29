import { Header } from "@/components/Header";
import { HeroCarousel } from "@/components/HeroCarousel";
import { TopSellersCarousel } from "@/components/TopSellersCarousel";
import { WhatYouMayLikeCarousel } from "@/components/WhatYouMayLikeCarousel";
import { WhatSimilarUsersLikedCarousel } from "@/components/WhatSimilarUsersLikedCarousel";
import { CategoryCard } from "@/components/CategoryCard";
import { FAQ } from "@/components/FAQ";
import { ChatBot } from "@/components/ChatBot";
import { Footer } from "@/components/Footer";
import { useCategoriesHierarchy, useProductsByCategory } from "@/hooks/useProducts";
import { CategoryHierarchy } from "@/types/api";
import { useAuth } from "@/contexts/AuthContext";

// Component to handle individual category with product fetching
const CategoryCardWithProducts = ({ category }: { category: CategoryHierarchy }) => {
  const { data: products = [], isLoading: productsLoading } = useProductsByCategory(category.category_id, { limit: 4 });
  
  return (
    <CategoryCard
      category={category.name}
      categoryId={category.category_id}
      products={products}
      productCount={category.product_count}
      subcategories={category.children}
    />
  );
};

const Index = () => {
  // Fetch categories from API
  const { data: categoriesHierarchy = [], isLoading: categoriesLoading } = useCategoriesHierarchy();
  const { isAuthenticated, user, isLoading: authLoading } = useAuth();

  // Show loading state
  if (categoriesLoading || authLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading...</p>
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
        <div className="container px-4 py-8">
          {/* Hero Section */}
          <HeroCarousel />

          {/* Recommendations Section - Conditional based on auth status */}
          {isAuthenticated && user ? (
            <>
              {/* Logged-in users: Show two carousels */}
              <WhatYouMayLikeCarousel userId={user.user_id} limit={8} />
              <WhatSimilarUsersLikedCarousel userId={user.user_id} limit={8} />
            </>
          ) : (
            /* Non-logged-in users: Show Top Sellers */
            <TopSellersCarousel limit={8} />
          )}

          {/* Categories Section */}
          <section className="py-12">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-foreground mb-2">
                Shop by Category
              </h2>
              <p className="text-muted-foreground">
                Browse our curated collections
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categoriesHierarchy.map((category: CategoryHierarchy) => (
                <CategoryCardWithProducts
                  key={category.category_id}
                  category={category}
                />
              ))}
            </div>
          </section>

          {/* FAQ Section */}
          <FAQ />
        </div>
      </main>

      <Footer />
      <ChatBot />
    </div>
  );
};

export default Index;
