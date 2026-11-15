# Phase 2 — Five-person division (codebase already generated)

**Everyone starts with the same finished application.** The tasks below are for verification, modification and integration, rather than creating five disconnected apps. AI can assist with modifications to each person's files. All team members can contribute commits on separate branches.

| Person | Feature owner | Main files | Main test |
|---|---|---|---|
| 1 | Setup, database and authentication | `backend/main.py`, `run_echoeats.py`, `requirements.txt` | Fresh installation, signup/login and role restrictions |
| 2 | Vendor listings, photos and dynamic pricing | `src/app.js`, `src/pricing.js`, `backend/main.py` | Add/edit/deactivate listing, test price floor and image |
| 3 | Consumer discovery, search and food details | `src/app.js`, `assets/styles.css` | Search/filter food, opening food details, responsive design |
| 4 | Reservations, locked prices and stock consistency | `backend/main.py`, `src/apiStore.js` | Last-portion race, 15-minute expiry and cancellations |
| 5 (Jude) | Checkout, vendor orders, preparation tasks and Scrum Master | `src/app.js`, `src/apiStore.js`, `docs/` | Demo pay, pickup code, collection, task CRUD/completion/priority/localStorage |

**Integration approach:** Person 1 owns `backend/main.py` integration; persons 2, 3 and 5 coordinate `src/app.js` edits to avoid conflicting merges. Use separate branches and pull requests. Each member should record actual tests and screenshots of their own features. Jude coordinates Jira/Sprint records and the report.

**Demo sequence:** vendor signs in → creates food → consumer finds it → reserves quantities → completes simulated payment → receives pickup code → vendor confirms collection → vendor creates/completes/prioritizes/deletes a preparation task → browser refresh proves task persistence.
