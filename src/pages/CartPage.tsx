import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { 
  ShoppingCart, 
  Plus, 
  Minus, 
  Trash2, 
  ArrowLeft,
  CreditCard,
  AlertCircle,
  Heart
} from "lucide-react";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { useAuth } from "@/contexts/AuthContext";
import { AuthModal } from "@/components/AuthModal";
import { CartItem } from "@/hooks/useCart";
import { interactionService } from "@/services/interactionService";
import { useEffect } from "react";

const CartPage = () => {
  const navigate = useNavigate();
  const { cart, updateQuantity, removeFromCart, clearCart, checkout } = useCart();
  const { toggleWishlist, isInWishlist } = useWishlist();
  const { user } = useAuth();
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Page view tracking removed as requested

  const handleProductClick = (productId: string) => {
    navigate(`/product/${productId}`);
  };

  const handleQuantityChange = async (productId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
    } else {
      await updateQuantity(productId, newQuantity);
    }
  };

  const handleAddToWishlist = (item: CartItem) => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }
    
    toggleWishlist(item);
  };

  const handleCheckout = async () => {
    setIsCheckingOut(true);
    try {
      await checkout();
      
      // Track purchase interactions for each item
      const totalValue = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      for (const item of cart.items) {
        interactionService.trackPurchase(item.product_id, item.price * item.quantity, {
          page: 'cart_checkout',
          product_name: item.name,
          product_id: item.product_id,
          quantity: item.quantity,
          unit_price: item.price,
          total_item_value: item.price * item.quantity,
          total_cart_value: totalValue,
          cart_items_count: cart.items.length,
          timestamp: new Date().toISOString()
        });
      }
      
      navigate("/profile");
    } catch (error) {
      console.error('Checkout failed:', error);
    } finally {
      setIsCheckingOut(false);
    }
  };

  if (cart.items.length === 0) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <CardContent className="p-8 text-center">
              <ShoppingCart className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <h2 className="text-2xl font-bold mb-2">Your Cart is Empty</h2>
              <p className="text-muted-foreground mb-6">
                Add some products to your cart to get started.
              </p>
              <Button onClick={() => navigate("/")} className="w-full">
                Continue Shopping
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
        <div className="container px-4 py-8">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate("/")}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Continue Shopping
            </Button>
            <div>
              <h1 className="text-3xl font-bold">Shopping Cart</h1>
              <p className="text-muted-foreground">
                {cart.totalItems} {cart.totalItems === 1 ? 'item' : 'items'} in your cart
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShoppingCart className="w-5 h-5" />
                    Cart Items
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y">
                    {cart.items.map((item: CartItem) => (
                      <div key={item.product_id} className="p-6">
                        <div className="flex items-center gap-4">
                          {/* Product Image */}
                          <div 
                            className="w-20 h-20 rounded-lg overflow-hidden cursor-pointer"
                            onClick={() => handleProductClick(item.product_id)}
                          >
                            <img 
                              src={item.image_url} 
                              alt={item.name}
                              className="w-full h-full object-cover hover:scale-105 transition-transform"
                            />
                          </div>

                          {/* Product Details */}
                          <div className="flex-1 min-w-0">
                            <h3 
                              className="font-medium text-lg cursor-pointer hover:text-primary"
                              onClick={() => handleProductClick(item.product_id)}
                            >
                              {item.name}
                            </h3>
                            <DiscountPrice 
                              price={item.price}
                              discountPercent={item.discount_percent}
                              size="sm"
                              layout="vertical"
                              alignment="left"
                              className="text-sm"
                            />
                            <p className="text-muted-foreground text-xs">
                              Added on {item.last_added ? new Date(item.last_added).toLocaleDateString() : 'Recently'}
                            </p>
                          </div>

                          {/* Quantity Controls */}
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleQuantityChange(item.product_id, item.quantity - 1)}
                              disabled={item.quantity <= 1}
                            >
                              <Minus className="w-4 h-4" />
                            </Button>
                            <span className="w-12 text-center font-medium">
                              {item.quantity}
                            </span>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleQuantityChange(item.product_id, item.quantity + 1)}
                            >
                              <Plus className="w-4 h-4" />
                            </Button>
                          </div>

                          {/* Price */}
                          <div className="text-right">
                            <p className="font-bold text-lg">
                              ₹{(item.price * item.quantity).toLocaleString()}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {item.quantity} × ₹{item.price.toLocaleString()}
                            </p>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex flex-col gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleAddToWishlist(item)}
                              className={`flex items-center gap-2 ${
                                isInWishlist(item.product_id) 
                                  ? 'text-red-500 hover:text-red-600' 
                                  : 'text-muted-foreground hover:text-red-500'
                              }`}
                            >
                              <Heart className={`w-4 h-4 ${isInWishlist(item.product_id) ? 'fill-current' : ''}`} />
                              {isInWishlist(item.product_id) ? 'In Wishlist' : 'Add to Wishlist'}
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeFromCart(item.product_id)}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="w-4 h-4" />
                              Remove
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <Card className="sticky top-4">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="w-5 h-5" />
                    Order Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Items ({cart.totalItems})</span>
                      <span>₹{cart.totalPrice.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Shipping</span>
                      <span className="text-green-600">FREE</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Tax</span>
                      <span>₹0</span>
                    </div>
                    <div className="border-t pt-2">
                      <div className="flex justify-between font-bold text-lg">
                        <span>Total</span>
                        <span>₹{cart.totalPrice.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <Button 
                    className="w-full" 
                    size="lg"
                    onClick={handleCheckout}
                    disabled={isCheckingOut}
                  >
                    {isCheckingOut ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <CreditCard className="w-4 h-4 mr-2" />
                        Proceed to Checkout
                      </>
                    )}
                  </Button>

                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={clearCart}
                  >
                    Clear Cart
                  </Button>

                  <div className="text-xs text-muted-foreground text-center">
                    <AlertCircle className="w-4 h-4 inline mr-1" />
                    Secure checkout with SSL encryption
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
      
      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        action="wishlist"
      />
    </div>
  );
};

export default CartPage;