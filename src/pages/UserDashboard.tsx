import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DiscountPrice } from "@/components/ui/DiscountPrice";
import { useUserDataSync } from "@/hooks/useUserDataSync";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";
import { useAuth } from "@/contexts/AuthContext";
import { RefreshCw, Database, ShoppingCart, Heart, CreditCard, BarChart3 } from "lucide-react";
import { useState } from "react";

const UserDashboard = () => {
  const { user } = useAuth();
  const { isLoading, userStats, refreshData } = useUserDataSync();
  const { cart } = useCart();
  const { wishlist } = useWishlist();
  const [showRawData, setShowRawData] = useState(false);

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Please log in to view your data</h1>
            <p className="text-muted-foreground">Your cart, wishlist, and purchase history will be displayed here.</p>
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
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold">User Dashboard</h1>
              <p className="text-muted-foreground">Welcome back, {user.username}!</p>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                onClick={refreshData}
                disabled={isLoading}
                variant="outline"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                {isLoading ? 'Syncing...' : 'Sync with DB'}
              </Button>
            </div>
          </div>

          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Local Cart</CardTitle>
                <ShoppingCart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{cart.totalItems}</div>
                <p className="text-xs text-muted-foreground">
                  ₹{cart.totalPrice.toLocaleString()}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Local Wishlist</CardTitle>
                <Heart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{wishlist.length}</div>
                <p className="text-xs text-muted-foreground">
                  Saved items
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">DB Interactions</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {userStats?.total_interactions || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Total tracked events
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Purchases</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {userStats?.purchases?.length || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  Completed orders
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Data Sources Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Local Storage Data */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  Local Storage Data
                </CardTitle>
                <CardDescription>
                  Data stored in browser's localStorage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">Cart Items ({cart.totalItems})</h4>
                    <div className="space-y-2">
                      {cart.items.slice(0, 3).map((item) => (
                        <div key={item.product_id} className="flex items-center justify-between p-2 bg-muted rounded">
                          <span className="text-sm">{item.name}</span>
                          <div className="flex flex-col items-end">
                            <DiscountPrice 
                              price={item.price}
                              discountPercent={item.discount_percent}
                              size="sm"
                              layout="compact"
                              alignment="right"
                              className="text-xs"
                            />
                            <span className="text-xs text-muted-foreground">× {item.quantity}</span>
                          </div>
                        </div>
                      ))}
                      {cart.items.length > 3 && (
                        <p className="text-sm text-muted-foreground">
                          +{cart.items.length - 3} more items
                        </p>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Wishlist Items ({wishlist.length})</h4>
                    <div className="space-y-2">
                      {wishlist.slice(0, 3).map((item) => (
                        <div key={item.product_id} className="flex items-center justify-between p-2 bg-muted rounded">
                          <span className="text-sm">{item.name}</span>
                          <DiscountPrice 
                            price={item.price}
                            discountPercent={item.discount_percent}
                            size="sm"
                            layout="compact"
                            alignment="right"
                            className="text-xs"
                          />
                        </div>
                      ))}
                      {wishlist.length > 3 && (
                        <p className="text-sm text-muted-foreground">
                          +{wishlist.length - 3} more items
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Database Data */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Database Interactions
                </CardTitle>
                <CardDescription>
                  Data fetched from PostgreSQL database
                </CardDescription>
              </CardHeader>
              <CardContent>
                {userStats ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Event Types</h4>
                      <div className="space-y-2">
                        {Object.entries(userStats.event_types || {}).map(([eventType, count]) => (
                          <div key={eventType} className="flex items-center justify-between p-2 bg-muted rounded">
                            <span className="text-sm capitalize">{eventType.replace('_', ' ')}</span>
                            <Badge variant="outline">{count as number}</Badge>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-2">Platforms</h4>
                      <div className="space-y-2">
                        {Object.entries(userStats.platforms || {}).map(([platform, count]) => (
                          <div key={platform} className="flex items-center justify-between p-2 bg-muted rounded">
                            <span className="text-sm">{platform}</span>
                            <Badge variant="outline">{count as number}</Badge>
                          </div>
                        ))}
                      </div>
                    </div>

                    {userStats.last_activity && (
                      <div>
                        <h4 className="font-semibold mb-2">Last Activity</h4>
                        <p className="text-sm text-muted-foreground">
                          {new Date(userStats.last_activity).toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Database className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No database data loaded</p>
                    <Button onClick={refreshData} className="mt-4" size="sm">
                      Load Data
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Raw Data Toggle */}
          <div className="mb-4">
            <Button
              variant="outline"
              onClick={() => setShowRawData(!showRawData)}
            >
              {showRawData ? 'Hide' : 'Show'} Raw Data
            </Button>
          </div>

          {/* Raw Data Display */}
          {showRawData && (
            <Card>
              <CardHeader>
                <CardTitle>Raw Database Response</CardTitle>
                <CardDescription>
                  Complete data structure returned from the API
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                  {JSON.stringify(userStats, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default UserDashboard;

