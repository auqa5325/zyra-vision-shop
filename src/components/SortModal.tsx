import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { SortAsc, SortDesc } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { SortOptions } from "./FilterModal";

interface SortModalProps {
  onApplySort: (sort: SortOptions) => void;
  currentSort: SortOptions;
  productCount: number;
}

const SORT_OPTIONS = [
  { value: 'name', label: 'Name', icon: SortAsc },
  { value: 'price', label: 'Price', icon: SortAsc },
  { value: 'rating', label: 'Rating', icon: SortDesc },
  { value: 'created_at', label: 'Newest', icon: SortDesc },
  { value: 'discount_percent', label: 'Discount %', icon: SortDesc },
  { value: 'discounted_price', label: 'Discounted Price', icon: SortAsc },
];

export const SortModal = ({ 
  onApplySort, 
  currentSort, 
  productCount 
}: SortModalProps) => {
  const [localSort, setLocalSort] = useState<SortOptions>(currentSort);
  const [isOpen, setIsOpen] = useState(false);

  const handleApply = () => {
    onApplySort(localSort);
    setIsOpen(false);
  };

  const handleClear = () => {
    const defaultSort: SortOptions = {
      field: 'name',
      direction: 'asc',
    };
    setLocalSort(defaultSort);
    onApplySort(defaultSort);
    setIsOpen(false);
  };

  const updateSortField = (field: string) => {
    setLocalSort(prev => ({ ...prev, field: field as SortOptions['field'] }));
  };

  const updateSortDirection = (direction: string) => {
    setLocalSort(prev => ({ ...prev, direction: direction as SortOptions['direction'] }));
  };

  const getCurrentSortLabel = () => {
    const option = SORT_OPTIONS.find(opt => opt.value === currentSort.field);
    const direction = currentSort.direction === 'asc' ? '↑' : '↓';
    return option ? `${option.label} ${direction}` : 'Sort';
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          {getCurrentSortLabel()}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Sort Products</span>
            <span className="text-sm font-normal text-muted-foreground">
              {productCount} products
            </span>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Sort Field */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Sort By</Label>
            <RadioGroup
              value={localSort.field}
              onValueChange={updateSortField}
              className="space-y-2"
            >
              {SORT_OPTIONS.map((option) => {
                const Icon = option.icon;
                return (
                  <div key={option.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={option.value} id={option.value} />
                    <Label htmlFor={option.value} className="flex items-center gap-2 cursor-pointer">
                      <Icon className="w-4 h-4" />
                      {option.label}
                    </Label>
                  </div>
                );
              })}
            </RadioGroup>
          </div>

          {/* Sort Direction */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Order</Label>
            <RadioGroup
              value={localSort.direction}
              onValueChange={updateSortDirection}
              className="space-y-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="asc" id="asc" />
                <Label htmlFor="asc" className="flex items-center gap-2 cursor-pointer">
                  <SortAsc className="w-4 h-4" />
                  Ascending (A-Z, Low-High)
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="desc" id="desc" />
                <Label htmlFor="desc" className="flex items-center gap-2 cursor-pointer">
                  <SortDesc className="w-4 h-4" />
                  Descending (Z-A, High-Low)
                </Label>
              </div>
            </RadioGroup>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={handleClear}
            className="flex items-center gap-2"
          >
            Reset
          </Button>
          <Button onClick={handleApply} className="flex-1">
            Apply Sort
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
