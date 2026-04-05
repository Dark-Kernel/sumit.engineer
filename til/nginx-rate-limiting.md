---
title: Nginx rate limiting with burst and nodelay
date: 2025-01-25
tags: [nginx, devops, networking]
---

The `burst` parameter allows temporary spikes, while `nodelay` processes burst requests immediately instead of queuing them.

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend;
}
```

This allows 20 requests to burst through immediately before rate limiting kicks in.
