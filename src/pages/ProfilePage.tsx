import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  User, 
  ShoppingCart, 
  Heart, 
  Package, 
  DollarSign,
  ArrowRight,
  Activity,
  Loader2
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { useUserDataSync } from "@/hooks/useUserDataSync";
import { reviewService, ReviewWithUser } from "@/services/reviewService";
import { interactionService } from "@/services/interactionService";
import { Star, MessageSquare } from "lucide-react";

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { cart } = useCart();
  const { wishlist } = useWishlist();
  const { userStats, isLoading } = useUserDataSync();
  const [userReviews, setUserReviews] = useState<ReviewWithUser[]>([]);
  const [reviewsLoading, setReviewsLoading] = useState(false);

  // Load user reviews
  const loadUserReviews = async () => {
    if (!user?.user_id) return;
    
    try {
      setReviewsLoading(true);
      const reviews = await reviewService.getUserReviews(user.user_id, 1, 10);
      setUserReviews(reviews || []);
    } catch (error) {
      console.error('Failed to load user reviews:', error);
      setUserReviews([]);
    } finally {
      setReviewsLoading(false);
    }
  };

  // Load reviews on component mount
  useEffect(() => {
    if (isAuthenticated && user) {
      loadUserReviews();
    }
  }, [isAuthenticated, user]);

  // Listen for new review submissions to refresh the list
  useEffect(() => {
    const handleReviewSubmitted = () => {
      if (isAuthenticated && user) {
        loadUserReviews();
      }
    };

    window.addEventListener('reviewSubmitted', handleReviewSubmitted);
    return () => {
      window.removeEventListener('reviewSubmitted', handleReviewSubmitted);
    };
  }, [isAuthenticated, user]);

  // Show login prompt if not authenticated
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center p-4">
          <Card className="w-full max-w-md">
            <CardContent className="p-8 text-center">
              <User className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
              <h2 className="text-2xl font-bold mb-2">Please Log In</h2>
              <p className="text-muted-foreground mb-6">
                You need to be logged in to view your profile.
              </p>
              <Button onClick={() => navigate("/login")} className="w-full">
                Go to Login
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
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Welcome back, {user.username}!</h1>
            <p className="text-muted-foreground">
              Here's an overview of your account activity.
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Cart Items</p>
                    <p className="text-2xl font-bold">{cart.totalItems}</p>
                  </div>
                  <ShoppingCart className="w-8 h-8 text-blue-500" />
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-4"
                  onClick={() => navigate("/cart")}
                >
                  View Cart
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Wishlist</p>
                    <p className="text-2xl font-bold">{wishlist.length}</p>
                  </div>
                  <Heart className="w-8 h-8 text-red-500" />
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-4"
                  onClick={() => navigate("/wishlist")}
                >
                  View Wishlist
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Purchases</p>
                    <p className="text-2xl font-bold">{userStats?.purchases?.length || 0}</p>
                  </div>
                  <Package className="w-8 h-8 text-green-500" />
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full mt-4"
                  onClick={() => navigate("/purchases")}
                >
                  View Purchases
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Activity Summary */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Activity Summary
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span className="text-muted-foreground">Loading activity data...</span>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3">Recent Activity</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm p-3 rounded-lg bg-muted/30 hover:bg-primary/10 transition-all duration-300 hover:scale-105 hover:shadow-md cursor-pointer group">
                        <span className="text-muted-foreground group-hover:text-primary transition-colors">Total Interactions</span>
                        <Badge variant="secondary" className="group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-300 group-hover:scale-110">
                          {userStats?.total_interactions || 0}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm p-3 rounded-lg bg-muted/30 hover:bg-green-500/10 transition-all duration-300 hover:scale-105 hover:shadow-md cursor-pointer group">
                        <span className="text-muted-foreground group-hover:text-green-600 transition-colors">Total Spent</span>
                        <Badge variant="secondary" className="group-hover:bg-green-500 group-hover:text-white transition-all duration-300 group-hover:scale-110">
                          ₹{userStats?.totalSpent?.toLocaleString() || 0}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm p-3 rounded-lg bg-muted/30 hover:bg-blue-500/10 transition-all duration-300 hover:scale-105 hover:shadow-md cursor-pointer group">
                        <span className="text-muted-foreground group-hover:text-blue-600 transition-colors">Last Activity</span>
                        <Badge variant="outline" className="group-hover:bg-blue-500 group-hover:text-white group-hover:border-blue-500 transition-all duration-300 group-hover:scale-110">
                          {userStats?.last_activity 
                            ? new Date(userStats.last_activity).toLocaleDateString()
                            : 'Never'
                          }
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-3">Interaction Types</h3>
                    <div className="space-y-3">
                      {userStats?.event_types && Object.entries(userStats.event_types).map(([type, count], index) => {
                        const colors = [
                          'hover:bg-purple-500/10 group-hover:text-purple-600 group-hover:bg-purple-500 group-hover:text-white',
                          'hover:bg-orange-500/10 group-hover:text-orange-600 group-hover:bg-orange-500 group-hover:text-white',
                          'hover:bg-pink-500/10 group-hover:text-pink-600 group-hover:bg-pink-500 group-hover:text-white',
                          'hover:bg-indigo-500/10 group-hover:text-indigo-600 group-hover:bg-indigo-500 group-hover:text-white',
                          'hover:bg-teal-500/10 group-hover:text-teal-600 group-hover:bg-teal-500 group-hover:text-white'
                        ];
                        const colorClass = colors[index % colors.length];
                        
                        return (
                          <div key={type} className={`flex items-center justify-between text-sm p-3 rounded-lg bg-muted/30 transition-all duration-300 hover:scale-105 hover:shadow-md cursor-pointer group ${colorClass.split(' ')[0]}`}>
                            <span className={`text-muted-foreground capitalize transition-colors ${colorClass.split(' ')[1]}`}>
                              {type.replace('_', ' ')}
                            </span>
                            <Badge variant="outline" className={`transition-all duration-300 group-hover:scale-110 ${colorClass.split(' ').slice(2).join(' ')}`}>
                              {count as number}
                            </Badge>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Purchases */}
          {userStats?.purchases && userStats.purchases.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package className="w-5 h-5" />
                  Recent Purchases
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {userStats.purchases.slice(0, 3).map((purchase: any) => (
                    <div 
                      key={purchase.product_id}
                      className="flex items-center gap-4 p-4 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => navigate(`/product/${purchase.product_id}`)}
                    >
                      <img 
                        src={purchase.image_url} 
                        alt={purchase.name}
                        className="w-16 h-16 rounded-lg object-cover"
                      />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium truncate">{purchase.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          ₹{purchase.price?.toLocaleString() || 0}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Purchased on {new Date(purchase.purchased_at).toLocaleDateString()}
                        </p>
                      </div>
                      <ArrowRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  ))}
                  
                  {userStats.purchases.length > 3 && (
                    <div className="text-center pt-4">
                      <Button 
                        variant="outline" 
                        onClick={() => navigate("/purchases")}
                      >
                        View All Purchases ({userStats.purchases.length})
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* User Reviews Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                My Reviews
                {reviewsLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {reviewsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mr-2" />
                  <span className="text-muted-foreground">Loading reviews...</span>
                </div>
              ) : userReviews.length > 0 ? (
                <div className="space-y-4">
                  {userReviews.map((review) => (
                    <div 
                      key={review.review_id}
                      className="p-4 rounded-lg border hover:bg-muted/50 cursor-pointer transition-colors"
                      onClick={() => {
                        // Track review view interaction
                        interactionService.trackView(review.product_id, {
                          page: 'profile',
                          product_id: review.product_id,
                          review_id: review.review_id,
                          action: 'view_review',
                          timestamp: new Date().toISOString()
                        });
                        navigate(`/product/${review.product_id}`);
                      }}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`w-4 h-4 ${
                                  i < review.rating 
                                    ? 'text-yellow-400 fill-current' 
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                          </div>
                          <span className="text-sm font-medium">{review.rating}/5</span>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {new Date(review.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      
                      {review.title && (
                        <h4 className="font-semibold text-foreground mb-2">{review.title}</h4>
                      )}
                      
                      {review.comment && (
                        <p className="text-muted-foreground text-sm mb-2 line-clamp-2">
                          {review.comment}
                        </p>
                      )}
                      
                      <div className="text-xs text-muted-foreground">
                        Product: {review.product_name || 'Unknown Product'}
                      </div>
                    </div>
                  ))}
                  
                  <div className="text-center pt-4">
                    <Button 
                      variant="outline" 
                    >
                      View All Reviews ({userReviews.length})
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-semibold mb-2">No Reviews Yet</h3>
                  <p className="text-muted-foreground mb-4">
                    You haven't written any reviews yet. Start by reviewing products you've purchased!
                  </p>
                  <Button 
                    variant="outline" 
                    onClick={() => navigate("/purchases")}
                  >
                    View Purchases
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default ProfilePage;