import { useParams, useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ReviewSection } from "@/components/ReviewSection";
import { YouMayAlsoLikeCarousel } from "@/components/YouMayAlsoLikeCarousel";
import { Product } from "@/types/product";
import { ArrowLeft, Star, ShoppingCart, Heart, Plus, Minus, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { useProduct } from "@/hooks/useProducts";
import { useSimilarProducts, useUserItemSimilarity } from "@/hooks/useRecommendations";
import { useEffect, useState } from "react";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { useAuth } from "@/contexts/AuthContext";
import { AuthModal } from "@/components/AuthModal";
import { interactionService } from "@/services/interactionService";

const ProductPage = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { addToCart, cart } = useCart();
  const { toggleWishlist, isInWishlist } = useWishlist();
  const { user } = useAuth();
  const [quantity, setQuantity] = useState(1);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authAction, setAuthAction] = useState<"cart" | "wishlist">("cart");
  
  const { data: product, isLoading, error } = useProduct(productId || '');
  const { data: similarProducts = [] } = useSimilarProducts(productId || '', 4);
  const { data: userItemSimilarity = 0 } = useUserItemSimilarity(user?.user_id || null, productId || '');

  // Track product view
  useEffect(() => {
    if (productId) {
      // Track view interaction - wrapped in setTimeout to avoid setState during render
      setTimeout(() => {
        interactionService.trackView(productId, {
          page: 'product_detail',
          timestamp: new Date().toISOString()
        });
      }, 0);
    }
  }, [productId]);

  // Console log review interactions
  useEffect(() => {
    const handleReviewInteraction = (event: CustomEvent) => {
      console.log('⭐ [REVIEW_INTERACTION] Review submitted:', {
        productId: productId,
        rating: event.detail?.rating,
        hasComment: !!event.detail?.comment,
        commentLength: event.detail?.comment?.length || 0,
        timestamp: new Date().toISOString()
      });
    };

    // Listen for custom review events
    window.addEventListener('reviewSubmitted', handleReviewInteraction as EventListener);
    
    return () => {
      window.removeEventListener('reviewSubmitted', handleReviewInteraction as EventListener);
    };
  }, [productId]);

  // Get current cart quantity for this product
  const currentCartQuantity = product ? 
    cart.items.find(item => item.product_id === product.product_id)?.quantity || 0 
    : 0;

  // Sync quantity state with cart
  useEffect(() => {
    if (product) {
      setQuantity(currentCartQuantity || 1);
    }
  }, [product, currentCartQuantity]);


  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading product...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Product not found</h1>
            <p className="text-muted-foreground mb-4">
              {error?.message || 'The product you are looking for does not exist.'}
            </p>
            <Button onClick={() => navigate("/")}>Back to Home</Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating)
            ? "fill-yellow-400 text-yellow-400"
            : "text-muted-foreground"
        }`}
      />
    ));
  };

  const handleAddToCart = () => {
    if (!user) {
      setAuthAction("cart");
      setShowAuthModal(true);
      return;
    }
    
    if (product) {
      addToCart(product, quantity);
      setQuantity(1); // Reset quantity after adding
      
      // Track add to cart interaction
      interactionService.trackAddToCart(product.product_id, quantity, {
        page: 'product_detail',
        product_name: product.name,
        price: product.price,
        timestamp: new Date().toISOString()
      });
    }
  };

  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity >= 1 && newQuantity <= 10) {
      setQuantity(newQuantity);
    }
  };

  const handleGoToCart = () => {
    navigate("/cart");
  };

  const handleWishlistToggle = () => {
    if (!user) {
      setAuthAction("wishlist");
      setShowAuthModal(true);
      return;
    }
    
    if (product) {
      const wasInWishlist = isInWishlist(product.product_id);
      toggleWishlist(product);
      
      // Track wishlist interaction
      const isAdding = !wasInWishlist;
      interactionService.trackWishlist(product.product_id, isAdding, {
        page: 'product_detail',
        timestamp: new Date().toISOString()
      });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1">
        <div className="container px-4 py-8">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
            {/* Product Image */}
            <div className="relative aspect-square rounded-xl overflow-hidden bg-muted/30">
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Product Details */}
            <div className="flex flex-col">
              <div className="mb-4">
                {product.category && (
                  <Badge variant="secondary" className="mb-2">
                    {product.category}
                  </Badge>
                )}
                <h1 className="text-3xl lg:text-4xl font-bold text-foreground mb-4">
                  {product.name}
                </h1>
                
                {(product.average_rating !== undefined || product.rating !== undefined) && (
                  <div className="flex items-center gap-2 mb-4">
                    <div className="flex gap-1">
                      {renderStars(product.average_rating ?? product.rating ?? 0)}
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {((product.average_rating ?? product.rating) || 0).toFixed(1)} out of 5
                      {product.total_reviews !== undefined && product.total_reviews > 0 && (
                        <span className="ml-1">({product.total_reviews} reviews)</span>
                      )}
                    </span>
                  </div>
                )}
              </div>

              <p className="text-lg text-muted-foreground mb-6">
                {product.description}
              </p>

              {user && userItemSimilarity > 0 && (
                <div className="mb-6">
                  <Badge 
                    variant="default" 
                    className="bg-gradient-to-r from-primary to-purple-600 text-white border-0 shadow-lg text-sm sm:text-base px-3 sm:px-4 py-1.5 sm:py-2 flex items-center gap-1.5 sm:gap-2 w-fit"
                  >
                    <Sparkles className="h-3.5 w-3.5 sm:h-4 sm:w-4 flex-shrink-0" />
                    <span>AI Score: {Math.round(userItemSimilarity * 100)}%</span>
                  </Badge>
                </div>
              )}
              
              {product.reason_features && product.reason_features.matched_tags && product.reason_features.matched_tags.length > 0 && (
                <div className="bg-muted/30 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold mb-2 text-foreground">Why we recommend this</h3>
                  <div className="flex flex-wrap gap-2">
                    {product.reason_features.matched_tags.map((tag) => (
                      <Badge key={tag} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-auto">
                <div className="mb-6">
                  <p className="text-sm text-muted-foreground mb-1">Price</p>
                  <DiscountPrice 
                    price={product.price}
                    discountPercent={product.discount_percent}
                    size="4xl"
                    layout="vertical"
                    alignment="left"
                  />
                </div>

                {/* Quantity Controls */}
                <div className="mb-4">
                  <p className="text-sm text-muted-foreground mb-2">Quantity</p>
                  <div className="flex items-center gap-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuantityChange(quantity - 1)}
                      disabled={quantity <= 1}
                    >
                      <Minus className="w-4 h-4" />
                    </Button>
                    <div className="w-16 text-center">
                      <span className="text-lg font-semibold">{quantity}</span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuantityChange(quantity + 1)}
                      disabled={quantity >= 10}
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Cart Status */}
                {currentCartQuantity > 0 && (
                  <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-700">
                      <ShoppingCart className="w-4 h-4 inline mr-1" />
                      {currentCartQuantity} {currentCartQuantity === 1 ? 'item' : 'items'} in cart
                    </p>
                    <Button 
                      variant="link" 
                      size="sm" 
                      onClick={handleGoToCart}
                      className="p-0 h-auto text-blue-600 hover:text-blue-700"
                    >
                      View Cart
                    </Button>
                  </div>
                )}

                <Button size="lg" className="w-full" variant="gradient" onClick={handleAddToCart}>
                  <ShoppingCart className="w-5 h-5 mr-2" />
                  Add to Cart
                </Button>
                
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="w-full mt-3"
                  onClick={handleWishlistToggle}
                >
                  <Heart 
                    className={`w-5 h-5 mr-2 ${
                      product && isInWishlist(product.product_id)
                        ? "fill-red-500 text-red-500" 
                        : "text-muted-foreground"
                    }`} 
                  />
                  {product && isInWishlist(product.product_id) ? "Remove from Wishlist" : "Add to Wishlist"}
                </Button>
              </div>
            </div>
          </div>

          {/* You May Also Like Section */}
          {productId && (
            <YouMayAlsoLikeCarousel productId={productId} limit={8} />
          )}

          {/* Reviews Section */}
          <ReviewSection productId={productId || ''} />

          {/* Similar Products Section */}
          {similarProducts.length > 0 && (
            <section className="mt-16">
              <h2 className="text-2xl font-bold text-foreground mb-6">You might also like</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {similarProducts.map((similarProduct) => (
                  <div
                    key={similarProduct.product_id}
                    className="bg-card rounded-lg border border-border overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => navigate(`/product/${similarProduct.product_id}`)}
                  >
                    <div className="aspect-square bg-muted/30">
                      <img
                        src={similarProduct.image_url}
                        alt={similarProduct.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-foreground mb-2 line-clamp-2">
                        {similarProduct.name}
                      </h3>
                      <div className="flex items-center gap-2 mb-2">
                        <div className="flex gap-1">
                          {renderStars(similarProduct.average_rating ?? similarProduct.rating ?? 0)}
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {((similarProduct.average_rating ?? similarProduct.rating) || 0).toFixed(1)}
                        </span>
                      </div>
                      <DiscountPrice 
                        price={similarProduct.price}
                        discountPercent={similarProduct.discount_percent}
                        size="lg"
                        layout="vertical"
                        alignment="left"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </main>

      <Footer />
      
      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        action={authAction}
      />
    </div>
  );
};

export default ProductPage;
