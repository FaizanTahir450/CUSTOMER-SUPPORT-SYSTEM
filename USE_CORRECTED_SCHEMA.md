# ⚠️ IMPORTANT: Use the CORRECTED Schema File

## 📌 Which SQL File to Use

### ✅ **USE THIS ONE:** `complete_schema_CORRECTED.sql`

This schema matches EXACTLY with:
- ✓ backend-nodejs code (signup.ts, login.ts, passwordReset.ts)
- ✓ backend-python code (memory.py, poller.py, database.py)
- ✓ All existing database queries

### ❌ **DO NOT USE** `complete_schema.sql`

This original schema has naming mismatches:
- ❌ `support_memory` instead of `memory` (Python will fail)
- ❌ Missing `user_id` field (Python queries won't work)
- ❌ Missing `order_id` field (Both backends use this)
- ❌ Wrong field sizes (order_id, status)

---

## 🔑 Key Differences

### users table
| Field | Original | Corrected | Code Uses |
|-------|----------|-----------|-----------|
| memory column | `support_memory` | `memory` | memory.py line 30 |
| user_id field | Missing | Added | memory.py, poller.py |

### orders table
| Field | Original | Corrected | Code Uses |
|-------|----------|-----------|-----------|
| order_id | Missing | Added VARCHAR 64 | database.py, db.ts |
| order_number size | VARCHAR 50 | VARCHAR 64 | db.ts VARCHAR 64 |
| status size | VARCHAR 50 | VARCHAR 32 | db.ts VARCHAR 32 |

---

## ✅ Steps to Deploy

1. **Use the CORRECTED file:**
   ```
   backend-python/sql/complete_schema_CORRECTED.sql
   ```

2. **In Supabase:**
   - SQL Editor → New Query
   - Copy entire contents from `complete_schema_CORRECTED.sql`
   - Paste into editor
   - Click Run

3. **Verify:**
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'users'
   ORDER BY ordinal_position;
   ```
   
   Should show: `id`, `user_id`, `memory`, `gmail_id`, etc.

---

## 📋 Quick Checklist

- [ ] Use `complete_schema_CORRECTED.sql`
- [ ] Run in Supabase SQL Editor
- [ ] Verify users table has `memory` column (not `support_memory`)
- [ ] Verify users table has `user_id` field
- [ ] Verify orders table has `order_id` field
- [ ] Test backend connections

**Created:** March 2025  
**Status:** Ready for immediate deployment ✅
