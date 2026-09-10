# Target Architecture — Phase 0

```text
Telegram
  │
  ├── User Bot updates ───────┐
  └── Admin Bot updates ──────┤
                              ▼
                        FastAPI Web Service
                         /webhook/user
                         /webhook/admin
                         /health
                         /ready
                              │
                    validation + update routing
                              │
              ┌───────────────┴────────────────┐
              ▼                                ▼
       User Bot Application              Admin Bot Application
              │                                │
              └───────────────┬────────────────┘
                              ▼
                       Service / Domain Layer
                              │
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
   Function Registry      Automation Engine     Support
          │                   │                    │
          ├── Media Jobs      ├── Scheduler       ├── Tickets
          ├── Text Tools      └── Rules           └── Notifications
          └── Telegram Tools
                              │
                              ▼
                       Durable Job Queue
                              │
                              ▼
                         Worker Process
                              │
              ┌───────────────┼─────────────────┐
              ▼               ▼                 ▼
          PostgreSQL      Object Storage      Telegram API
```

## Persistence rule

Critical state belongs in PostgreSQL. RAM may be used only as a cache/optimization, never as the source of truth.

## Render deployment

- Web service: FastAPI + webhook endpoints.
- Background worker: durable job processor.
- Optional Key Value/Redis: shared queue/cache where needed.
- PostgreSQL/Supabase: persistent state.
- Object storage: large media.

Render documents web services for HTTP applications and background workers for continuous queue processing. citeturn1search0turn1search1
