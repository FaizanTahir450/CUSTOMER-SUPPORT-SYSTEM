-- ============================================================================
-- CORRECTED SCHEMA - Matches Actual Code Usage
-- Database: PostgreSQL (Supabase)
-- Updated: Verified against backend-nodejs and backend-python code
-- ============================================================================

-- ============================================================================
-- 1. USERS TABLE - CORRECTED (Matches All Code Usage)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    -- Node.js uses: id, email, password_hash, name, created_at, updated_at
    -- Python uses: user_id, memory, gmail_id, updated_at
    
    -- Use "id" as primary key (Node.js convention)
    -- Python can use either id or user_id - we'll support both
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE DEFAULT gen_random_uuid(), -- Alias for Python compatibility
    
    -- Authentication (from Node.js)
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    
    -- Gmail Integration (from Python email poller)
    gmail_id VARCHAR(255) UNIQUE,
    gmail_email VARCHAR(255),
    
    -- AI Support Memory (from Python memory.py)
    memory JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_id ON users(id);
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_gmail_id ON users(gmail_id);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- 2. PASSWORD_RESET_TOKENS TABLE - EXACT MATCH
-- ============================================================================
-- From Node.js: id, user_id, token, expires_at, used_at, created_at
-- All columns match exactly
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT token_not_empty CHECK (token != '')
);

CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- ============================================================================
-- 3. ORDERS TABLE - CORRECTED (Unified from Node.js and Python)
-- ============================================================================
-- Node.js MySQL uses: id, order_id, user_id, status, total, created_at
-- Python Supabase uses: order_id, user_id, status, total, created_at
-- 
-- Consolidation: Use order_number (unique) + support for order_id
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Node.js calls this "order_id" (VARCHAR 64, UNIQUE)
    -- Python also uses order_id
    -- Rename to "order_number" in PostgreSQL for clarity, keep order_id as alias
    order_number VARCHAR(64) NOT NULL UNIQUE,
    order_id VARCHAR(64) NOT NULL UNIQUE, -- Alias for backward compatibility
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Order Status (Node.js)
    status VARCHAR(32) NOT NULL DEFAULT 'pending',  -- pending, processing, shipped, delivered, cancelled
    payment_status VARCHAR(50) DEFAULT 'pending',   -- pending, paid, refunded
    
    -- Pricing
    subtotal DECIMAL(10, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL,  -- Required (from both Node.js and Python)
    
    -- Shipping Address
    shipping_address_line1 VARCHAR(255),
    shipping_address_line2 VARCHAR(255),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    shipping_country VARCHAR(100),
    
    -- Billing Address
    billing_address_line1 VARCHAR(255),
    billing_address_line2 VARCHAR(255),
    billing_city VARCHAR(100),
    billing_state VARCHAR(100),
    billing_postal_code VARCHAR(20),
    billing_country VARCHAR(100),
    
    -- Shipping
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    
    -- Notes
    customer_notes TEXT,
    internal_notes TEXT,
    
    -- Timestamps (ONLY created_at used in code, but good to add others)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Python: ORDER BY DESC
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP
);

CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- ============================================================================
-- 4. ORDER_ITEMS TABLE (Required by orders)
-- ============================================================================
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT quantity_positive CHECK (quantity > 0)
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- ============================================================================
-- 5. PRODUCTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Pricing
    price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    
    -- Inventory
    stock_quantity INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    
    -- Categorization
    category VARCHAR(100),
    subcategory VARCHAR(100),
    tags VARCHAR(500),
    
    -- Sustainability
    is_sustainable BOOLEAN DEFAULT true,
    sustainability_rating DECIMAL(3, 2),
    material VARCHAR(255),
    
    -- Media
    image_url VARCHAR(500),
    gallery_urls TEXT[],
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_is_active ON products(is_active);

-- ============================================================================
-- 6. CART_ITEMS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    quantity INT NOT NULL DEFAULT 1,
    price_at_time DECIMAL(10, 2) NOT NULL,
    
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT quantity_positive CHECK (quantity > 0)
);

CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);
CREATE UNIQUE INDEX idx_cart_items_unique ON cart_items(user_id, product_id);

-- ============================================================================
-- 7. CONVERSATIONS TABLE (AI Support)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    title VARCHAR(255),
    topic VARCHAR(100),
    
    status VARCHAR(50) DEFAULT 'active',
    
    resolution_summary TEXT,
    resolved_at TIMESTAMP,
    resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- ============================================================================
-- 8. CONVERSATION_MESSAGES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    
    sender_type VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    message TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    
    model_used VARCHAR(100),
    confidence_score DECIMAL(3, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_conversation_messages_sender_type ON conversation_messages(sender_type);
CREATE INDEX idx_conversation_messages_created_at ON conversation_messages(created_at);

-- ============================================================================
-- 9. CONVERSATION_MEMORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    memory_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    summary TEXT,
    
    message_count INT DEFAULT 0,
    compressed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_memory_user_id ON conversation_memory(user_id);
CREATE INDEX idx_conversation_memory_conversation_id ON conversation_memory(conversation_id);

-- ============================================================================
-- 10. PRODUCT_REVIEWS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
    
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    review_text TEXT,
    
    is_verified_purchase BOOLEAN DEFAULT false,
    helpful_count INT DEFAULT 0,
    unhelpful_count INT DEFAULT 0,
    
    is_approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_user_product_review UNIQUE(product_id, user_id)
);

CREATE INDEX idx_product_reviews_product_id ON product_reviews(product_id);
CREATE INDEX idx_product_reviews_user_id ON product_reviews(user_id);

-- ============================================================================
-- 11. ADMIN_USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    role VARCHAR(50),
    department VARCHAR(100),
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX idx_admin_users_role ON admin_users(role);
CREATE INDEX idx_admin_users_is_active ON admin_users(is_active);

-- ============================================================================
-- 12. EMAIL_LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    email_type VARCHAR(100),
    
    status VARCHAR(50) DEFAULT 'sent',
    
    message_id VARCHAR(255),
    external_id VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    opened_at TIMESTAMP
);

CREATE INDEX idx_email_logs_user_id ON email_logs(user_id);
CREATE INDEX idx_email_logs_recipient_email ON email_logs(recipient_email);
CREATE INDEX idx_email_logs_email_type ON email_logs(email_type);

-- ============================================================================
-- 13. AUDIT_LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    
    old_values JSONB,
    new_values JSONB,
    
    ip_address INET,
    user_agent VARCHAR(500),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity_type ON audit_logs(entity_type);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- ============================================================================
-- 14. PROMO_CODES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS promo_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) NOT NULL UNIQUE,
    
    description VARCHAR(255),
    discount_type VARCHAR(50),
    discount_value DECIMAL(10, 2) NOT NULL,
    
    minimum_order_value DECIMAL(10, 2),
    max_uses INT,
    current_uses INT DEFAULT 0,
    
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_promo_codes_code ON promo_codes(code);

-- ============================================================================
-- 15. REFUNDS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE RESTRICT,
    
    reason VARCHAR(255),
    refund_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processed_by UUID REFERENCES admin_users(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_refunds_order_id ON refunds(order_id);
CREATE INDEX idx_refunds_status ON refunds(status);

-- ============================================================================
-- TRIGGERS & FUNCTIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_update_timestamp BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER products_update_timestamp BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER orders_update_timestamp BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER conversations_update_timestamp BEFORE UPDATE ON conversations
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER cart_items_update_timestamp BEFORE UPDATE ON cart_items
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER refunds_update_timestamp BEFORE UPDATE ON refunds
FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- VERIFICATION QUERIES (Run these after schema creation)
-- ============================================================================

-- Verify all tables exist
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Verify critical columns exist
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'users';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'orders';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'password_reset_tokens';
