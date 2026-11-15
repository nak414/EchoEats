# Feature and requirements traceability

The working application targets the EchoEats team's core Phase 1 marketplace stories and the Phase 2 rubric. It does not claim that every Phase 1 production-scale NFR is satisfied.

| Phase 1 story | Delivered feature | Test method |
|---|---|---|
| US-C01 | Consumer signup/login, profile and reservation history | Register, log out/in, view profile |
| US-C02 | Available-food feed with vendor pickup addresses; external map lookup | Open Food Details and map link; true 5-km radius filtering deferred |
| US-C03 | Search, category/diet/price filters, sorting and no-result state | Search and combine filters; refresh |
| US-C04 | Food details, photos, prices, discount and quantity | Open item details |
| US-C05 | Quantity-based 15-minute reservation and price lock | Reserve, check timer, wait for expiration |
| US-C06 | Simulated checkout and pickup code | Confirm demo payment, check order |
| US-V01 | Vendor signup/login, profile/logout | Sign up as vendor and log in |
| US-V02 | Add food listing, required details, photo upload | Create listing, search as consumer |
| US-V03 | Edit/deactivate listings, available quantities, deadlines | Edit and deactivate; check consumer view |
| US-V04 | Starting and minimum prices | Add a listing with both prices |
| US-V05 | Time+demand price calculation with three curve options, minimum floor | Choose curve and observe changes |
| US-V06 | Vendor order statuses and pickup confirmation | Pay as consumer, mark as collected as vendor |

## Phase 2 rubric mapping

| Criterion | Evidence to demonstrate | Location |
|---|---|---|
| Creation and deletion — 3 | Add and delete vendor preparation tasks, also create/deactivate food listings | Vendor → Prep tasks; Vendor → My listings |
| Completion and prioritization — 3 | Check/uncheck completed tasks; change High/Medium/Low; tasks reorder | Vendor → Prep tasks |
| Basic user interface — 2 | Consumer cards/search/details; vendor forms/dashboard; mobile layout | All screens |
| Local storage — 2 | Create tasks, refresh/reopen; filters and listing drafts remain | Prep tasks; Explore; Add food |

**Rubric uncertainty:** Because the exact wording mentions *task creation, task completion and prioritization*, this plan provides a literal vendor preparation checklist. Dr. Sara must confirm this matches the intended EchoEats assessment interpretation.

## Design decisions

- One app shared by consumer and vendor roles.
- One database shared by logged-in users; no client-only inventory.
- Reservations are one table with pending/confirmed/expired/cancelled/collected states.
- Payment is clearly labeled a simulation, with no card collection.
- Accounts are authenticated by the local backend. Dynamic pricing and stock changes occur server-side.
- Browser localStorage is used for personal preferences, draft listings, and preparation tasks only.
- Rely on actual tested behavior and screenshots in the report; do not claim production performance, PCI certification, real refunds or integrated mapping.
