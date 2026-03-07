# Backend-NodeJS: MySQL → Supabase/PostgreSQL Migration Plan

## 🔍 Current State

**Database:** MySQL (mysql2/promise)
**Files Using DB:**
- `src/lib/db.ts` - Connection pool
- `src/controllers/signup.ts` - INSERT user, SELECT by email
- `src/controllers/login.ts` - SELECT user by email  
- `src/controllers/passwordReset.ts` - INSERT token, UPDATE password

**Query Style:** MySQL with `?` placeholders
**UUID Generation:** `UUID()` in MySQL

---

## 📋 Migration Steps

### Step 1: Replace DB Library
```
Remove: mysql2/promise
Add: @supabase/supabase-js
```

### Step 2: Update Connection (src/lib/db.ts)
```typescript
// OLD
import {createPool} from 'mysql2/promise';
export const pool = createPool({...});

// NEW
import { createClient } from '@supabase/supabase-js';
export const supabase = createClient(url, key);
```

### Step 3: Query Syntax Changes

#### MySQL → PostgreSQL Placeholders
```sql
-- MySQL
WHERE email = ?
INSERT INTO users (id, email) VALUES (?, ?)

-- PostgreSQL
WHERE email = $1
INSERT INTO users (id, email) VALUES ($1, $2)
```

#### Type Changes
```typescript
// MySQL
import type { RowDataPacket } from 'mysql2';

// PostgreSQL - Supabase returns arrays/objects directly
```

#### UUID Generation
```typescript
// MySQL
UUID()  -- in SQL

// PostgreSQL - use uuid library client-side
import { v4 as uuidv4 } from 'uuid';
const id = uuidv4();
```

### Step 4: Query Results Format
```typescript
// MySQL
const [users] = await pool.execute(); // Returns [rows, fields]
const user = users[0];

// Supabase PostgreSQL  
const { data, error } = await supabase
  .from('users')
  .select()
  .eq('email', email);
const user = data?.[0];
```

---

## 📝 Files to Update

| File | Changes | Complexity |
|------|---------|------------|
| `src/lib/db.ts` | Connection, remove ensureSchema() | High |
| `src/controllers/signup.ts` | Query syntax, UUID generation | Medium |
| `src/controllers/login.ts` | Query syntax | Low |
| `src/controllers/passwordReset.ts` | Query syntax, parameter binding | Medium |
| `package.json` | Replace mysql2 with @supabase/supabase-js | Low |

---

## 🔑 Environment Variables

**Update `.env`:**
```env
# Remove MySQL
MYSQL_HOST=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=
MYSQL_PORT=

# Add Supabase
SUPABASE_URL=https://ovjcaowxkvjlypqchcuy.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_DB_URL=postgresql://postgres.ovjcaowxkvjlypqchcuy:password@...
```

---

## ✅ Steps to Execute

1. ✅ Tables already created in Supabase (from complete_schema_CORRECTED.sql)
2. ⏳ Update package.json (replace mysql2)
3. ⏳ Create new db.ts with Supabase connection
4. ⏳ Update signup.ts for PostgreSQL queries
5. ⏳ Update login.ts for PostgreSQL queries
6. ⏳ Update passwordReset.ts for PostgreSQL queries
7. ⏳ Update .env.example
8. ⏳ Test all endpoints

---

## 🔄 Query Translation Examples

### Signup - Check if user exists
```typescript
// MySQL
const [existingUser] = await pool.execute<RowDataPacket[]>(
    `select id from users where email = ?`, 
    [email]
);

// PostgreSQL
const { data, error } = await supabase
    .from('users')
    .select('id')
    .eq('email', email)
    .single() // Only expect one result
    .maybeSingle(); // Or null if not found
```

### Signup - Insert new user
```typescript
// MySQL
await pool.execute(
    `INSERT INTO users (id, email, password_hash, name) values (UUID(), ?, ?, ?)`,
    [email, passwordHash, name || null]
);

// PostgreSQL
const userId = uuidv4();
const { data, error } = await supabase
    .from('users')
    .insert([{
        id: userId,
        email: email,
        password_hash: passwordHash,
        name: name || null
    }]);
```

### Login - Get user by email
```typescript
// MySQL
const [users] = await pool.execute<RowDataPacket[]>(
    `select id, email, password_hash, name, created_at from users where email = ?`,
    [email]
);
const user = users[0];

// PostgreSQL
const { data, error } = await supabase
    .from('users')
    .select('id, email, password_hash, name, created_at')
    .eq('email', email)
    .single();
const user = data;
```

---

## ⚠️ Important Notes

1. **ensureSchema()** - Schema already exists in Supabase, so we can remove this function
2. **UUID()** - No longer available in SQL, use uuid library client-side
3. **Transactions** - May need adjustments if they exist
4. **Connection pooling** - Supabase handles this automatically
5. **Error handling** - PostgreSQL error codes are different from MySQL

---

## Next: Create migration files

Ready to start?
