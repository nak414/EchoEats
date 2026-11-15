# Manual demonstration and report test cases

Start `python run_echoeats.py`. Open `http://127.0.0.1:8765`.

| Case | Steps | Expected result |
|---|---|---|
| T01 | Sign in with vendor demo account | Vendor dashboard and orders navigation appear |
| T02 | Add a food listing with name, quantity 5, original/start/min price, pickup/expiry dates | Listing saved and visible to consumers |
| T03 | Edit listing quantity and picture | Updated information appears |
| T04 | Change pricing curve (Linear/Exponential/Stepped) | Saved in listing; price respects minimum |
| T05 | Sign in as consumer and search the new food | Correct listing appears, filter/sort work |
| T06 | Reserve two out of five available portions | Stock becomes three, pending order shows 15-minute countdown |
| T07 | Open the checkout and confirm demo payment | Order status becomes confirmed and pickup code appears |
| T08 | Sign in as vendor and open Orders | Confirmed order appears and can be marked collected |
| T09 | Reserve more food than remains | Server rejects reservation; quantity does not turn negative |
| T10 | Start an unpaid hold then let 15 minutes pass | Status changes to expired; stock is released (if listing still available) |
| T11 | Start another pending hold and cancel | Status changes to cancelled; stock restored |
| T12 | After demo payment, cancel eligible confirmed order | Status changes to cancelled and demo refund is recorded; no real money moved |
| T13 | Add a preparation task, set High priority, mark complete, refresh, uncheck and delete | Task status persists until deleted |
| T14 | Save a consumer category filter then refresh | Selected filter persists |
| T15 | On an unfinished Add Food form, refresh browser and reopen | Browser remembers the draft |
| T16 | Change phone/name on Profile | Updated profile persists |
| T17 | Try consumer account adding food | Rejected; vendor permissions required |
| T18 | Browse at phone-size screen | Main navigation and forms remain usable |

Run `python tests/full_workflow.py` to verify 12 HTTP checks automatically. The tests use a temporary DB and exercise actual API endpoints. Node UI smoke checks are `node tests/ui-server-smoke.mjs`. Collect **real screenshots** from the browser for each required rubric area.

**Not tested/claimed:** actual credit-card charges, PCI audit, public cloud uptime, 5-km map radius, cloud email delivery, 5,000 concurrent users.
