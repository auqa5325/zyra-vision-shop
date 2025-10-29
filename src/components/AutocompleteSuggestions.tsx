import React, { useState, useRef, useEffect } from 'react';
import { Search, Package, Tag, Building2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { SearchSuggestion } from '@/hooks/useSearchSuggestions';

interface AutocompleteSuggestionsProps {
  suggestions: SearchSuggestion[];
  isLoading: boolean;
  isVisible: boolean;
  onSelect: (suggestion: SearchSuggestion) => void;
  onClose: () => void;
  className?: string;
}

export const AutocompleteSuggestions: React.FC<AutocompleteSuggestionsProps> = ({
  suggestions,
  isLoading,
  isVisible,
  onSelect,
  onClose,
  className
}) => {
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Reset selected index when suggestions change
  useEffect(() => {
    setSelectedIndex(-1);
  }, [suggestions]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isVisible) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => 
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
          break;
        case 'Enter':
          e.preventDefault();
          if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
            onSelect(suggestions[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isVisible, selectedIndex, suggestions, onSelect, onClose]);

  // Handle click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isVisible, onClose]);

  if (!isVisible) return null;

  const getSuggestionIcon = (suggestion: SearchSuggestion) => {
    switch (suggestion.type) {
      case 'product':
        return <Package className="h-4 w-4" />;
      case 'category':
        return <Tag className="h-4 w-4" />;
      case 'brand':
        return <Building2 className="h-4 w-4" />;
      default:
        return <Search className="h-4 w-4" />;
    }
  };

  const getSuggestionTypeLabel = (suggestion: SearchSuggestion) => {
    switch (suggestion.type) {
      case 'product':
        return 'Product';
      case 'category':
        return 'Category';
      case 'brand':
        return 'Brand';
      default:
        return 'Search';
    }
  };

  return (
    <div
      ref={suggestionsRef}
      className={cn(
        "absolute top-full left-0 right-0 z-50 mt-1 bg-background border border-border rounded-md shadow-lg max-h-80 overflow-y-auto",
        className
      )}
    >
      {isLoading ? (
        <div className="p-4 text-center text-muted-foreground">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-sm">Searching...</p>
        </div>
      ) : suggestions.length > 0 ? (
        <div className="py-2">
          {suggestions.map((suggestion, index) => (
            <button
              key={`${suggestion.type}-${suggestion.text}-${index}`}
              className={cn(
                "w-full px-4 py-3 text-left hover:bg-muted/50 transition-colors flex items-center gap-3",
                selectedIndex === index && "bg-muted"
              )}
              onClick={() => onSelect(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div className="text-muted-foreground">
                {getSuggestionIcon(suggestion)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-foreground truncate">
                  {suggestion.text}
                </div>
                <div className="text-xs text-muted-foreground">
                  {getSuggestionTypeLabel(suggestion)}
                </div>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="p-4 text-center text-muted-foreground">
          <Search className="h-6 w-6 mx-auto mb-2" />
          <p className="text-sm">No suggestions found</p>
        </div>
      )}
    </div>
  );
};

