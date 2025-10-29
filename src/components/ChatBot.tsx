import { useState, useEffect } from "react";
import { MessageCircle, X, Send, RotateCcw, Loader2, ShoppingCart, Heart, ExternalLink, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { chatbotService, ChatMessage, ProductSuggestion } from "@/services/chatbotService";
import { useAuth } from "@/hooks/useAuth";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { productService } from "@/services/productService";
import { dualTrackingService } from "@/services/dualTrackingService";
import { useNavigate } from "react-router-dom";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  products?: ProductSuggestion[];
}

export const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hi! I'm Zyra, your AI shopping assistant powered by Gemini. How can I help you find the perfect product today?",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHealthy, setIsHealthy] = useState(true);
  const [productDetails, setProductDetails] = useState<Record<string, any>>({});
  const [loadingProducts, setLoadingProducts] = useState<Set<string>>(new Set());
  
  const { user } = useAuth();
  const { addToCart } = useCart();
  const { addToWishlist } = useWishlist();
  const navigate = useNavigate();

  // Check chatbot health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthy = await chatbotService.checkHealth();
        setIsHealthy(healthy);
        if (!healthy) {
          console.warn('⚠️ [CHATBOT] Service is not healthy');
        }
      } catch (error) {
        console.error('❌ [CHATBOT] Health check failed:', error);
        setIsHealthy(false);
      }
    };
    
    checkHealth();
  }, []);

  // Load product details when products are shown
  useEffect(() => {
    const loadAllProductDetails = async () => {
      const allProducts = messages
        .flatMap(msg => msg.products || [])
        .map(product => product.product_id);
      
      for (const productId of allProducts) {
        if (!productDetails[productId] && !loadingProducts.has(productId)) {
          await loadProductDetails(productId);
        }
      }
    };
    
    loadAllProductDetails();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Convert messages to ChatMessage format
      const chatMessages: ChatMessage[] = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Send to Gemini API
      const response = await chatbotService.sendMessage(chatMessages, user?.user_id);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.message,
        products: response.products
      };
      
      setMessages((prev) => [...prev, aiMessage]);
      
      // Add suggestions if available
      if (response.suggestions && response.suggestions.length > 0) {
        const suggestionMessage: Message = {
          id: (Date.now() + 2).toString(),
          role: "assistant",
          content: `💡 Suggestions: ${response.suggestions.join(", ")}`,
        };
        setMessages((prev) => [...prev, suggestionMessage]);
      }
      
    } catch (error) {
      console.error('❌ [CHATBOT] Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: chatbotService.getErrorMessage().content,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestart = () => {
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: chatbotService.getInitialMessage().content,
      },
    ]);
  };

  // Load product details when products are shown
  const loadProductDetails = async (productId: string) => {
    if (productDetails[productId] || loadingProducts.has(productId)) return;
    
    setLoadingProducts(prev => new Set(prev).add(productId));
    try {
      const details = await productService.getProductById(productId);
      setProductDetails(prev => ({ ...prev, [productId]: details }));
    } catch (error) {
      console.error('Failed to load product details:', error);
    } finally {
      setLoadingProducts(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
  };

  // Handle adding to cart
  const handleAddToCart = async (product: ProductSuggestion) => {
    try {
      const productDetails = await productService.getProductById(product.product_id);
      const result = await dualTrackingService.addToCart(productDetails, 1);
      
      if (result.success) {
        // Add success message to chat
        const successMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: `✅ Added "${product.name}" to your cart!`,
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Failed to add to cart:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `❌ Failed to add "${product.name}" to cart. Please try again.`,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Handle adding to wishlist
  const handleAddToWishlist = async (product: ProductSuggestion) => {
    try {
      const productDetails = await productService.getProductById(product.product_id);
      const result = await dualTrackingService.addToWishlist(productDetails);
      
      if (result.success) {
        // Add success message to chat
        const successMessage: Message = {
          id: Date.now().toString(),
          role: "assistant",
          content: `❤️ Added "${product.name}" to your wishlist!`,
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `❌ Failed to add "${product.name}" to wishlist. Please try again.`,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Handle viewing product details
  const handleViewProduct = (productId: string) => {
    navigate(`/product/${productId}`);
    setIsOpen(false); // Close chatbot when navigating
  };

  return (
    <>
      {/* Floating Button */}
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-glow z-40"
        variant="gradient"
        size="icon"
      >
        <MessageCircle className="h-6 w-6" />
      </Button>

      {/* Chat Drawer */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setIsOpen(false)}
          />

          {/* Drawer */}
          <div className="fixed top-0 right-0 h-full w-full md:w-96 bg-background border-l shadow-2xl z-50 flex flex-col animate-slide-in-right">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-primary/5 to-secondary/5">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <MessageCircle className="h-5 w-5 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Zyra AI</h3>
                  <p className="text-xs text-muted-foreground">
                    Powered by Gemini {isHealthy ? "🟢" : "🔴"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleRestart}
                  className="h-8 w-8"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    } animate-fade-in`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                        message.role === "user"
                          ? "bg-gradient-to-r from-primary to-secondary text-primary-foreground"
                          : "bg-muted text-foreground"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      
                      {/* Product Suggestions */}
                      {message.products && message.products.length > 0 && (
                        <div className="mt-3 space-y-3">
                          <p className="text-xs font-medium text-muted-foreground">Recommended Products:</p>
                          {message.products.map((product) => {
                            const details = productDetails[product.product_id];
                            const isLoading = loadingProducts.has(product.product_id);
                            
                            return (
                              <Card key={product.product_id} className="bg-background/50 border-muted hover:border-primary/20 transition-colors">
                                <CardContent className="p-4">
                                  <div className="flex items-start gap-3">
                                    {product.image_url && (
                                      <img
                                        src={product.image_url}
                                        alt={product.name}
                                        className="w-16 h-16 rounded-lg object-cover flex-shrink-0"
                                      />
                                    )}
                                    <div className="flex-1 min-w-0">
                                      <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                          <h4 className="text-sm font-medium truncate">{product.name}</h4>
                                          <div className="flex items-center gap-2 mt-1">
                                            <DiscountPrice 
                                              price={product.price}
                                              discountPercent={product.discount_percent}
                                              size="sm"
                                              layout="compact"
                                              alignment="left"
                                            />
                                            {details && (
                                              <div className="flex items-center gap-1">
                                                <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                                                <span className="text-xs text-muted-foreground">{details.rating?.toFixed(1) || '0.0'}</span>
                                              </div>
                                            )}
                                          </div>
                                          {details && (
                                            <div className="flex items-center gap-1 mt-1">
                                              <Badge variant="secondary" className="text-xs px-1 py-0">
                                                {details.category || 'General'}
                                              </Badge>
                                            </div>
                                          )}
                                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{product.reason}</p>
                                        </div>
                                        <div className="flex flex-col gap-1">
                                          <Button 
                                            size="sm" 
                                            variant="outline" 
                                            className="h-8 w-8 p-0 hover:bg-primary hover:text-primary-foreground"
                                            onClick={() => handleAddToCart(product)}
                                            disabled={isLoading}
                                          >
                                            <ShoppingCart className="h-4 w-4" />
                                          </Button>
                                          <Button 
                                            size="sm" 
                                            variant="outline" 
                                            className="h-8 w-8 p-0 hover:bg-red-500 hover:text-white"
                                            onClick={() => handleAddToWishlist(product)}
                                            disabled={isLoading}
                                          >
                                            <Heart className="h-4 w-4" />
                                          </Button>
                                          <Button 
                                            size="sm" 
                                            variant="outline" 
                                            className="h-8 w-8 p-0 hover:bg-blue-500 hover:text-white"
                                            onClick={() => handleViewProduct(product.product_id)}
                                          >
                                            <ExternalLink className="h-4 w-4" />
                                          </Button>
                                        </div>
                                      </div>
                                      {isLoading && (
                                        <div className="flex items-center gap-2 mt-2">
                                          <Loader2 className="h-3 w-3 animate-spin" />
                                          <span className="text-xs text-muted-foreground">Loading details...</span>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {isLoading && (
                <div className="flex justify-start animate-fade-in">
                  <div className="max-w-[80%] rounded-2xl px-4 py-2 bg-muted text-foreground">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <p className="text-sm">Zyra is thinking...</p>
                    </div>
                  </div>
                </div>
              )}
            </ScrollArea>

            {/* Input */}
            <div className="p-4 border-t bg-muted/30">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask Zyra anything..."
                  className="flex-1 bg-background"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSendMessage}
                  variant="gradient"
                  size="icon"
                  className="shrink-0"
                  disabled={isLoading || !inputValue.trim()}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                Powered by Gemini AI • Always learning
              </p>
            </div>
          </div>
        </>
      )}
    </>
  );
};
