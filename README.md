# AADi INFINITY LABS

**Indian Roots. Infinite Vision.**

Corporate website and centralized application administration dashboard, built with Python 3 and SQLite.

## Local setup (macOS)

1. Download/clone this repository.
2. Open Terminal in the repository directory.
3. Run `bash START.command` or run `AADI_ADMIN_PASSWORD='choose-a-long-unique-password' python3 app.py`.
4. Visit http://127.0.0.1:8080 for the website and http://127.0.0.1:8080/admin for administration.

The launcher requests a password of at least 12 characters. Six example apps start as **drafts**, not publicly listed. Applications can be published only when privacy, terms, and support text are filled in. The SQLite database is created locally as `site.db` and is **excluded from Git**.

## Features

- Premium midnight-black and gold responsive corporate site
- Application portfolio and individual application pages
- Central administrator sign-in, editable company content and product information
- Per-app privacy, terms, support and App Store URL fields
- Support and account deletion **request capture** (manual review only)
- Draft/published controls and manual request review

## Important limitations

**Local prototype only. Do not expose this Python development server to the public internet.** It requires production authentication, persistent secure sessions, TLS, backups, monitoring, rate limiting, spam controls, server hardening, and legal/privacy review. It does not send emails, delete accounts automatically, or connect to the App Store. Do not enter real customer information until a production-grade data-handling system is deployed. Publishing an application requires accurate legal documents, not placeholder text.

GitHub stores source code; it does not host this Python + SQLite administration backend. Deploying this complete system requires a separate production server and secure, persistent storage. GitHub Pages can serve static sites only.

## Copyright

© 2026 AADi Infinity Labs — proposed brand. Use the legal owner's correct name where required.
