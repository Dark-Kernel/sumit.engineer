---
title: ss command is the modern replacement for netstat
date: 2025-01-26
tags: [linux, networking, cli]
---

`ss` is faster and provides more detailed socket information. Use `ss -tlnp` to show listening TCP ports with process info.

```bash
# Show listening TCP ports with process names
ss -tlnp

# Show established connections to specific port
ss -t state established '( dport = :80 or sport = :80 )'
```

**Bonus:** Combine with `watch` for real-time monitoring: `watch -n 1 ss -tlnp`
