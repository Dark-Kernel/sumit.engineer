---
title: PostgreSQL UPSERT with ON CONFLICT in Python
date: 2025-01-27
tags: [python, database, postgres]
---

PostgreSQL's `ON CONFLICT` clause is perfect for idempotent operations. Much cleaner than try/except INSERT/UPDATE patterns.

```python
INSERT INTO users (email, name) 
VALUES (%s, %s)
ON CONFLICT (email) 
DO UPDATE SET 
    name = EXCLUDED.name,
    updated_at = NOW()
```

The `EXCLUDED` keyword refers to the values that were attempted to be inserted.
