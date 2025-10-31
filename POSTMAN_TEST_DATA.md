# Postman Test Data - Ready-to-Use Values

Copy these values directly into your Postman requests!

## 🌍 Environment Variables

Set these in your Postman environment:

| Variable | Value | Notes |
|----------|-------|-------|
| `baseUrl` | `http://localhost:8005` | Your backend URL |
| `accessToken` | _(auto-filled after login)_ | JWT token |
| `refreshToken` | _(auto-filled after login)_ | Refresh token |
| `userId` | _(auto-filled after login)_ | User UUID |
| `productId` | _(set after listing products)_ | Product UUID |

---

## 🔐 Authentication Test Data

### Register User

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test@123456",
  "profile": {
    "name": "Test User",
    "preferences": ["electronics", "books"]
  }
}
```

**Alternative Test Users:**

User 2:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "profile": {
    "name": "John Doe",
    "preferences": ["electronics", "fashion"]
  }
}
```

User 3:
```json
{
  "username": "jane_smith",
  "email": "jane@example.com",
  "password": "StrongPass456!",
  "profile": {
    "name": "Jane Smith",
    "preferences": ["books", "home"]
  }
}
```

### Login User

```json
{
  "username": "testuser",
  "password": "Test@123456"
}
```

---

## 📦 Product Test Data

### Create Product

```json
{
  "name": "Wireless Bluetooth Headphones",
  "short_description": "Premium noise-cancelling headphones",
  "long_description": "Experience crystal-clear sound with our premium wireless headphones featuring active noise cancellation, 30-hour battery life, and comfortable over-ear design.",
  "price": 199.99,
  "currency": "INR",
  "brand": "SoundMax",
  "tags": ["electronics", "audio", "wireless"],
  "available": true
}
```

**More Test Products:**

Laptop:
```json
{
  "name": "ProBook 15 Laptop",
  "short_description": "High-performance laptop for professionals",
  "long_description": "Powerful Intel i7 processor, 16GB RAM, 512GB SSD, 15-inch Full HD display. Perfect for work and play.",
  "price": 899.99,
  "currency": "INR",
  "brand": "TechPro",
  "tags": ["electronics", "computers", "laptops"],
  "available": true
}
```

Smart Watch:
```json
{
  "name": "FitTrack Pro",
  "short_description": "Advanced fitness tracking smartwatch",
  "long_description": "Track your health with heart rate monitoring, GPS, sleep tracking, and 7-day battery life. Water resistant up to 50 meters.",
  "price": 249.99,
  "currency": "INR",
  "brand": "HealthTech",
  "tags": ["electronics", "wearables", "fitness"],
  "available": true
}
```

Coffee Maker:
```json
{
  "name": "BrewMaster Deluxe",
  "short_description": "Professional coffee maker",
  "long_description": "Programmable 12-cup coffee maker with thermal carafe, brew strength control, and auto shut-off feature.",
  "price": 79.99,
  "currency": "INR",
  "brand": "KitchenPro",
  "tags": ["home", "appliances", "coffee"],
  "available": true
}
```

---

## 📝 Interaction Test Data

### Create Interaction (View)

```json
{
  "user_id": "{{userId}}",
  "product_id": "{{productId}}",
  "event_type": "view",
  "event_value": 1.0,
  "platform": "web",
  "device": "desktop"
}
```

**More Interaction Types:**

Click:
```json
{
  "user_id": "{{userId}}",
  "product_id": "{{productId}}",
  "event_type": "click",
  "event_value": 1.0,
  "platform": "web",
  "device": "desktop"
}
```

Add to Cart:
```json
{
  "user_id": "{{userId}}",
  "product_id": "{{productId}}",
  "event_type": "add_to_cart",
  "event_value": 1.0,
  "platform": "web",
  "device": "desktop"
}
```

Purchase:
```json
{
  "user_id": "{{userId}}",
  "product_id": "{{productId}}",
  "event_type": "purchase",
  "event_value": 5.0,
  "platform": "web",
  "device": "desktop"
}
```

Search:
```json
{
  "user_id": "{{userId}}",
  "product_id": null,
  "event_type": "search",
  "event_value": 1.0,
  "platform": "web",
  "device": "desktop",
  "metadata": {
    "query": "laptop"
  }
}
```

---

## ⭐ Review Test Data

### Create Review

```json
{
  "product_id": "{{productId}}",
  "rating": 5,
  "title": "Great Product!",
  "comment": "This product exceeded my expectations. Highly recommended! The quality is excellent and it works perfectly."
}
```

**More Test Reviews:**

5 Stars:
```json
{
  "product_id": "{{productId}}",
  "rating": 5,
  "title": "Excellent Quality",
  "comment": "One of the best products I've purchased. Fast shipping and great value for money."
}
```

4 Stars:
```json
{
  "product_id": "{{productId}}",
  "rating": 4,
  "title": "Very Good",
  "comment": "Really satisfied with this purchase. Minor issues but overall great product."
}
```

3 Stars:
```json
{
  "product_id": "{{productId}}",
  "rating": 3,
  "title": "Okay Product",
  "comment": "It's decent but has some room for improvement. Gets the job done."
}
```

2 Stars:
```json
{
  "product_id": "{{productId}}",
  "rating": 2,
  "title": "Disappointed",
  "comment": "Expected more for the price. Has several issues that need to be addressed."
}
```

1 Star:
```json
{
  "product_id": "{{productId}}",
  "rating": 1,
  "title": "Poor Quality",
  "comment": "Not worth the money. Multiple defects and doesn't work as advertised."
}
```

---

## 🔍 Search Query Examples

### Search Products

Use these in the query parameter:

| Query | Expected Results |
|-------|------------------|
| `laptop` | Laptops, computers |
| `headphone` | Audio devices, headphones |
| `book` | Books, literature |
| `phone` | Mobile phones, smartphones |
| `watch` | Timepieces, smartwatches |
| `shoe` | Footwear, shoes |

### Category IDs

| ID | Category |
|----|----------|
| `1` | Electronics |
| `2` | Clothing |
| `3` | Books |
| `4` | Home & Kitchen |
| `5` | Sports & Outdoors |

---

## 🎯 Recommendation Parameters

### Hybrid Recommendations

```json
{
  "user_id": "{{userId}}",
  "query": "laptop",
  "alpha": 0.6,
  "k": 10
}
```

**Parameter Values:**

| Parameter | Range | Description |
|-----------|-------|-------------|
| `alpha` | 0.0 - 1.0 | Weight for collaborative filtering (0=content only, 1=collab only) |
| `k` | 1 - 50 | Number of recommendations to return |

### Common Alpha Values

- `0.0` = Pure content-based
- `0.3` = More content, less collaborative
- `0.5` = Balanced
- `0.7` = More collaborative, less content
- `1.0` = Pure collaborative

---

## 👤 User Profile Update

### Update Profile

```json
{
  "name": "Updated User Name",
  "preferences": ["electronics", "books", "fashion"],
  "address": "123 Main St, City, Country",
  "phone": "+1-234-567-8900"
}
```

---

## 📊 API Query Parameters

### List Products

```
?skip=0&limit=20&available_only=true
```

### Get Products by Category

```
?skip=0&limit=20
```

### Get Product Reviews

```
?page=1&limit=10&sort=newest
```

Sort options: `newest`, `oldest`, `rating_high`, `rating_low`

### Search Products

```
?q=laptop&k=10
```

---

## 🧪 Quick Copy-Paste Guide

### 1️⃣ Register First User

Copy this into "Register User" request body:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test@123456",
  "profile": {
    "name": "Test User",
    "preferences": ["electronics", "books"]
  }
}
```

### 2️⃣ Login

Copy this into "Login User" request body:
```json
{
  "username": "testuser",
  "password": "Test@123456"
}
```

### 3️⃣ Create Interaction

After getting a productId, copy this into "Create Interaction" request body:
```json
{
  "user_id": "{{userId}}",
  "product_id": "{{productId}}",
  "event_type": "view",
  "event_value": 1.0,
  "platform": "web",
  "device": "desktop"
}
```

### 4️⃣ Create Review

```json
{
  "product_id": "{{productId}}",
  "rating": 5,
  "title": "Great Product!",
  "comment": "This product exceeded my expectations. Highly recommended!"
}
```

---

## 🎯 Testing Scenarios

### Scenario 1: New User Journey

1. Register with User data above
2. Login
3. Browse products (Search "laptop")
4. View product details
5. Get recommendations
6. Add to cart (create interaction)
7. Create review

### Scenario 2: Multiple Interactions

1. View 3 different products
2. Add 2 to cart
3. Make 1 purchase
4. Check user stats

### Scenario 3: Recommendation Testing

1. Get hybrid recommendations (alpha=0.6)
2. Get content-based recommendations
3. Get collaborative recommendations
4. Compare results

---

## 💡 Pro Tips

1. **Use Variables**: Always use `{{userId}}` and `{{productId}}` instead of hardcoding
2. **Save Responses**: Save product IDs from responses for later use
3. **Chain Requests**: Results from one request can inform the next
4. **Test Edge Cases**: Try invalid data, empty fields, etc.
5. **Check Status Codes**: 200 = success, 400 = bad data, 401 = auth needed

---

## 📚 Need More?

- [Postman Quick Start](POSTMAN_QUICKSTART.md) - Get started in 5 minutes
- [First Steps Guide](docs/POSTMAN_FIRST_STEPS.md) - Step-by-step testing
- [Complete Guide](docs/POSTMAN_GUIDE.md) - Full documentation

---

**Happy Testing! 🎉**

