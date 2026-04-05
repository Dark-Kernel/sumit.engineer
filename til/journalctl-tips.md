---
title: journalctl can follow logs in real-time like tail -f
date: 2025-01-24
tags: [linux, systemd, devops]
---

Use `journalctl -f` to follow logs, `-u service_name` for specific services, and `--since "1 hour ago"` for time-based filtering.

```bash

 # Follow nginx logs from the last hour
journalctl -u nginx -f --since "1 hour ago"

 # Show logs with specific priority
journalctl -p err -f

 # Follow all logs for a specific binary
journalctl -f /usr/sbin/nginx
```

**Pro tip:** Use `--no-pager` when scripting to avoid interactive behavior.
