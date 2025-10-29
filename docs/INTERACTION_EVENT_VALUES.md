# Interaction Event Value Guide

This document describes what `event_value` should be for each interaction type.

## Event Value Definitions

### 1. **view** (Product View)
- **event_value**: `1` (always)
- **Meaning**: Just viewing/browsing a product
- **Usage**: Base weight (1.0) in ML models

### 2. **click** (Product Click)
- **event_value**: `1` (always)
- **Meaning**: User clicked to explore the product
- **Usage**: Weight multiplier 1.2x in ML models (higher engagement)

### 3. **add_to_cart** (Add to Cart)
- **event_value**: `quantity` (1, 2, 3, etc.)
- **Meaning**: Number of items added to cart
- **Usage**: 
  - Weight multiplier 1.5x in ML models (strong intent)
  - Used to sync cart quantities
- **Example**: `event_value = 2` means 2 items added

### 4. **remove_from_cart** (Remove from Cart)
- **event_value**: `quantity` (1, 2, etc.) or `0` (remove all)
- **Meaning**: Number of items removed from cart
- **Usage**: Used to sync cart quantities (decrease)
- **Example**: `event_value = 1` means remove 1 item

### 5. **update_cart_quantity** (Update Cart Quantity)
- **event_value**: `new_quantity` (0, 1, 2, etc.)
- **Meaning**: New quantity in cart for this product
- **Usage**: Used to sync cart quantities (set directly)
- **Example**: `event_value = 3` means set quantity to 3

### 6. **purchase** (Purchase/Order)
- **event_value**: `1` (always)
- **Meaning**: One purchase transaction
- **Usage**: 
  - Weight multiplier 2.0x in ML models (highest - actual conversion)
  - Quantity is always 1 per purchase interaction
- **Note**: Do NOT use product price as event_value

### 7. **wishlist** (Add/Remove from Wishlist)
- **event_value**: `1` (add) or `0` (remove)
- **Meaning**: 
  - `1` = Add item to wishlist
  - `0` = Remove item from wishlist
- **Usage**: 
  - Weight multiplier 1.3x in ML models
  - Used to sync wishlist state
- **Example**: 
  - `event_value = 1` → Add to wishlist
  - `event_value = 0` → Remove from wishlist

### 8. **review** (Product Review)
- **event_value**: `rating` (1, 2, 3, 4, or 5)
- **Meaning**: Star rating given by user
- **Usage**: 
  - Weight multiplier 1.6x in ML models (explicit feedback)
  - Rating value (1-5) is used directly
- **Example**: `event_value = 5` means 5-star rating

### 9. **search** (Search Query)
- **event_value**: `1` (always)
- **Meaning**: User performed a search
- **Usage**: Track search behavior

## Summary Table

| Event Type | event_value | Meaning | ML Weight |
|------------|-------------|---------|-----------|
| `view` | `1` | Viewing product | 1.0x (base) |
| `click` | `1` | Clicking product | 1.2x |
| `add_to_cart` | `quantity` (1+) | Items added | 1.5x |
| `remove_from_cart` | `quantity` or `0` | Items removed | - |
| `update_cart_quantity` | `new_quantity` | New cart quantity | - |
| `purchase` | `1` | Purchase transaction | 2.0x |
| `wishlist` | `1` or `0` | Add/Remove | 1.3x |
| `review` | `1-5` | Rating stars | 1.6x |
| `search` | `1` | Search performed | 1.0x |

## Important Notes

1. **Purchase**: Always use `event_value = 1`, NOT product price
2. **Cart**: Use actual quantity added/removed
3. **Wishlist**: Use `1` for add, `0` for remove
4. **Review**: Use rating value (1-5)
5. **Everything else**: Use `1` as default

## Example Interactions

```python
# Product view
Interaction(event_type="view", event_value=1)

# Add 2 items to cart
Interaction(event_type="add_to_cart", event_value=2)

# Remove 1 item from cart
Interaction(event_type="remove_from_cart", event_value=1)

# Purchase (quantity always 1)
Interaction(event_type="purchase", event_value=1)

# Add to wishlist
Interaction(event_type="wishlist", event_value=1)

# Remove from wishlist
Interaction(event_type="wishlist", event_value=0)

# 5-star review
Interaction(event_type="review", event_value=5)
```

