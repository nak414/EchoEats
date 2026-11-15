# EchoEats Phase 2 Core Implementation

## Project overview

EchoEats is a food waste marketplace that allows vendors to sell surplus food at discounted prices and consumers to browse, reserve, and collect available food. This application implements the core features designed in Phase 1

## Implemented Features

- Consumer and vendor registration and login
- Food listing creation, editing, and management
- Dynamic pricing and inventory management
- Food search, filtering, and details
- 15-minute food reservations
- Simulated checkout and pickup confirmation
- Preparation task creation, deletion, completion, and prioritization
- Local storage for saved tasks and preferences

## How to Run the Application

**Requirement:** Python 3.10 or later.

1. Download or clone the repository.
2. Open the `application` folder.
3. On Mac, run `start_mac.command`. On Windows, run `start_windows.bat`.
4. Keep the Terminal window open.
5. Visit http://127.0.0.1:8765 in your browser.

## Demo Accounts

| Account | Email | Password |
|---|---|---|
| Consumer | consumer@echoeats.test | Demo12345! |
| Vendor | vendor@echoeats.test | Demo12345! |

## Testing

To run the automated backend tests:

`python3 tests/full_workflow.py`

**Note:** Payments are simulated - The application is a Phase 2 prototype rather than a publicly deployed  platform
