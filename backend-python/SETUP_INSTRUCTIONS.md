# Backend-Python Setup Instructions

## ✅ Completed Tasks

### 1. **Function Naming Bug Fixed** ✓
Changed `get_mysql_service()` → `get_db_service()` across all files:
- `app/models/database.py`
- `app.py`
- `app/main.py`
- `app/services/email/poller.py`
- `tests/test_app.py`
- `tests/test_db.py`

**Why:** The function returns a PostgreSQL/Supabase service, not MySQL. This clarifies the actual database being used.

---

## 📋 Next Steps: Create Orders Table in Supabase

### How to Create the Orders Table

#### **Option 1: Using Supabase Web Console (Easiest)**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Click **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy the SQL from `sql/orders_table.sql`
6. Paste it into the editor
7. Click **Run** (or press Ctrl+Enter)

You should see: ✓ "Success. No rows returned"

#### **Option 2: Using Supabase CLI**

```bash
# From the backend-python directory
supabase db push

# Or paste the SQL directly
supabase sql < sql/orders_table.sql
```

#### **Option 3: Manual SQL (PostgreSQL Client)**

```bash
psql -h aws-1-ap-south-1.pooler.supabase.com -U postgres -d postgres -p 6543

# Then paste the contents of sql/orders_table.sql
```

---

## 📊 Orders Table Structure

The table includes:
- **order_id** (UUID) - Primary key, auto-generated
- **user_id** (UUID) - Foreign key referencing users table
- **status** (VARCHAR) - pending, processing, shipped, delivered, cancelled
- **total** (DECIMAL) - Order total amount
- **created_at** (TIMESTAMP) - When order was created
- **updated_at** (TIMESTAMP) - When order was last updated

**Indexes created for performance:**
- `user_id` - Fast lookup of user's orders
- `created_at` - Fast sorting by date
- `status` - Fast filtering by order status

---

## ✅ Verify the Table Was Created

After running the SQL, verify it worked:

```sql
-- This query lists all tables in your database
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- You should see 'orders' in the list
```

---

## 🔧 Environment Variables (.env)

Your `.env` file already has the required variables:

```dotenv
OPENROUTER_API_KEY=sk-or-v1-...
SUPABASE_DB_URL=postgresql://postgres...
```

**Additional variables to add if needed:**

```dotenv
# Gmail (for email support feature)
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
GMAIL_SENDER_NAME=support@lamaretail.com

# LLM Configuration
MODEL_NAME=google/gemini-2.5-flash

# Optional: Security API Key
API_KEY=your-secret-api-key-here

# PDF for knowledge base
PDF_PATH=./Lama1.pdf
```

---

## 🧪 Test the Database Connection

Run this command to test if the database is working:

```bash
python -c "from app.models.database import init_database; init_database()"
```

If successful, you'll see:
```
Supabase database connected successfully
Database Schema: ============================================================
...orders table schema...
============================================================
```

---

## 📝 What's Left to Do

- [ ] Create orders table in Supabase (👈 **DO THIS NEXT**)
- [ ] Add JWT validation middleware (will do at the end)
- [ ] Fix Gemini service model name in frontend
- [ ] Add authToken header to frontend API calls
- [ ] Create missing constants.tsx and types.ts in frontend
- [ ] Add email configuration (SMTP)

---

## 🔗 Useful Links

- [Supabase SQL Editor](https://supabase.com/dashboard)
- [PostgreSQL CREATE TABLE Reference](https://www.postgresql.org/docs/current/sql-createtable.html)
- [FastAPI Database Integration](https://fastapi.tiangolo.com/)
