"""
Database migration script to create user state tables
Run this to create the new optimized tables
"""

from sqlalchemy import create_engine, text
from app.config import settings

def create_user_state_tables():
    """Create the new user state tables"""
    engine = create_engine(settings.get_database_url())
    
    with engine.connect() as conn:
        print("🔧 Creating user state tables...")
        
        # Create user_cart table
        print("Creating user_cart table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_cart (
                id BIGSERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
                added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                UNIQUE(user_id, product_id)
            )
        """))
        
        # Create user_wishlist table
        print("Creating user_wishlist table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_wishlist (
                id BIGSERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
                added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                UNIQUE(user_id, product_id)
            )
        """))
        
        # Create purchase_history table
        print("Creating purchase_history table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS purchase_history (
                id BIGSERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
                unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
                total_price NUMERIC(10,2) NOT NULL CHECK (total_price >= 0),
                order_id UUID,
                purchased_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                payment_method VARCHAR,
                payment_status VARCHAR DEFAULT 'completed'
            )
        """))
        
        # Create indexes for performance
        print("Creating indexes...")
        
        # Cart indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_cart_user_id ON user_cart (user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_cart_product_id ON user_cart (product_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_cart_added_at ON user_cart (added_at DESC)"))
        
        # Wishlist indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_wishlist_user_id ON user_wishlist (user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_wishlist_product_id ON user_wishlist (product_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_wishlist_added_at ON user_wishlist (added_at DESC)"))
        
        # Purchase history indexes
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_history_user_id ON purchase_history (user_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_history_product_id ON purchase_history (product_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_history_order_id ON purchase_history (order_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_history_purchased_at ON purchase_history (purchased_at DESC)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_history_user_purchased ON purchase_history (user_id, purchased_at DESC)"))
        
        conn.commit()
        print("✅ All user state tables created successfully!")

def migrate_existing_data():
    """Migrate existing interaction data to new tables"""
    engine = create_engine(settings.get_database_url())
    
    with engine.connect() as conn:
        print("🔄 Migrating existing interaction data...")
        
        # Migrate cart data (add_to_cart interactions)
        print("Migrating cart data...")
        conn.execute(text("""
            INSERT INTO user_cart (user_id, product_id, quantity, added_at)
            SELECT 
                user_id,
                product_id,
                SUM(event_value)::INTEGER as quantity,
                MAX(created_at) as added_at
            FROM interactions 
            WHERE event_type = 'add_to_cart' 
            AND user_id IS NOT NULL 
            AND product_id IS NOT NULL
            GROUP BY user_id, product_id
            ON CONFLICT (user_id, product_id) DO NOTHING
        """))
        
        # Migrate wishlist data (wishlist interactions with event_value = 1)
        print("Migrating wishlist data...")
        conn.execute(text("""
            INSERT INTO user_wishlist (user_id, product_id, added_at)
            SELECT DISTINCT ON (user_id, product_id)
                user_id,
                product_id,
                created_at as added_at
            FROM interactions 
            WHERE event_type = 'wishlist' 
            AND event_value = 1
            AND user_id IS NOT NULL 
            AND product_id IS NOT NULL
            ORDER BY user_id, product_id, created_at DESC
            ON CONFLICT (user_id, product_id) DO NOTHING
        """))
        
        # Migrate purchase data
        print("Migrating purchase data...")
        conn.execute(text("""
            INSERT INTO purchase_history (user_id, product_id, quantity, unit_price, total_price, purchased_at)
            SELECT 
                user_id,
                product_id,
                1 as quantity,  -- Default quantity, could be improved with product price lookup
                event_value as unit_price,
                event_value as total_price,
                created_at as purchased_at
            FROM interactions 
            WHERE event_type = 'purchase' 
            AND user_id IS NOT NULL 
            AND product_id IS NOT NULL
            ON CONFLICT DO NOTHING
        """))
        
        conn.commit()
        print("✅ Data migration completed!")

def verify_migration():
    """Verify the migration was successful"""
    engine = create_engine(settings.get_database_url())
    
    with engine.connect() as conn:
        print("🔍 Verifying migration...")
        
        # Check table counts
        cart_count = conn.execute(text("SELECT COUNT(*) FROM user_cart")).scalar()
        wishlist_count = conn.execute(text("SELECT COUNT(*) FROM user_wishlist")).scalar()
        purchase_count = conn.execute(text("SELECT COUNT(*) FROM purchase_history")).scalar()
        
        print(f"Cart items migrated: {cart_count}")
        print(f"Wishlist items migrated: {wishlist_count}")
        print(f"Purchase records migrated: {purchase_count}")
        
        # Check sample data
        print("\nSample cart data:")
        cart_sample = conn.execute(text("SELECT * FROM user_cart LIMIT 3")).fetchall()
        for row in cart_sample:
            print(f"  User: {row[1]}, Product: {row[2]}, Quantity: {row[3]}")
        
        print("\nSample wishlist data:")
        wishlist_sample = conn.execute(text("SELECT * FROM user_wishlist LIMIT 3")).fetchall()
        for row in wishlist_sample:
            print(f"  User: {row[1]}, Product: {row[2]}, Added: {row[3]}")
        
        print("\nSample purchase data:")
        purchase_sample = conn.execute(text("SELECT * FROM purchase_history LIMIT 3")).fetchall()
        for row in purchase_sample:
            print(f"  User: {row[1]}, Product: {row[2]}, Total: {row[5]}, Date: {row[7]}")

if __name__ == "__main__":
    create_user_state_tables()
    migrate_existing_data()
    verify_migration()

