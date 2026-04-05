---
title: ssh tunnel
date: 2026-04-03
tags: [ssh, devops]
---

1. From client to server

```bash
ssh -N -L 8080:localhost:8080 user@server
```

2. From server to client

```bash
ssh -N -R 8080:localhost:8080 user@server
```

**Pro tip:**: You can also use `ssh -N -f -L 8080:localhost:8080 user@server`

> You can do it always :)
