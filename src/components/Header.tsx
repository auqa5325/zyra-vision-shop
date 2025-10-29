import { useState, useEffect } from "react";
import { Search, ShoppingCart, User, Menu, X, Sun, Moon, LogOut, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SearchInput } from "@/components/SearchInput";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useCart } from "@/hooks/useCart";
import { useWishlist } from "@/hooks/useWishlist";

export const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isDark, setIsDark] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [mobileSearchQuery, setMobileSearchQuery] = useState("");
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const { cart, refreshCart } = useCart();
  const { wishlist, refreshWishlist } = useWishlist();

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // Listen for cart/wishlist updates from other components
  useEffect(() => {
    const handleCartUpdate = () => {
      refreshCart();
    };

    const handleWishlistUpdate = () => {
      refreshWishlist();
    };

    // Listen for custom events
    window.addEventListener('cartUpdated', handleCartUpdate);
    window.addEventListener('wishlistUpdated', handleWishlistUpdate);

    return () => {
      window.removeEventListener('cartUpdated', handleCartUpdate);
      window.removeEventListener('wishlistUpdated', handleWishlistUpdate);
    };
  }, [refreshCart, refreshWishlist]);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        {/* Logo */}
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/")}>
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-secondary" />
            <span className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              sandh.ai
            </span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <button 
              onClick={() => navigate("/")}
              className="text-sm font-medium text-foreground hover:text-primary transition-colors"
            >
              Home
            </button>
            <button 
              onClick={() => navigate("/profile")}
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              Profile
            </button>
            <button 
              onClick={() => navigate("/wishlist")}
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              Wishlist
            </button>
          </nav>
        </div>

        {/* Search Bar - Desktop */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <SearchInput
            placeholder="Search products..."
            className="w-full"
            initialValue={searchQuery}
            onSearch={(query) => {
              setSearchQuery(query);
              navigate(`/search?q=${encodeURIComponent(query)}`);
            }}
          />
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <Button variant="ghost" size="icon" onClick={() => setIsDark(!isDark)}>
            {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          {/* Wishlist */}
          <Button 
            variant="ghost" 
            size="icon" 
            className="relative"
            onClick={() => navigate("/wishlist")}
          >
            <Heart className="h-5 w-5" />
            {wishlist.length > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-medium">
                {wishlist.length}
              </span>
            )}
          </Button>

          {/* Cart */}
          <Button 
            variant="ghost" 
            size="icon" 
            className="relative"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              navigate("/cart");
            }}
          >
            <ShoppingCart className="h-5 w-5" />
            {cart.totalItems > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-medium">
                {cart.totalItems}
              </span>
            )}
          </Button>

          {/* Profile */}
          {isAuthenticated ? (
            <Button 
              variant="ghost" 
              size="icon" 
              className="hidden md:flex"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                navigate("/profile");
              }}
            >
              <User className="h-5 w-5" />
            </Button>
          ) : (
            <Button 
              variant="ghost" 
              size="icon" 
              className="hidden md:flex"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                navigate("/login");
              }}
            >
              <User className="h-5 w-5" />
            </Button>
          )}

          {/* Login/Logout Button - Desktop */}
          {isAuthenticated ? (
            <div className="hidden md:flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                Welcome, {user?.username || user?.profile?.username || 'User'}
              </span>
              <Button variant="outline" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          ) : (
            <Button variant="outline" className="hidden md:flex" onClick={() => navigate("/login")}>
              Login
            </Button>
          )}

          {/* Mobile Menu Toggle */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t bg-background p-4 animate-fade-in">
          <div className="flex flex-col gap-4">
            {/* Mobile Search */}
            <SearchInput
              placeholder="Search products..."
              className="w-full"
              initialValue={mobileSearchQuery}
              onSearch={(query) => {
                setMobileSearchQuery(query);
                navigate(`/search?q=${encodeURIComponent(query)}`);
                setMobileMenuOpen(false);
              }}
            />

            {/* Mobile Navigation */}
            <nav className="flex flex-col gap-2">
              <a href="#" className="text-sm font-medium text-foreground hover:text-primary transition-colors py-2">
                Home
              </a>
              <a href="#categories" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors py-2">
                Categories
              </a>
              <a href="#deals" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors py-2">
                Deals
              </a>
            </nav>

            {isAuthenticated ? (
              <div className="w-full space-y-2">
                <div className="text-sm text-muted-foreground text-center">
                  Welcome, {user?.username || user?.profile?.username || 'User'}
                </div>
                <Button variant="outline" className="w-full" onClick={logout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            ) : (
              <Button variant="outline" className="w-full" onClick={() => navigate("/login")}>
                Login
              </Button>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
