# EchoEats — Working full-stack application

**EchoEats is a runnable responsive food-waste marketplace**, based on the team's Phase 1 EchoEats requirements. The entire frontend and backend source is included. No external accounts, API keys, proprietary tools, or frontend build process are required to demonstrate the core system.

This edition replaces the earlier browser-only demo with a **real multi-user Python/SQLite backend**. Food listings and reservations are stored in a database and shared between accounts using the same server. The database controls stock updates and reservation deadlines; localStorage is used separately for browser-specific preparation tasks, saved filters and drafts.

## Run the application

**Requires Python 3.10+**. In a terminal inside the extracted folder:

```bash
python -m pip install -r requirements.txt
python run_echoeats.py
```

On macOS, use `python3` instead of `python` when necessary. On Windows, `py` may work better than `python`.

Open **http://127.0.0.1:8765**. A new `echoeats.sqlite3` database is created automatically and loaded with sample food and accounts on first launch.

| Account | Email | Password |
|---|---|---|
| Consumer | `consumer@echoeats.test` | `Demo12345!` |
| Vendor | `vendor@echoeats.test` | `Demo12345!` |
| Second vendor | `cafe@echoeats.test` | `Demo12345!` |

Select **Log in / Sign up** and use the shortcut buttons to fill the sample consumer or vendor credentials. Create new accounts through Sign up. To demonstrate shared records, sign in as a vendor in one browser window and a consumer in another browser or private window.

**Quick demo:** Vendor logs in → adds a food listing → consumer searches for it → reserves portions (15-minute stock hold) → completes simulated checkout → receives pickup code → vendor sees confirmed order and marks it collected.

### Run tests

```bash
python tests/full_workflow.py
node tests/ui-server-smoke.mjs
```

The Python tests create a separate temporary SQLite database, start a local test server, and test multiple independent accounts. Node is optional and only needed for the UI rendering smoke test.

## Technology choice

- **Frontend:** standards-based HTML, CSS, and modern JavaScript modules. No React/npm build required for the app to run.
- **Backend:** FastAPI (Python) with REST endpoints. API documentation available at `/api/docs` while the server is running.
- **Persistent shared storage:** SQLite, with serialized `BEGIN IMMEDIATE` write transactions and foreign keys. Not tied to any cloud account.
- **Authentication:** per-account salted PBKDF2 password hashes, HTTP-only SameSite cookies and 30-minute idle session expiry. Lockout after five incorrect passwords for 15 minutes.
- **Food images:** validated JPG/PNG/WebP uploads stored in a local uploads folder.
- **Browser localStorage:** saved filters, unfinished vendor listing drafts, and task creation/deletion/priority/completion, satisfying the browser persistence requirement.

This setup is **simpler to run as a complete local student application** than separately configuring React, Supabase Auth, PostgreSQL and third-party services. If deployed for multiple users on the internet, the server and storage need a proper host, HTTPS, persistent disk, and a security review.

## Implemented features

**Accounts:** registration, login, logout, vendor/consumer role checking, profile changes, password changes, unique email, password validation, and failed-login lockouts.

**Vendors:** add/edit/deactivate food; upload food photos; set category/dietary labels/description, available quantity, original/start/minimum price, pickup deadline and expiration; automatic pricing with **linear, exponential or stepped** curves using time and demand; never discount below the minimum; dashboard and orders; pickup confirmation; simple sales total for confirmed/collected demo orders.

**Consumers:** browse available listings, food images, prices and discount percentages; keyword search, category/dietary/maximum-price filters and sorting; food detail page, pickup address, external map search link, quantity selection, reservation history and pickup code.

**Reservations:** server-validated quantity and availability, atomic stock decrement, locked price, 15-minute expiry independent of browser, automatic stock release on unpaid expiry, cancellation, one-time demo checkout, simulated refund on eligible cancellations, collected/confirmed/expired/cancelled statuses, and pickup confirmation by the appropriate vendor.

**Phase 2 task criteria:** a vendor preparation checklist with create, delete, completion toggle, High/Medium/Low priority and persistent browser localStorage. Consumer filters and food listing drafts also persist through refresh.

**UI:** responsive desktop and mobile layout with EchoEats green theme, account forms, food cards, filters, vendor dashboard, order list, task list, forms, and errors. It requires no frontend build tools.

## Limitations (do not represent as implemented)

The application is a **functional student implementation, not a finished commercial payment platform**. Real bank/card payments, card refunds, vendor payouts, emails, map-based geolocation/5-km radius filtering, guaranteed 99.5% uptime, 5,000-concurrent-user performance targets, distributed deployment and formal PCI compliance are **not implemented**. Demo payment/refund updates order status only; **no money changes hands**. Map links open an external search rather than an integrated live map. Expiry and prices are handled in the local server and database while the server runs.

The Phase 2 rubric appears to use generic task-app wording (creation/deletion, completion/prioritization). The preparation checklist maps directly to those actions, but **Dr. Sara should confirm that this interpretation is accepted for EchoEats**.

## Project layout

```text
EchoEats_Built_Application/
├── run_echoeats.py              Starts the real application
├── requirements.txt             Two Python dependencies
├── index.html                   Website entry page
├── assets/styles.css            Responsive EchoEats interface
├── src/
│   ├── app.js                   All web pages and interactions
│   ├── apiStore.js              Browser ↔ backend data adapter
│   ├── pricing.js               Frontend pricing/validation helpers
│   ├── store.js                 Data adapter loader
│   └── config.js                Configuration
├── backend/
│   └── main.py                  Accounts, database, APIs, pricing, holds
├── uploads/                    Food photos (created/filled as needed)
├── tests/
│   ├── full_workflow.py         12 end-to-end HTTP integration checks
│   └── ui-server-smoke.mjs      UI template and navigation smoke tests
└── docs/
    ├── FEATURE_REQUIREMENTS.md  Scope and rubric mapping
    ├── TEST_CASES.md            Manual test script and evidence checklist
    └── TEAM_TASKS.md            Five-person file ownership
```

The SQLite database and image uploads are *runtime data* and are intentionally not shipped as part of the ZIP. A clean database with sample records is created the first time the app runs.

## GitHub and demonstration

Place the extracted folder in the existing EchoEats GitHub repository on its own branch or in a clearly identified `application/` folder, review it, and merge it using the team's preferred process. Do not upload `echoeats.sqlite3`, runtime images containing personal information, or secrets. Add the files to your `.gitignore`.

On one computer, the app serves multiple browser clients. To run it from multiple computers or show it publicly, deploy the backend to a reachable service and configure a persistent database/HTTPS. A localhost URL is **not a public live website**.

The user manual, rubric mapping and test scenarios are in `docs/`.
