---
title: Docker multi-stage builds can share intermediate layers
date: 2025-01-28
tags: [docker, devops]
---

Using `--target` flag allows building specific stages, and you can reference previous stages with `COPY --from=stage_name`. Great for separating build tools from runtime.

```dockerfile
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runtime
COPY --from=builder /app/node_modules ./node_modules
```

**Pro tip:** Name your stages descriptively for easier referencing later.
