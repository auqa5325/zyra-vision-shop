import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { 
  Heart, 
  ShoppingCart, 
  ArrowLeft,
  Trash2,
  Calendar
} from "lucide-react";
import { useWishlist } from "@/hooks/useWishlist";
import { useCart } from "@/hooks/useCart";
import { useAuth } from "@/contexts/AuthContext";
import { AuthModal } from "@/components/AuthModal";
import { WishlistItem } from "@/hooks/useWishlist";
import { useEffect } from "react";

const WishlistPage = () => {
  const navigate = useNavigate();
  const { wishlist, removeFromWishlist, clearWishlist, moveToCart } = useWishlist();
  const { addToCart } = useCart();
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Page view tracking removed as requested

  const handleProductClick = (productId: string) => {
    navigate(`/product/${productId}`);
  };

  const handleAddToCart = async (item: WishlistItem) => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }
    
    // Move from wishlist to cart (removes from wishlist and adds to cart)
    await moveToCart({
      product_id: item.product_id,
      name: item.name,
      price: item.price,
      image_url: item.image_url,
      short_description: item.short_description || '',
      long_description: item.long_description || '',
      category_id: item.category_id || 0,
      tags: item.tags || [],
      currency: item.currency || 'INR',
      brand: item.brand || '',
      available: item.available || true,
      created_at: item.created_at || new Date().toISOString(),
      updated_at: item.updated_at || new Date().toISOString(),
      metadata_json: item.metadata_json || {}
    });
  };

  const handleRemoveFromWishlist = (productId: string) => {
    const item = wishlist.find(item => item.product_id === productId);
    
    removeFromWishlist(productId);
  };

  if (wishlist.length === 0) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <CardContent className="p-8 text-center">
              <Heart className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <h2 className="text-2xl font-bold mb-2">Your Wishlist is Empty</h2>
              <p className="text-muted-foreground mb-6">
                Save products you love to your wishlist.
              </p>
              <Button onClick={() => navigate("/")} className="w-full">
                Start Shopping
              </Button>
            </CardContent>
          </Card>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />
      
      <main className="flex-1">
        <div className="container px-4 py-4 sm:py-6 lg:py-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4 mb-6 sm:mb-8">
            <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate("/")}
                className="flex items-center gap-2 w-fit"
              >
                <ArrowLeft className="w-4 h-4" />
                Continue Shopping
              </Button>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold">My Wishlist</h1>
                <p className="text-sm sm:text-base text-muted-foreground">
                  {wishlist.length} {wishlist.length === 1 ? 'item' : 'items'} saved
                </p>
              </div>
            </div>
            
            <Button 
              variant="outline" 
              onClick={clearWishlist}
              className="text-destructive hover:text-destructive w-full sm:w-auto"
              size="sm"
            >
              Clear All
            </Button>
          </div>

          {/* Wishlist Items */}
          <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-6">
            {wishlist.map((item: WishlistItem) => (
              <Card key={item.product_id} className="group hover:shadow-lg transition-shadow">
                <CardContent className="p-0">
                  {/* Product Image */}
                  <div 
                    className="relative aspect-square overflow-hidden cursor-pointer"
                    onClick={() => handleProductClick(item.product_id)}
                  >
                    <img 
                      src={item.image_url} 
                      alt={item.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    
                    {/* Remove from Wishlist Button */}
                    <Button
                      variant="ghost"
                      size="sm"
                      className="absolute top-1 right-1 sm:top-2 sm:right-2 bg-background/80 backdrop-blur-sm hover:bg-background h-6 w-6 sm:h-8 sm:w-8 p-0"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveFromWishlist(item.product_id);
                      }}
                    >
                      <Trash2 className="w-3 h-3 sm:w-4 sm:h-4 text-destructive" />
                    </Button>
                  </div>

                  {/* Product Details */}
                  <div className="p-3 sm:p-4">
                    <h3 
                      className="font-medium text-sm sm:text-base lg:text-lg mb-2 cursor-pointer hover:text-primary line-clamp-2"
                      onClick={() => handleProductClick(item.product_id)}
                    >
                      {item.name}
                    </h3>
                    
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3 gap-2">
                      <DiscountPrice 
                        price={item.price}
                        discountPercent={item.discount_percent}
                        size="2xl"
                        layout="vertical"
                        alignment="left"
                      />
                      <Badge variant="secondary" className="text-xs w-fit">
                        <Calendar className="w-3 h-3 mr-1" />
                        {new Date(item.added_at).toLocaleDateString()}
                      </Badge>
                    </div>

                    {/* Add to Cart Button */}
                    <Button 
                      className="w-full" 
                      onClick={() => handleAddToCart(item)}
                      size="sm"
                    >
                      <ShoppingCart className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                      <span className="text-xs sm:text-sm">Add to Cart</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Summary */}
          <Card className="mt-6 sm:mt-8">
            <CardContent className="p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-base sm:text-lg font-semibold">Wishlist Summary</h3>
                  <p className="text-sm text-muted-foreground">
                    {wishlist.length} items • Total value: ₹{wishlist.reduce((sum, item) => sum + item.price, 0).toLocaleString()}
                  </p>
                </div>
                <Button 
                  size="sm"
                  onClick={() => {
                    wishlist.forEach(item => handleAddToCart(item));
                    clearWishlist();
                  }}
                  className="w-full sm:w-auto"
                >
                  <ShoppingCart className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  Add All to Cart
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
      
      <Footer />
      
      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        action="cart"
      />
    </div>
  );
};

export default WishlistPage;