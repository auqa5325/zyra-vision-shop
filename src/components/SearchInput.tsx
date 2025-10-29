import React, { useState, useRef } from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { AutocompleteSuggestions } from '@/components/AutocompleteSuggestions';
import { useSearchSuggestions } from '@/hooks/useSearchSuggestions';
import { SearchSuggestion } from '@/hooks/useSearchSuggestions';
import { useNavigate } from 'react-router-dom';

interface SearchInputProps {
  placeholder?: string;
  className?: string;
  onSearch?: (query: string) => void;
  initialValue?: string;
  showSubmitButton?: boolean;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  placeholder = "Search products...",
  className,
  onSearch,
  initialValue = "",
  showSubmitButton = true
}) => {
  const [query, setQuery] = useState(initialValue);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const { suggestions, isLoading, hasSuggestions } = useSearchSuggestions({
    query,
    enabled: isFocused && query.trim().length >= 2
  });

  // Simple logic for showing suggestions
  const shouldShowSuggestions = isFocused && query.trim().length >= 2 && (hasSuggestions || isLoading);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      performSearch(query.trim());
    }
  };

  const performSearch = (searchQuery: string) => {
    if (onSearch) {
      onSearch(searchQuery);
    } else {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleSuggestionSelect = (suggestion: SearchSuggestion) => {
    setQuery(suggestion.text);
    setIsFocused(false);
    
    if (suggestion.type === 'product' && suggestion.product) {
      // Navigate directly to product page
      navigate(`/product/${suggestion.product.product_id}`);
    } else {
      // Perform search with the suggestion text
      performSearch(suggestion.text);
    }
  };

  const handleFocus = () => {
    setIsFocused(true);
  };

  const handleBlur = () => {
    // Use a small delay to allow clicking on suggestions
    setTimeout(() => {
      setIsFocused(false);
    }, 150);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          ref={inputRef}
          type="search"
          placeholder={placeholder}
          className={`w-full pl-10 ${showSubmitButton ? 'pr-12' : 'pr-4'} bg-muted/50 border-none focus-visible:ring-primary`}
          value={query}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyPress={handleKeyPress}
          autoComplete="off"
        />
        {showSubmitButton && (
          <Button
            type="submit"
            size="sm"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0"
            disabled={!query.trim()}
          >
            <Search className="h-4 w-4" />
          </Button>
        )}
      </form>

      <AutocompleteSuggestions
        suggestions={suggestions}
        isLoading={isLoading}
        isVisible={shouldShowSuggestions}
        onSelect={handleSuggestionSelect}
        onClose={() => setIsFocused(false)}
      />
    </div>
  );
};