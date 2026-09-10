# Telegram Capability Matrix — Phase 0

| Capability | Official support | Decision |
|---|---|---|
| BusinessConnection updates | Yes | Implement |
| Business messages | Yes | Implement |
| Edited business messages | Yes | Implement |
| Deleted business messages | Yes | Implement with content-retention caveat |
| Send on behalf of business | Permission-dependent | Gate by rights |
| Delete business messages | Yes for supported operations/rights | Gate by rights; do not assume universal support |
| Edit business messages | Business-capable | Verify method/rights per operation |
| Business profile name/username/bio/photo | Current Telegram Business capability exists | Implement only after checking PTB exposure; otherwise isolate adapter |
| Advanced MTProto business operations | Exists | Do not assume Bot API support; isolate as optional adapter |
| Webhook secret token | Yes | Implement |
| Webhook allowed_updates | Yes | Implement |
| Durable scheduled jobs | Not a Telegram feature | Application/PostgreSQL concern |
| Local media conversion | Not Telegram-dependent | Implement via worker/ffmpeg/Pillow where appropriate |
| Voice cloning | Not required | Exclude |
| Doxxing/PII lookup | Unsafe/unwanted | Exclude |
| Unlimited spam | Unsafe/against project policy | Exclude |
