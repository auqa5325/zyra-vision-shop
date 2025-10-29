export interface Product {
  product_id: string;
  name: string;
  description: string;
  price: number;
  discount_percent?: number;
  image_url: string;
  rating?: number; // For backward compatibility
  average_rating?: number; // Average rating from reviews (0-5)
  total_reviews?: number; // Total number of reviews
  rating_distribution?: { [key: string]: number }; // {1: count, 2: count, 3: count, 4: count, 5: count}
  category?: string;
  category_id?: number;
  brand?: string;
  reason_features?: {
    matched_tags?: string[];
    cf_score?: number;
    content_score?: number;
    hybrid_score?: number;
    source?: string;
    hybrid?: boolean;
  };
}

export interface CartItem extends Product {
  quantity: number;
}
