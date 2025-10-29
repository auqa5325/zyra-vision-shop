import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { X, Filter, RotateCcw } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export interface FilterOptions {
  priceRange: [number, number];
  brands: string[];
  subcategories: number[];
  minRating: number;
  inStock: boolean;
  discountRange: [number, number];
  hasDiscount: boolean;
}

export interface SortOptions {
  field: 'name' | 'price' | 'rating' | 'created_at' | 'discount_percent' | 'discounted_price';
  direction: 'asc' | 'desc';
}

interface FilterModalProps {
  onApplyFilters: (filters: FilterOptions) => void;
  onClearFilters: () => void;
  currentFilters: FilterOptions;
  productCount: number;
  availableBrands: string[];
  availableSubcategories: Array<{id: number, name: string}>;
  priceRange: [number, number];
}

export const FilterModal = ({ 
  onApplyFilters, 
  onClearFilters, 
  currentFilters, 
  productCount,
  availableBrands,
  availableSubcategories,
  priceRange
}: FilterModalProps) => {
  const [localFilters, setLocalFilters] = useState<FilterOptions>(currentFilters);
  const [isOpen, setIsOpen] = useState(false);

  // Sync local filters with currentFilters prop when it changes
  useEffect(() => {
    setLocalFilters(currentFilters);
  }, [currentFilters]);

  const handleApply = () => {
    onApplyFilters(localFilters);
    setIsOpen(false);
  };

  const handleClear = () => {
    const defaultFilters: FilterOptions = {
      priceRange: priceRange,
      brands: [],
      subcategories: [],
      minRating: 0,
      inStock: false,
      discountRange: [0, 100],
      hasDiscount: false,
    };
    setLocalFilters(defaultFilters);
    onClearFilters();
    setIsOpen(false);
  };

  const updatePriceRange = (value: number[]) => {
    setLocalFilters(prev => ({ ...prev, priceRange: value as [number, number] }));
  };

  const toggleBrand = (brand: string) => {
    const currentBrands = localFilters.brands || [];
    setLocalFilters(prev => ({
      ...prev,
      brands: currentBrands.includes(brand)
        ? currentBrands.filter(b => b !== brand)
        : [...currentBrands, brand]
    }));
  };

  const toggleSubcategory = (subcategoryId: number) => {
    const currentSubcategories = localFilters.subcategories || [];
    setLocalFilters(prev => ({
      ...prev,
      subcategories: currentSubcategories.includes(subcategoryId)
        ? currentSubcategories.filter(id => id !== subcategoryId)
        : [...currentSubcategories, subcategoryId]
    }));
  };

  const updateMinRating = (value: number[]) => {
    setLocalFilters(prev => ({ ...prev, minRating: value[0] }));
  };

  const toggleInStock = (checked: boolean) => {
    setLocalFilters(prev => ({ ...prev, inStock: checked }));
  };

  const updateDiscountRange = (value: number[]) => {
    setLocalFilters(prev => ({ ...prev, discountRange: value as [number, number] }));
  };

  const toggleHasDiscount = (checked: boolean) => {
    setLocalFilters(prev => ({ ...prev, hasDiscount: checked }));
  };

  const hasActiveFilters = 
    (currentFilters.brands && currentFilters.brands.length > 0) ||
    (currentFilters.subcategories && currentFilters.subcategories.length > 0) ||
    currentFilters.minRating > 0 ||
    currentFilters.inStock ||
    currentFilters.hasDiscount ||
    (currentFilters.discountRange[0] > 0 || currentFilters.discountRange[1] < 100);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <Filter className="w-4 h-4" />
          Filters
          {hasActiveFilters && (
            <Badge variant="secondary" className="ml-1 px-1.5 py-0.5 text-xs">
              {(currentFilters.brands ? currentFilters.brands.length : 0) + 
               (currentFilters.subcategories ? currentFilters.subcategories.length : 0) +
               (currentFilters.minRating > 0 ? 1 : 0) + 
               (currentFilters.inStock ? 1 : 0) +
               (currentFilters.hasDiscount ? 1 : 0) +
               (currentFilters.discountRange[0] > 0 || currentFilters.discountRange[1] < 100 ? 1 : 0)}
            </Badge>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Filter Products</span>
            <span className="text-sm font-normal text-muted-foreground">
              {productCount} products
            </span>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Maximum Price */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Maximum Price</Label>
            <div className="px-3">
              <Slider
                value={[localFilters.priceRange[1]]}
                onValueChange={(value) => updatePriceRange([priceRange[0], value[0]])}
                max={priceRange[1]}
                min={priceRange[0]}
                step={Math.max(1, Math.floor((priceRange[1] - priceRange[0]) / 100))}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-muted-foreground mt-2">
                <span>₹{priceRange[0]}</span>
                <span>₹{localFilters.priceRange[1]}</span>
              </div>
            </div>
          </div>

          {/* Brands */}
          {availableBrands && availableBrands.length > 0 && (
            <div className="space-y-3">
              <Label className="text-base font-semibold">Brands</Label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                {availableBrands.map((brand) => (
                  <div key={brand} className="flex items-center space-x-2">
                    <Checkbox
                      id={brand}
                      checked={(localFilters.brands || []).includes(brand)}
                      onCheckedChange={() => toggleBrand(brand)}
                    />
                    <Label
                      htmlFor={brand}
                      className="text-sm font-normal cursor-pointer"
                    >
                      {brand}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Minimum Rating */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Minimum Rating</Label>
            <div className="px-3">
              <Slider
                value={[localFilters.minRating]}
                onValueChange={updateMinRating}
                max={5}
                min={0}
                step={0.5}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-muted-foreground mt-2">
                <span>Any</span>
                <span>{localFilters.minRating} ⭐</span>
              </div>
            </div>
          </div>

          {/* Discount Range */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Discount Range</Label>
            <div className="px-3">
              <Slider
                value={localFilters.discountRange}
                onValueChange={updateDiscountRange}
                max={100}
                min={0}
                step={5}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-muted-foreground mt-2">
                <span>{localFilters.discountRange[0]}%</span>
                <span>{localFilters.discountRange[1]}%</span>
              </div>
            </div>
          </div>

          {/* Has Discount Only */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="hasDiscount"
              checked={localFilters.hasDiscount}
              onCheckedChange={toggleHasDiscount}
            />
            <Label htmlFor="hasDiscount" className="text-sm font-normal cursor-pointer">
              Discounted Items Only
            </Label>
          </div>

          {/* In Stock Only */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="inStock"
              checked={localFilters.inStock}
              onCheckedChange={toggleInStock}
            />
            <Label htmlFor="inStock" className="text-sm font-normal cursor-pointer">
              In Stock Only
            </Label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleClear}
            className="flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Clear All
          </Button>
          <Button onClick={handleApply} className="flex-1">
            Apply Filters
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
