# Master Function Registry — Phase 0 Baseline

Legend: IMPLEMENTED = demonstrably present; PARTIAL = a subset exists; MISSING = required but absent; BLOCKED = cannot assess until competitor videos are supplied.

| ID | Category | Function | Current status | Notes |
|---|---|---|---|---|
| CORE-001 | Onboarding | Language selection RU/UZ/EN | PARTIAL | UI exists; full localization audit absent |
| CORE-002 | Onboarding | Rules acceptance | IMPLEMENTED | Stored in PostgreSQL |
| CORE-003 | Onboarding | Required channel check | PARTIAL | Bot API check exists; configuration hardcoded by env/default |
| CORE-004 | Onboarding | Persistent onboarding recovery | PARTIAL | DB state persists; full restart/E2E test absent |
| BUS-001 | Business | Business connection tracking | IMPLEMENTED | DB record + update handler |
| BUS-002 | Business | Business message intake | IMPLEMENTED | Basic path |
| BUS-003 | Business | Business message edit tracking | PARTIAL | Updates archive text only |
| BUS-004 | Business | Deleted message event capture | PARTIAL | IDs/event stored; retention/security incomplete |
| MSG-001 | Messages | Reverse | IMPLEMENTED | Pure transformation |
| MSG-002 | Messages | Remove spaces | IMPLEMENTED | Pure transformation |
| MSG-003 | Messages | Bubble text | IMPLEMENTED | Pure transformation |
| MSG-004 | Messages | Leet | IMPLEMENTED | Pure transformation |
| MSG-005 | Messages | Dumb/random case | IMPLEMENTED | Pure transformation |
| MSG-006 | Messages | Glitch | IMPLEMENTED | Pure transformation |
| MSG-007 | Messages | Spoiler formatter | IMPLEMENTED | Pure transformation |
| MSG-008 | Messages | Word splitter | IMPLEMENTED | Limited |
| MSG-009 | Messages | Heart decoration | IMPLEMENTED | Pure transformation |
| MSG-010 | Messages | Matrix effect | IMPLEMENTED | Pure transformation |
| MSG-011 | Messages | Coin | IMPLEMENTED | Random utility |
| MSG-012 | Messages | Controlled repeater | IMPLEMENTED | Max repeat limit |
| MSG-013 | Messages | Quote | PARTIAL | Depends on incoming business reply object |
| MSG-014 | Messages | Quick replies | PARTIAL | DB lookup exists; management UI absent |
| MSG-015 | Messages | Delayed message | PARTIAL | PTB JobQueue only; not durable |
| AUTO-001 | Automation | Basic auto-reply | PARTIAL | One global text + cooldown; no rules engine |
| AUTO-002 | Automation | Keyword/regex conditions | MISSING | |
| AUTO-003 | Automation | Working hours | MISSING | |
| AUTO-004 | Automation | Per-chat rules | MISSING | |
| AUTO-005 | Automation | Automation history | MISSING | |
| LIB-001 | Library | Quick replies | PARTIAL | Table exists |
| LIB-002 | Library | Saved voice | MISSING | |
| LIB-003 | Library | GIFs/images/files | MISSING | |
| LIB-004 | Library | Favorites/search/pagination | MISSING | |
| MEDIA-001 | Media | Video to circle | MISSING | |
| MEDIA-002 | Media | Video trim/merge/compress | MISSING | |
| MEDIA-003 | Media | Image processing | MISSING | Pillow dependency alone is not implementation |
| MEDIA-004 | Media | PDF tools | MISSING | |
| VOICE-001 | Voice | Audio conversion | MISSING | |
| FILE-001 | Files | File inspection | MISSING | |
| FILE-002 | Files | Archive/PDF operations | MISSING | |
| PRIV-001 | Privacy | Data export | MISSING | |
| PRIV-002 | Privacy | Data deletion | MISSING | |
| ADMIN-001 | Admin | User list/search | IMPLEMENTED | Basic |
| ADMIN-002 | Admin | User block/unblock | IMPLEMENTED | No fine-grained RBAC |
| ADMIN-003 | Admin | Ticket list/reply/close | PARTIAL | Basic workflow only |
| ADMIN-004 | Admin | Broadcast | PARTIAL | Immediate synchronous broadcast |
| ADMIN-005 | Admin | Function toggle | PARTIAL | Backend toggle exists for command paths |
| ADMIN-006 | Admin | Admin roles/permissions | MISSING | Role column exists but not enforced as RBAC |
| ADMIN-007 | Admin | Audit log | MISSING | Event table is not a proper admin audit log |
| ANALYTICS-001 | Analytics | DAU/WAU/MAU | MISSING | |
| ANALYTICS-002 | Analytics | Retention | MISSING | |
| ANALYTICS-003 | Analytics | Function usage | PARTIAL | Basic usage count exists |
| SEC-001 | Security | Rate limiting | MISSING | |
| SEC-002 | Security | Admin brute-force protection | MISSING | Session exists, attempts do not |
| SEC-003 | Security | File security | MISSING | No file engine |
| OPS-001 | Operations | Health endpoint | MISSING | |
| OPS-002 | Operations | Durable jobs | MISSING | |
| OPS-003 | Operations | Job recovery | MISSING | |
| OPS-004 | Operations | Webhook | MISSING | Polling only |
| OPS-005 | Operations | Alembic migrations | MISSING | Startup schema creation only |
| I18N-001 | Localization | RU/UZ/EN parity audit | MISSING | |
| AUDIT-001 | Quality | Button audit | MISSING | |
| AUDIT-002 | Quality | Function audit | MISSING | |
| AUDIT-003 | Quality | Security audit | MISSING | |
| AUDIT-004 | Quality | Final test report | MISSING | |
| COMP-001 | Competitor | Video feature inventory | BLOCKED | MP4 files absent from supplied ZIP |
