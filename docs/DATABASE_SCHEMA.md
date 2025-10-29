# Database Schema Documentation

**Database**: `localhost:5432/zyra_db`  
**Total Tables**: 15  
**Generated**: 2025-10-28 21:11:28

## Table of Contents

1. [ab_tests](#ab_tests)
2. [categories](#categories)
3. [embeddings_meta](#embeddings_meta)
4. [interactions](#interactions)
5. [product_images](#product_images)
6. [products](#products)
7. [purchase_history](#purchase_history)
8. [recommendation_logs](#recommendation_logs)
9. [review_helpful_votes](#review_helpful_votes)
10. [reviews](#reviews)
11. [sessions](#sessions)
12. [system_audit](#system_audit)
13. [user_cart](#user_cart)
14. [user_wishlist](#user_wishlist)
15. [users](#users)

---

## ab_tests

**Record Count**: 0

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `INTEGER` | No | nextval('ab_tests_id_seq'::regclass) | No | Primary identifier |
| `test_name` | `VARCHAR` | No | None | No |  |
| `user_id` | `UUID` | Yes | None | No | Primary identifier |
| `cohort` | `VARCHAR` | Yes | None | No |  |
| `assigned_at` | `TIMESTAMP` | Yes | now() | No |  |

### Foreign Keys

| Column | References |
|--------|------------|
| `user_id` | `users.user_id` |

### Sample Data

*Unable to retrieve sample data*

---

## categories

**Record Count**: 26

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `category_id` | `INTEGER` | No | nextval('categories_category_id_seq'::regclass) | No | Primary identifier |
| `name` | `VARCHAR` | No | None | No |  |
| `slug` | `VARCHAR` | No | None | No |  |
| `parent_id` | `INTEGER` | Yes | None | No | Primary identifier |

### Foreign Keys

| Column | References |
|--------|------------|
| `parent_id` | `categories.category_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `categories_slug_key` | UNIQUE | `slug` |

### Sample Data

| `category_id` | `name` | `slug` | `parent_id` |
|---|---|---|---|
| 1 | Electronics | electronics | NULL |
| 2 | Laptops | electronics-laptops | 1 |
| 3 | Smartphones | electronics-smartphones | 1 |
| 4 | Headphones | electronics-headphones | 1 |
| 5 | Cameras | electronics-cameras | 1 |

---

## embeddings_meta

**Record Count**: 1,331

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `BIGINT` | No | nextval('embeddings_meta_id_seq'::regclass) | No | Primary identifier |
| `object_type` | `VARCHAR` | No | None | No |  |
| `object_id` | `UUID` | No | None | No | Primary identifier |
| `embedding_file` | `VARCHAR` | Yes | None | No |  |
| `vector_index` | `INTEGER` | Yes | None | No |  |
| `dim` | `INTEGER` | Yes | None | No |  |
| `created_at` | `TIMESTAMP` | Yes | now() | No | Creation timestamp |

### Sample Data

| `id` | `object_type` | `object_id` | `embedding_file` | `vector_index` | `dim` | `created_at` |
|---|---|---|---|---|---|---|
| 974 | product | 2ac0d35e-8fdf-4fcb-b73b-b180f71398ee | artifacts/product_embeddings.npy | 0 | 384 | 2025-10-28 00:03:54.489726+05:30 |
| 975 | product | 6f435120-2cb2-406a-9168-3c3dff63a519 | artifacts/product_embeddings.npy | 1 | 384 | 2025-10-28 00:03:54.489726+05:30 |
| 976 | product | bc99d473-b80a-4ff7-a350-ab596d66cccd | artifacts/product_embeddings.npy | 2 | 384 | 2025-10-28 00:03:54.489726+05:30 |
| 977 | product | c43caae2-af96-4625-a274-6154945b7399 | artifacts/product_embeddings.npy | 3 | 384 | 2025-10-28 00:03:54.489726+05:30 |
| 978 | product | bcfaa86b-2d11-4e31-8869-a3633cbe5f53 | artifacts/product_embeddings.npy | 4 | 384 | 2025-10-28 00:03:54.489726+05:30 |

---

## interactions

**Record Count**: 6

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `BIGINT` | No | nextval('interactions_id_seq'::regclass) | No | Primary identifier |
| `user_id` | `UUID` | Yes | None | No | Primary identifier |
| `product_id` | `UUID` | Yes | None | No | Primary identifier |
| `session_id` | `UUID` | Yes | None | No | Primary identifier |
| `event_type` | `VARCHAR` | No | None | No |  |
| `event_value` | `NUMERIC` | Yes | None | No |  |
| `platform` | `VARCHAR` | Yes | None | No |  |
| `device` | `JSON` | Yes | None | No |  |
| `created_at` | `TIMESTAMP` | No | now() | No | Creation timestamp |

### Foreign Keys

| Column | References |
|--------|------------|
| `product_id` | `products.product_id` |
| `user_id` | `users.user_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `idx_interactions_created_at` | NON-UNIQUE | `created_at` |
| `idx_interactions_event_type` | NON-UNIQUE | `event_type` |
| `idx_interactions_product_event` | NON-UNIQUE | `product_id, event_type` |
| `idx_interactions_user_event` | NON-UNIQUE | `user_id, event_type` |
| `idx_interactions_user_purchases` | NON-UNIQUE | `user_id, created_at` |

### Sample Data

| `id` | `user_id` | `product_id` | `session_id` | `event_type` | `event_value` | `platform` | `device` | `created_at` |
|---|---|---|---|---|---|---|---|---|
| 105813 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 77ae4555-ac6f-4a4b-8cdd-c5f03cb08a06 | NULL | click | 1 | web | {'type': 'desktop', 'os': 'MacIntel', 'browser': 'Safari'} | 2025-10-28 01:14:54.991563+05:30 |
| 105814 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 17f7f201-4cad-4343-8de7-c2ce3e0b1315 | NULL | click | 1 | web | {'type': 'desktop', 'os': 'MacIntel', 'browser': 'Safari'} | 2025-10-28 01:20:26.685837+05:30 |
| 105815 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 9ea4630b-1ab4-4a44-8999-312efa000c20 | NULL | click | 1 | web | {'type': 'desktop', 'os': 'MacIntel', 'browser': 'Safari'} | 2025-10-28 01:28:27.071187+05:30 |
| 105816 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 09bb9bd1-453b-4242-973f-74ad27bd7a7a | NULL | click | 1 | web | {'type': 'desktop', 'os': 'MacIntel', 'browser': 'Safari'} | 2025-10-28 11:38:10.770395+05:30 |
| 105817 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 82bfd93d-254c-4fd4-9aef-1551d1d28b87 | NULL | click | 1 | web | {'type': 'desktop', 'os': 'MacIntel', 'browser': 'Safari'} | 2025-10-28 11:56:21.274582+05:30 |

---

## product_images

**Record Count**: 1,331

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `image_id` | `UUID` | No | None | No | Primary identifier |
| `product_id` | `UUID` | No | None | No | Primary identifier |
| `s3_key` | `VARCHAR` | No | None | No |  |
| `cdn_url` | `VARCHAR` | Yes | None | No |  |
| `width` | `INTEGER` | Yes | None | No | Primary identifier |
| `height` | `INTEGER` | Yes | None | No |  |
| `format` | `VARCHAR` | Yes | None | No |  |
| `variant` | `VARCHAR` | Yes | None | No |  |
| `alt_text` | `VARCHAR` | Yes | None | No |  |
| `is_primary` | `BOOLEAN` | Yes | None | No |  |
| `created_at` | `TIMESTAMP` | Yes | now() | No | Creation timestamp |

### Foreign Keys

| Column | References |
|--------|------------|
| `product_id` | `products.product_id` |

### Sample Data

| `image_id` | `product_id` | `s3_key` | `cdn_url` | `width` | `height` | `format` | `variant` | `alt_text` | `is_primary` | `created_at` |
|---|---|---|---|---|---|---|---|---|---|---|
| 14851bca-d30b-43e6-8214-e281a1805eb1 | b48a1876-3c67-4544-8a9b-3ff7ad8917bd | products/b48a1876-3c67-4544-8a9b-3ff7ad8917bd/House of Pataudi Printed Silk Kurta Set_57cee513.jpg | https://crestora-uploads.s3.ap-south-1.amazonaws.com/products/b48a1876-3c67-4544-8a9b-3ff7ad8917b... | NULL | NULL | NULL | NULL | NULL | True | 2025-10-27 09:13:21.522116+05:30 |
| 3cea74a9-5ba5-4417-b16c-0e425e428674 | ea98ca2b-f422-4429-a2a4-8f47a0dbcff3 | uploads/products/ea98ca2b-f422-4429-a2a4-8f47a0dbcff3/ea98ca2b-f422-4429-a2a4-8f47a0dbcff3.png | /api/images/ea98ca2b-f422-4429-a2a4-8f47a0dbcff3/ea98ca2b-f422-4429-a2a4-8f47a0dbcff3.png | NULL | NULL | NULL | NULL | NULL | True | 2025-10-27 09:13:21.522116+05:30 |
| 77f27855-fabb-4715-b520-2c44462c2fb6 | a85c7c35-7fbf-44b0-827c-91e805b49afd | products/a85c7c35-7fbf-44b0-827c-91e805b49afd/Nivia Foam Roller - High Density_33f14ab9.jpg | https://crestora-uploads.s3.ap-south-1.amazonaws.com/products/a85c7c35-7fbf-44b0-827c-91e805b49af... | NULL | NULL | NULL | NULL | NULL | True | 2025-10-27 09:13:21.522116+05:30 |
| 623dcf85-4f7e-4767-aef6-03c667fb1a30 | 4c55b579-731a-49bd-a44b-fc52919ee7a8 | uploads/products/4c55b579-731a-49bd-a44b-fc52919ee7a8/4c55b579-731a-49bd-a44b-fc52919ee7a8.png | /api/images/4c55b579-731a-49bd-a44b-fc52919ee7a8/4c55b579-731a-49bd-a44b-fc52919ee7a8.png | NULL | NULL | NULL | NULL | NULL | True | 2025-10-27 09:13:21.522116+05:30 |
| 657844bc-f161-4ea0-85d1-c17c81b34725 | 70ad1fec-f882-404d-b9f8-e6072f5bee43 | uploads/products/70ad1fec-f882-404d-b9f8-e6072f5bee43/70ad1fec-f882-404d-b9f8-e6072f5bee43.png | /api/images/70ad1fec-f882-404d-b9f8-e6072f5bee43/70ad1fec-f882-404d-b9f8-e6072f5bee43.png | NULL | NULL | NULL | NULL | NULL | True | 2025-10-27 09:13:21.522116+05:30 |

---

## products

**Record Count**: 1,331

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `product_id` | `UUID` | No | None | No | Primary identifier |
| `sku` | `VARCHAR` | Yes | None | No |  |
| `name` | `VARCHAR` | No | None | No |  |
| `short_description` | `VARCHAR` | Yes | None | No |  |
| `long_description` | `VARCHAR` | Yes | None | No |  |
| `category_id` | `INTEGER` | Yes | None | No | Primary identifier |
| `tags` | `ARRAY` | Yes | None | No |  |
| `price` | `NUMERIC(10, 2)` | Yes | None | No |  |
| `currency` | `VARCHAR` | Yes | None | No |  |
| `brand` | `VARCHAR` | Yes | None | No |  |
| `available` | `BOOLEAN` | Yes | None | No |  |
| `created_at` | `TIMESTAMP` | No | now() | No | Creation timestamp |
| `updated_at` | `TIMESTAMP` | No | now() | No | Last update timestamp |
| `metadata_json` | `JSON` | Yes | None | No |  |
| `rating` | `NUMERIC(3, 1)` | Yes | 0.0 | No |  |
| `discount_percent` | `NUMERIC(5, 2)` | Yes | 0 | No |  |

### Foreign Keys

| Column | References |
|--------|------------|
| `category_id` | `categories.category_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `products_sku_key` | UNIQUE | `sku` |

### Sample Data

| `product_id` | `sku` | `name` | `short_description` | `long_description` | `category_id` | `tags` | `price` | `currency` | `brand` | `available` | `created_at` | `updated_at` | `metadata_json` | `rating` | `discount_percent` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0233067c-94d6-41a5-9616-6292eae0eec7 | SS-DT-6S-GT | Style Spa Dining Table (6 Seater, Glass Top) | Elegant dining table with a glass top for modern dining rooms. | Add a touch of elegance to your dining room with this Style Spa dining table. The glass top and s... | 18 | ['Table', 'Dining', 'Style Spa', 'Dining Room'] | 24300.00 | INR | Style Spa | True | 2025-10-27 08:17:24.217013+05:30 | 2025-10-27 08:17:24.217013+05:30 | {'generated_by': 'gemini', 'generation_method': 'gemini-2.5-flash', 'generated_at': '2025-10-27T08:1... | 0.0 | 40.00 |
| 0233ffe9-f5e8-44f4-93a0-2cfd9818770d | CH-CM-MANDALA-031 | Chumbak Ceramic Coffee Mug - Mandala Art | Ceramic coffee mug with colorful Mandala art. | Enjoy your morning coffee or tea with this vibrant and stylish ceramic mug from Chumbak. Featurin... | 20 | ['coffee mug', 'ceramic', 'chumbak', 'mandala art', 'kitchen'] | 499.00 | INR | Chumbak | True | 2025-10-27 08:17:52.644738+05:30 | 2025-10-27 08:17:52.644738+05:30 | {'generated_by': 'gemini', 'generation_method': 'gemini-2.5-flash', 'generated_at': '2025-10-27T08:1... | 0.0 | 20.00 |
| 02a4b7fd-38bc-4730-874b-3fe146f86b07 | VI-T2X5G4128AG_8F1A49B9 | Vivo T2x 5G (Aurora Gold, 4GB RAM, 128GB Storage) | 50MP Camera, Dimensity 6020, Slim Design | The Vivo T2x 5G boasts a slim and stylish design with a capable 50MP camera. Powered by the Dimen... | 3 | ['5G', 'Vivo', '50MP Camera', '4GB RAM', '128GB Storage', 'T Series'] | 13999.00 | INR | Vivo | True | 2025-10-27 08:22:46.788295+05:30 | 2025-10-27 08:22:46.788295+05:30 | {'generated_by': 'gemini', 'generation_method': 'gemini-2.0-flash', 'generated_at': '2025-10-27T08:2... | 0.0 | 0.00 |
| 02d6cc54-126a-40a3-afb0-4357e2ae4dd7 | NK-PC-SET4-033 | Nilkamal Plastic Chair - Set of 4 | Set of four durable plastic chairs from Nilkamal. | Provide comfortable seating for your guests with this set of four plastic chairs from Nilkamal. M... | 20 | ['plastic chair', 'nilkamal', 'furniture', 'outdoor', 'set of 4'] | 2999.00 | INR | Nilkamal | True | 2025-10-27 08:17:52.644738+05:30 | 2025-10-27 08:17:52.644738+05:30 | {'generated_by': 'gemini', 'generation_method': 'gemini-2.5-flash', 'generated_at': '2025-10-27T08:1... | 0.0 | 10.00 |
| 02dbd636-9aa4-4d9e-be41-1f2f516cdd09 | AS-RN-WM-PP-06 | ASICS Gel-Kayano 29 Running Shoes - Women (Pink/Purple) | Supportive running shoes for overpronators. | The ASICS Gel-Kayano 29 provides exceptional support and cushioning for overpronators. These runn... | 10 | ['running shoes', 'women', 'asics', 'gel-kayano 29', 'pink', 'purple', 'supportive'] | 10499.00 | INR | ASICS | True | 2025-10-27 08:17:09.099418+05:30 | 2025-10-27 08:17:09.099418+05:30 | {'generated_by': 'gemini', 'generation_method': 'gemini-2.5-flash', 'generated_at': '2025-10-27T08:1... | 0.0 | 5.00 |

---

## purchase_history

**Record Count**: 15

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `BIGINT` | No | nextval('purchase_history_id_seq'::regclass) | No | Primary identifier |
| `user_id` | `UUID` | No | None | No | Primary identifier |
| `product_id` | `UUID` | No | None | No | Primary identifier |
| `quantity` | `INTEGER` | No | 1 | No |  |
| `unit_price` | `NUMERIC(10, 2)` | No | None | No |  |
| `total_price` | `NUMERIC(10, 2)` | No | None | No |  |
| `order_id` | `UUID` | Yes | None | No | Primary identifier |
| `purchased_at` | `TIMESTAMP` | No | now() | No |  |
| `payment_method` | `VARCHAR` | Yes | None | No |  |
| `payment_status` | `VARCHAR` | Yes | 'completed'::character varying | No |  |

### Foreign Keys

| Column | References |
|--------|------------|
| `product_id` | `products.product_id` |
| `user_id` | `users.user_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `idx_purchase_history_order_id` | NON-UNIQUE | `order_id` |
| `idx_purchase_history_product_id` | NON-UNIQUE | `product_id` |
| `idx_purchase_history_purchased_at` | NON-UNIQUE | `purchased_at` |
| `idx_purchase_history_user_id` | NON-UNIQUE | `user_id` |
| `idx_purchase_history_user_purchased` | NON-UNIQUE | `user_id, purchased_at` |

### Sample Data

| `id` | `user_id` | `product_id` | `quantity` | `unit_price` | `total_price` | `order_id` | `purchased_at` | `payment_method` | `payment_status` |
|---|---|---|---|---|---|---|---|---|---|
| 7262 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 63288c8a-3dd5-4703-9da5-33cfa03a8cae | 1 | 499.00 | 499.00 | 76ee78b7-6fc6-45b8-9527-4fce35602dd9 | 2025-10-28 01:12:49.668698+05:30 | credit_card | completed |
| 7263 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 9bdabefd-8856-41fe-95c2-3f65045d0ffe | 1 | 399.00 | 399.00 | 76ee78b7-6fc6-45b8-9527-4fce35602dd9 | 2025-10-28 01:12:49.668698+05:30 | credit_card | completed |
| 7264 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | e2fd6a27-0164-49d2-8efe-c7683fc9cd7a | 1 | 3999.00 | 3999.00 | 4f765e04-460a-4871-bd2d-a843b35a9ecd | 2025-10-28 01:16:13.226624+05:30 | credit_card | completed |
| 7265 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | e2fd6a27-0164-49d2-8efe-c7683fc9cd7a | 1 | 3999.00 | 3999.00 | 36604af5-9687-47a2-b3f4-5e3f427aa15f | 2025-10-28 01:16:55.462943+05:30 | credit_card | completed |
| 7266 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 77ae4555-ac6f-4a4b-8cdd-c5f03cb08a06 | 1 | 124999.00 | 124999.00 | f0812a36-c3b1-4d71-b77d-d74095220438 | 2025-10-28 01:17:37.592845+05:30 | credit_card | completed |

---

## recommendation_logs

**Record Count**: 18

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `rec_id` | `BIGINT` | No | nextval('recommendation_logs_rec_id_seq'::regclass) | No | Primary identifier |
| `user_id` | `UUID` | Yes | None | No | Primary identifier |
| `session_id` | `UUID` | Yes | None | No | Primary identifier |
| `request_context` | `JSON` | Yes | None | No |  |
| `candidate_products` | `ARRAY` | Yes | None | No | Primary identifier |
| `returned_at` | `TIMESTAMP` | Yes | now() | No |  |

### Foreign Keys

| Column | References |
|--------|------------|
| `user_id` | `users.user_id` |

### Sample Data

| `rec_id` | `user_id` | `session_id` | `request_context` | `candidate_products` | `returned_at` |
|---|---|---|---|---|---|
| 2 | a1ae20b4-1cff-4e31-ae1f-3bbdddf42f7b | NULL | {'query': None, 'alpha': 0.6, 'k': 3, 'type': 'hybrid'} | [] | 2025-10-27 06:11:53.550104+05:30 |
| 3 | a1ae20b4-1cff-4e31-ae1f-3bbdddf42f7b | NULL | {'query': None, 'alpha': 0.6, 'k': 3, 'type': 'hybrid'} | [UUID('f8329552-a362-4ec2-b887-158c1c388bc2'), UUID('d9edc861-0d8a-4dd4-9697-38bbe763e7ae'), UUID('9... | 2025-10-27 06:12:26.133006+05:30 |
| 4 | 42edafbf-6622-438f-b91e-2835c41e02b5 | NULL | {'query': None, 'alpha': 0.6, 'k': 5, 'type': 'hybrid'} | [] | 2025-10-27 09:29:52.579236+05:30 |
| 5 | 42edafbf-6622-438f-b91e-2835c41e02b5 | NULL | {'query': None, 'alpha': 0.6, 'k': 5, 'type': 'hybrid'} | [] | 2025-10-27 09:32:39.572362+05:30 |
| 6 | 42edafbf-6622-438f-b91e-2835c41e02b5 | NULL | {'query': None, 'alpha': 0.6, 'k': 5, 'type': 'hybrid'} | [] | 2025-10-27 09:32:54.258502+05:30 |

---

## review_helpful_votes

**Record Count**: 0

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `BIGINT` | No | nextval('review_helpful_votes_id_seq'::regclass) | No | Primary identifier |
| `review_id` | `UUID` | No | None | No | Primary identifier |
| `user_id` | `UUID` | No | None | No | Primary identifier |
| `created_at` | `TIMESTAMP` | No | now() | No | Creation timestamp |

### Foreign Keys

| Column | References |
|--------|------------|
| `review_id` | `reviews.review_id` |
| `user_id` | `users.user_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `review_helpful_votes_review_id_user_id_key` | UNIQUE | `review_id, user_id` |

### Sample Data

*Unable to retrieve sample data*

---

## reviews

**Record Count**: 3

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `review_id` | `UUID` | No | gen_random_uuid() | No | Primary identifier |
| `user_id` | `UUID` | No | None | No | Primary identifier |
| `product_id` | `UUID` | No | None | No | Primary identifier |
| `rating` | `INTEGER` | No | None | No |  |
| `title` | `VARCHAR` | Yes | None | No |  |
| `comment` | `TEXT` | Yes | None | No |  |
| `verified_purchase` | `BOOLEAN` | No | false | No |  |
| `helpful_count` | `INTEGER` | No | 0 | No |  |
| `is_approved` | `BOOLEAN` | No | true | No |  |
| `created_at` | `TIMESTAMP` | No | now() | No | Creation timestamp |
| `updated_at` | `TIMESTAMP` | No | now() | No | Last update timestamp |

### Foreign Keys

| Column | References |
|--------|------------|
| `product_id` | `products.product_id` |
| `user_id` | `users.user_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `idx_reviews_product_id` | NON-UNIQUE | `product_id` |
| `idx_reviews_rating` | NON-UNIQUE | `rating` |
| `idx_reviews_user_id` | NON-UNIQUE | `user_id` |
| `reviews_user_id_product_id_key` | UNIQUE | `user_id, product_id` |

### Sample Data

| `review_id` | `user_id` | `product_id` | `rating` | `title` | `comment` | `verified_purchase` | `helpful_count` | `is_approved` | `created_at` | `updated_at` |
|---|---|---|---|---|---|---|---|---|---|---|
| 16b40455-9685-481a-84d3-10cbe5038d0c | 02e54e60-8c9b-4bb8-97c3-bf74705b38f6 | 9bdabefd-8856-41fe-95c2-3f65045d0ffe | 5 | 1234 | 1234567 | False | 4 | True | 2025-10-27 22:29:07.704560+05:30 | 2025-10-27 23:48:18.838063+05:30 |
| 6678f520-0e23-4ff2-9d87-3de984df2acb | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 9bdabefd-8856-41fe-95c2-3f65045d0ffe | 3 | 123 | 124 | False | 3 | True | 2025-10-27 23:47:40.585916+05:30 | 2025-10-27 23:51:19.704077+05:30 |
| 2b035457-132a-4ba8-bd96-3f25718fe078 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 043fabbd-430f-4765-bca2-e0418dd25f41 | 5 | 23456 | 3456789 | False | 0 | True | 2025-10-28 12:11:29.347899+05:30 | 2025-10-28 12:11:29.347899+05:30 |

---

## sessions

**Record Count**: 1,900

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `session_id` | `UUID` | No | None | No | Primary identifier |
| `user_id` | `UUID` | Yes | None | No | Primary identifier |
| `started_at` | `TIMESTAMP` | No | now() | No |  |
| `ended_at` | `TIMESTAMP` | Yes | None | No |  |
| `context` | `JSON` | Yes | None | No |  |

### Foreign Keys

| Column | References |
|--------|------------|
| `user_id` | `users.user_id` |

### Sample Data

| `session_id` | `user_id` | `started_at` | `ended_at` | `context` |
|---|---|---|---|---|
| a5ed92bd-6c63-41d6-a10b-cbea3e9b19de | 9e57e084-f46c-42b6-a621-1b6865e1a607 | 2025-08-20 23:12:59.274117+05:30 | NULL | {'referrer': 'instagram', 'campaign': 'new_arrivals', 'device_type': 'mobile'} |
| 4748775c-d0d8-45e0-95fe-eadc6708c093 | 8d6fef54-7f70-46b7-8499-b2727df0e2b4 | 2025-10-11 00:52:41.418896+05:30 | NULL | {'referrer': 'google', 'campaign': 'summer_sale', 'device_type': 'tablet'} |
| 4a28bf97-c837-4f5c-9865-1ee3bc894af5 | 6123828d-821f-4931-a540-ef21aa28eca8 | 2025-10-19 03:46:03.088141+05:30 | NULL | {'referrer': 'http://www.rodriguez-flynn.com/', 'campaign': None, 'device_type': 'mobile'} |
| 620a09ed-efbf-4ede-953f-ed52dc943405 | c84c2913-1de0-449b-9533-977833d72151 | 2025-09-07 20:00:35.580765+05:30 | NULL | {'referrer': 'google', 'campaign': None, 'device_type': 'tablet'} |
| 0876e538-11eb-4f4d-ae1a-276f69d36cee | 1d544528-722d-4075-a146-3c397360523e | 2025-10-22 14:29:12.548161+05:30 | NULL | {'referrer': 'direct', 'campaign': 'summer_sale', 'device_type': 'desktop'} |

---

## system_audit

**Record Count**: 0

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `BIGINT` | No | nextval('system_audit_id_seq'::regclass) | No | Primary identifier |
| `component` | `VARCHAR` | Yes | None | No |  |
| `severity` | `VARCHAR` | Yes | None | No |  |
| `message` | `VARCHAR` | Yes | None | No |  |
| `payload` | `JSON` | Yes | None | No |  |
| `created_at` | `TIMESTAMP` | Yes | now() | No | Creation timestamp |

### Sample Data

*Unable to retrieve sample data*

---

## user_cart

**Record Count**: 1

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `BIGINT` | No | nextval('user_cart_id_seq'::regclass) | No | Primary identifier |
| `user_id` | `UUID` | No | None | No | Primary identifier |
| `product_id` | `UUID` | No | None | No | Primary identifier |
| `quantity` | `INTEGER` | No | 1 | No |  |
| `added_at` | `TIMESTAMP` | No | now() | No |  |
| `updated_at` | `TIMESTAMP` | No | now() | No | Last update timestamp |

### Foreign Keys

| Column | References |
|--------|------------|
| `product_id` | `products.product_id` |
| `user_id` | `users.user_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `idx_user_cart_added_at` | NON-UNIQUE | `added_at` |
| `idx_user_cart_product_id` | NON-UNIQUE | `product_id` |
| `idx_user_cart_user_id` | NON-UNIQUE | `user_id` |
| `user_cart_user_id_product_id_key` | UNIQUE | `user_id, product_id` |

### Sample Data

| `id` | `user_id` | `product_id` | `quantity` | `added_at` | `updated_at` |
|---|---|---|---|---|---|
| 11235 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 82bfd93d-254c-4fd4-9aef-1551d1d28b87 | 12 | 2025-10-28 11:56:19.231986+05:30 | 2025-10-28 11:56:27.948254+05:30 |

---

## user_wishlist

**Record Count**: 2

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `id` | `BIGINT` | No | nextval('user_wishlist_id_seq'::regclass) | No | Primary identifier |
| `user_id` | `UUID` | No | None | No | Primary identifier |
| `product_id` | `UUID` | No | None | No | Primary identifier |
| `added_at` | `TIMESTAMP` | No | now() | No |  |

### Foreign Keys

| Column | References |
|--------|------------|
| `product_id` | `products.product_id` |
| `user_id` | `users.user_id` |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `idx_user_wishlist_added_at` | NON-UNIQUE | `added_at` |
| `idx_user_wishlist_product_id` | NON-UNIQUE | `product_id` |
| `idx_user_wishlist_user_id` | NON-UNIQUE | `user_id` |
| `user_wishlist_user_id_product_id_key` | UNIQUE | `user_id, product_id` |

### Sample Data

| `id` | `user_id` | `product_id` | `added_at` |
|---|---|---|---|
| 443 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | 0f40ac23-2f7d-4c28-92a7-7708a3ead3af | 2025-10-28 11:29:58.824107+05:30 |
| 444 | 002ddc13-5c90-466c-a4b8-9095fbf9cbb0 | da212b8d-9dec-45ff-ab97-f3f50e6fcac4 | 2025-10-28 11:54:03.058623+05:30 |

---

## users

**Record Count**: 200

### Schema

| Column | Type | Nullable | Default | Primary Key | Description |
|--------|------|----------|---------|-------------|-------------|
| `user_id` | `UUID` | No | None | No | Primary identifier |
| `email` | `VARCHAR` | Yes | None | No |  |
| `password_hash` | `VARCHAR` | Yes | None | No |  |
| `created_at` | `TIMESTAMP` | No | now() | No | Creation timestamp |
| `last_seen_at` | `TIMESTAMP` | Yes | None | No |  |
| `profile` | `JSON` | Yes | None | No |  |
| `is_anonymous` | `BOOLEAN` | No | None | No |  |
| `is_active` | `BOOLEAN` | No | None | No |  |
| `username` | `VARCHAR` | Yes | None | No |  |

### Indexes

| Name | Type | Columns |
|------|------|----------|
| `users_username_key` | UNIQUE | `username` |

### Sample Data

| `user_id` | `email` | `password_hash` | `created_at` | `last_seen_at` | `profile` | `is_anonymous` | `is_active` | `username` |
|---|---|---|---|---|---|---|---|---|
| 42edafbf-6622-438f-b91e-2835c41e02b5 | april59@example.net | 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 | 2025-10-26 22:27:15.669056+05:30 | 2025-10-27 03:53:29.415691+05:30 | {'name': 'Christina Singh', 'age': 19, 'location': 'Port Isaactown', 'preferences': {'favorite_categ... | False | True | user50 |
| a1ae20b4-1cff-4e31-ae1f-3bbdddf42f7b | davisduane@example.com | 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 | 2025-10-26 22:27:15.669056+05:30 | 2025-10-27 00:40:43.609246+05:30 | {'name': 'David Schneider', 'age': 56, 'location': 'Lake Lisa', 'preferences': {'favorite_categories... | False | True | user122 |
| a4864507-ae27-43b7-9b80-3bdd0b63dd0d | stephanie99@example.com | 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 | 2025-10-26 22:27:15.669056+05:30 | 2025-10-22 09:38:33.358910+05:30 | {'session_data': {'ip_address': '185.179.222.237', 'user_agent': 'Opera/8.25.(Windows CE; ky-KG) Pre... | True | True | user124 |
| a5fb70dc-dbbe-4f1b-a4b2-e737c61710ee | ashleywilson@example.com | 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 | 2025-10-26 22:27:15.669056+05:30 | 2025-10-24 19:23:00.392837+05:30 | {'session_data': {'ip_address': '111.142.194.117', 'user_agent': 'Mozilla/5.0 (compatible; MSIE 9.0;... | True | True | user126 |
| a7b30f90-e877-4be7-bb98-86366f2dd919 | elizabeth49@example.org | 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 | 2025-10-26 22:27:15.669056+05:30 | 2025-10-25 14:30:34.099982+05:30 | {'session_data': {'ip_address': '163.106.35.109', 'user_agent': 'Opera/8.56.(Windows 95; eo-US) Pres... | True | True | user127 |

---

