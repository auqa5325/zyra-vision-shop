#!/usr/bin/env python3
"""
Sync interactions to user state tables (cart, wishlist, purchases)
Processes interactions chronologically to build accurate current state
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# Database setup
engine = create_engine(settings.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def sync_interactions_to_user_states():
    """Sync interactions to user state tables by processing chronologically"""
    print("🔄 Syncing interactions to user state tables...")
    
    with SessionLocal() as session:
        # Clear existing state tables to rebuild from scratch
        print("🧹 Clearing existing user state tables...")
        session.execute(text("DELETE FROM user_cart"))
        session.execute(text("DELETE FROM user_wishlist"))
        # Note: We DON'T delete purchase_history as it's a historical record
        session.commit()
        
        # Get all users with interactions
        users = session.execute(text("""
            SELECT DISTINCT user_id FROM interactions 
            WHERE user_id IS NOT NULL
        """)).fetchall()
        
        print(f"Processing {len(users)} users...")
        
        total_cart_synced = 0
        total_wishlist_synced = 0
        total_purchases_synced = 0
        
        for user_row in users:
            user_id = user_row.user_id
            
            # Get all interactions for this user, ordered by time
            interactions = session.execute(text("""
                SELECT 
                    id, product_id, event_type, event_value, created_at
                FROM interactions
                WHERE user_id = :user_id AND product_id IS NOT NULL
                ORDER BY created_at ASC
            """), {'user_id': user_id}).fetchall()
            
            if not interactions:
                continue
            
            # Track current state for this user
            current_cart = {}  # {product_id: quantity}
            current_wishlist = set()  # {product_id}
            purchases_processed = set()  # {(product_id, created_at)} to avoid duplicates
            
            for interaction in interactions:
                product_id = interaction.product_id
                event_type = interaction.event_type
                event_value = float(interaction.event_value) if interaction.event_value else 1
                created_at = interaction.created_at
                
                # Handle cart interactions
                if event_type == 'add_to_cart':
                    quantity = int(event_value) if event_value >= 1 else 1
                    if product_id in current_cart:
                        current_cart[product_id] += quantity
                    else:
                        current_cart[product_id] = quantity
                
                elif event_type == 'remove_from_cart':
                    if product_id in current_cart:
                        # Remove specified quantity or all if not specified
                        remove_qty = int(event_value) if event_value > 0 else current_cart[product_id]
                        current_cart[product_id] = max(0, current_cart[product_id] - remove_qty)
                        if current_cart[product_id] == 0:
                            del current_cart[product_id]
                
                elif event_type == 'update_cart_quantity':
                    # Update cart quantity directly
                    new_quantity = int(event_value) if event_value > 0 else 0
                    if new_quantity > 0:
                        current_cart[product_id] = new_quantity
                    elif product_id in current_cart:
                        del current_cart[product_id]
                
                # Handle wishlist interactions
                elif event_type == 'wishlist':
                    # event_value > 0 or NULL/undefined means add to wishlist
                    # event_value = 0 means remove from wishlist
                    wishlist_value = float(interaction.event_value) if interaction.event_value is not None else 1
                    if wishlist_value > 0:
                        current_wishlist.add(product_id)
                    else:
                        # Explicitly remove (event_value = 0)
                        current_wishlist.discard(product_id)
                
                # Handle purchase interactions
                elif event_type == 'purchase':
                    # Purchase event_value should be 1 (quantity), not product price
                    quantity = int(event_value) if event_value >= 1 else 1
                    # Cap quantity at 100 to match Pydantic validation
                    quantity = min(100, quantity)
                    purchase_key = (product_id, created_at)
                    
                    if purchase_key not in purchases_processed:
                        # Get product price at time of purchase (or current price)
                        product_price = session.execute(text("""
                            SELECT price FROM products WHERE product_id = :product_id
                        """), {'product_id': product_id}).scalar()
                        
                        if product_price:
                            # Check if this exact purchase already exists
                            existing_purchase = session.execute(text("""
                                SELECT id FROM purchase_history
                                WHERE user_id = :user_id 
                                AND product_id = :product_id 
                                AND purchased_at = :purchased_at
                                LIMIT 1
                            """), {
                                'user_id': user_id,
                                'product_id': product_id,
                                'purchased_at': created_at
                            }).fetchone()
                            
                            if not existing_purchase:
                                unit_price = float(product_price)
                                total_price = unit_price * quantity
                                
                                # Cap values to fit NUMERIC(10,2) which allows up to 99,999,999.99
                                max_price = 99999999.99
                                if unit_price > max_price:
                                    unit_price = max_price
                                if total_price > max_price:
                                    total_price = max_price
                                
                                # Cap quantity if needed (to avoid overflow in total_price calculation)
                                max_quantity = int(max_price / unit_price) if unit_price > 0 else 10000
                                if quantity > max_quantity:
                                    quantity = max_quantity
                                    total_price = unit_price * quantity
                                
                                # Insert purchase record
                                session.execute(text("""
                                    INSERT INTO purchase_history 
                                    (user_id, product_id, quantity, unit_price, total_price, order_id, purchased_at, payment_method, payment_status)
                                    VALUES (:user_id, :product_id, :quantity, :unit_price, :total_price, :order_id, :purchased_at, :payment_method, :payment_status)
                                """), {
                                    'user_id': user_id,
                                    'product_id': product_id,
                                    'quantity': quantity,
                                    'unit_price': unit_price,
                                    'total_price': total_price,
                                    'order_id': str(uuid.uuid4()),
                                    'purchased_at': created_at,
                                    'payment_method': 'credit_card',
                                    'payment_status': 'completed'
                                })
                                
                                total_purchases_synced += 1
                            purchases_processed.add(purchase_key)
                        
                        # Remove from cart when purchased (purchase consumes cart items)
                        if product_id in current_cart:
                            # Reduce cart quantity by purchased quantity
                            current_cart[product_id] = max(0, current_cart[product_id] - quantity)
                            if current_cart[product_id] == 0:
                                del current_cart[product_id]
            
            # Now sync the final state to database tables
            # Sync cart
            for product_id, quantity in current_cart.items():
                if quantity > 0:
                    # Get the first add_to_cart timestamp for this product
                    first_added = session.execute(text("""
                        SELECT MIN(created_at) FROM interactions
                        WHERE user_id = :user_id 
                        AND product_id = :product_id 
                        AND event_type = 'add_to_cart'
                    """), {'user_id': user_id, 'product_id': product_id}).scalar()
                    
                    last_updated = session.execute(text("""
                        SELECT MAX(created_at) FROM interactions
                        WHERE user_id = :user_id 
                        AND product_id = :product_id 
                        AND event_type IN ('add_to_cart', 'remove_from_cart', 'update_cart_quantity')
                    """), {'user_id': user_id, 'product_id': product_id}).scalar()
                    
                    # Check if cart item already exists
                    existing_cart = session.execute(text("""
                    SELECT id FROM user_cart
                    WHERE user_id = :user_id AND product_id = :product_id
                    """), {'user_id': user_id, 'product_id': product_id}).fetchone()
                
                    if existing_cart:
                        # Update existing item
                        session.execute(text("""
                            UPDATE user_cart
                            SET quantity = :quantity, updated_at = :updated_at
                            WHERE user_id = :user_id AND product_id = :product_id
                        """), {
                            'user_id': user_id,
                            'product_id': product_id,
                            'quantity': quantity,
                            'updated_at': last_updated or datetime.now()
                        })
                    else:
                        # Insert new item
                        session.execute(text("""
                            INSERT INTO user_cart (user_id, product_id, quantity, added_at, updated_at)
                            VALUES (:user_id, :product_id, :quantity, :added_at, :updated_at)
                        """), {
                            'user_id': user_id,
                            'product_id': product_id,
                            'quantity': quantity,
                            'added_at': first_added or datetime.now(),
                            'updated_at': last_updated or datetime.now()
                        })
                        total_cart_synced += 1
            
            # Sync wishlist
            for product_id in current_wishlist:
                # Get the first wishlist add timestamp
                first_added = session.execute(text("""
                    SELECT MIN(created_at) FROM interactions
                    WHERE user_id = :user_id 
                    AND product_id = :product_id 
                    AND event_type = 'wishlist'
                    AND (event_value IS NULL OR event_value > 0)
                """), {'user_id': user_id, 'product_id': product_id}).scalar()
                
                # Check if wishlist item already exists
                existing = session.execute(text("""
                    SELECT id FROM user_wishlist
                    WHERE user_id = :user_id AND product_id = :product_id
                """), {'user_id': user_id, 'product_id': product_id}).fetchone()
                
                if not existing:
                    session.execute(text("""
                        INSERT INTO user_wishlist (user_id, product_id, added_at)
                        VALUES (:user_id, :product_id, :added_at)
                    """), {
                        'user_id': user_id,
                        'product_id': product_id,
                        'added_at': first_added or datetime.now()
                    })
                    total_wishlist_synced += 1
            
            # Commit periodically (every 100 users)
            if total_cart_synced % 100 == 0:
                session.commit()
        
        # Final commit
        session.commit()
        
        print(f"\n✅ Sync completed:")
        print(f"  - Cart items: {total_cart_synced}")
        print(f"  - Wishlist items: {total_wishlist_synced}")
        print(f"  - Purchase records: {total_purchases_synced}")
        print(f"  - Total synced: {total_cart_synced + total_wishlist_synced + total_purchases_synced}")

def verify_sync():
    """Verify the sync worked correctly"""
    print("\n🔍 Verifying sync...")
    
    with SessionLocal() as session:
        # Check totals
        total_cart_items = session.execute(text("SELECT COUNT(*) FROM user_cart")).scalar()
        total_wishlist_items = session.execute(text("SELECT COUNT(*) FROM user_wishlist")).scalar()
        total_purchases = session.execute(text("SELECT COUNT(*) FROM purchase_history")).scalar()
        
        print(f"Total cart items: {total_cart_items}")
        print(f"Total wishlist items: {total_wishlist_items}")
        print(f"Total purchases: {total_purchases}")
        
        # Check interactions vs synced state
        total_add_to_cart = session.execute(text("""
            SELECT COUNT(*) FROM interactions 
            WHERE event_type = 'add_to_cart' AND user_id IS NOT NULL
        """)).scalar()
        
        total_wishlist_interactions = session.execute(text("""
            SELECT COUNT(*) FROM interactions 
            WHERE event_type = 'wishlist' AND user_id IS NOT NULL
        """)).scalar()
        
        total_purchase_interactions = session.execute(text("""
            SELECT COUNT(*) FROM interactions 
            WHERE event_type = 'purchase' AND user_id IS NOT NULL
        """)).scalar()
        
        print(f"\n📊 Interactions summary:")
        print(f"  - add_to_cart interactions: {total_add_to_cart}")
        print(f"  - wishlist interactions: {total_wishlist_interactions}")
        print(f"  - purchase interactions: {total_purchase_interactions}")
        
        # Check a sample user if available
        sample_user = session.execute(text("""
            SELECT user_id FROM users LIMIT 1
        """)).fetchone()
        
        if sample_user:
            user_id = sample_user.user_id
            user_cart = session.execute(text("""
                SELECT COUNT(*) FROM user_cart WHERE user_id = :user_id
            """), {'user_id': user_id}).scalar()
            
            user_wishlist = session.execute(text("""
                SELECT COUNT(*) FROM user_wishlist WHERE user_id = :user_id
            """), {'user_id': user_id}).scalar()
            
            user_purchases = session.execute(text("""
                SELECT COUNT(*) FROM purchase_history WHERE user_id = :user_id
            """), {'user_id': user_id}).scalar()
            
            print(f"\n📋 Sample user {user_id}:")
            print(f"  - Cart items: {user_cart}")
            print(f"  - Wishlist items: {user_wishlist}")
            print(f"  - Purchases: {user_purchases}")

if __name__ == "__main__":
    sync_interactions_to_user_states()
    verify_sync()

