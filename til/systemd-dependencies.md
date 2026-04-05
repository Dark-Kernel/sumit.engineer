---
title: systemd service dependencies with After= vs Requires=
date: 2025-01-29
tags: [linux, systemd, devops]
---

Discovered the subtle difference: `After=` only controls startup order, while `Requires=` creates a dependency that stops this service if the required service fails. Use `Wants=` for loose coupling.

```bash
# Start after network, but don't fail if network fails
After=network.target
Wants=network.target

# vs requiring PostgreSQL to be running
Requires=postgresql.service
After=postgresql.service
```

The key insight: **Wants=** is what you want for most cases - it starts the service but doesn't cascade failures.
