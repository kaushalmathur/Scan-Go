-- Scan & Go Multi-Tenant Database Schema

-- Enable Row-Level Security
-- To use RLS, ensure the database session sets 'app.current_merchant_id'
-- Example: SET local app.current_merchant_id = '123';

-----------------------------------------
-- 1. MERCHANTS (The Tenants)
-----------------------------------------
CREATE TABLE merchants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50) DEFAULT 'basic', -- e.g., 'basic', 'premium', 'enterprise'
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_merchants_name ON merchants(name);

-----------------------------------------
-- 2. USERS (Customers)
-----------------------------------------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES merchants(id) ON DELETE CASCADE,
    session_token UUID DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_store_id ON users(store_id);
CREATE INDEX idx_users_email ON users(email);

-----------------------------------------
-- 3. PRODUCTS
-----------------------------------------
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    merchant_id INTEGER REFERENCES merchants(id) ON DELETE CASCADE,
    sku VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0),
    stock INTEGER DEFAULT 0 CHECK (stock >= 0),
    category VARCHAR(100),
    barcode VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: SKU should be unique per merchant
    CONSTRAINT unique_sku_per_merchant UNIQUE (merchant_id, sku),
    -- Constraint: Barcode uniqueness depends on business logic, but typically unique per merchant or global
    CONSTRAINT unique_barcode_per_merchant UNIQUE (merchant_id, barcode)
);

CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_category ON products(category);

-----------------------------------------
-- 4. TRANSACTIONS
-----------------------------------------
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    merchant_id INTEGER REFERENCES merchants(id) ON DELETE CASCADE,
    amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_merchant_id ON transactions(merchant_id);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

-----------------------------------------
-- 5. CART ITEMS (Line Items)
-----------------------------------------
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL -- Snapshotted price at time of purchase
);

CREATE INDEX idx_cart_items_transaction_id ON cart_items(transaction_id);

-----------------------------------------
-- 6. SCANS (Audit/Log of user scanning activity)
-----------------------------------------
CREATE TABLE scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    barcode VARCHAR(100) NOT NULL,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_barcode ON scans(barcode);

-----------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES
-----------------------------------------

-- 1. Enable RLS on core multi-tenant tables
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;

-- 2. Define Policies
-- These policies assume the application sets 'app.current_merchant_id' in a transaction variable

-- Products Policy
CREATE POLICY merchant_products_access ON products
    FOR ALL
    TO PUBLIC
    USING (merchant_id = NULLIF(current_setting('app.current_merchant_id', true), '')::integer);

-- Transactions Policy
CREATE POLICY merchant_transactions_access ON transactions
    FOR ALL
    TO PUBLIC
    USING (merchant_id = NULLIF(current_setting('app.current_merchant_id', true), '')::integer);

-- Cart Items Policy (accessed through transaction join or directly if merchant_id was present)
-- Since cart_items doesn't have merchant_id, we check the linked transaction
CREATE POLICY merchant_cart_items_access ON cart_items
    FOR ALL
    TO PUBLIC
    USING (
        EXISTS (
            SELECT 1 FROM transactions t 
            WHERE t.id = cart_items.transaction_id 
            AND t.merchant_id = NULLIF(current_setting('app.current_merchant_id', true), '')::integer
        )
    );

-- Users Policy (Merchants can see users who have interacted with their store)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY merchant_users_access ON users
    FOR ALL
    TO PUBLIC
    USING (store_id = NULLIF(current_setting('app.current_merchant_id', true), '')::integer);

-- Scans Policy
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
CREATE POLICY merchant_scans_access ON scans
    FOR ALL
    TO PUBLIC
    USING (
        EXISTS (
            SELECT 1 FROM products p 
            WHERE p.id = scans.product_id 
            AND p.merchant_id = NULLIF(current_setting('app.current_merchant_id', true), '')::integer
        )
    );
