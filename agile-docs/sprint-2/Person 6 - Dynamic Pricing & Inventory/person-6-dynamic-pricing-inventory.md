 Dynamic Pricing, Inventory Design & Next-Phase Planning

Task 1 — Dynamic Pricing Design

1.1 Pricing Factors

EchoEats uses dynamic pricing to reduce food prices as the pickup deadline approaches.

The price depends on:

Initial Price: The vendor's original listing price.

Minimum Price: The lowest price allowed, protecting the vendor from excessive discounts.

Remaining Time: Prices decrease as the pickup deadline approaches.

Customer Demand: High demand slows discounts, while low demand accelerates them.

Pricing Method: The system supports linear, exponential, and stepped pricing.

1.2 Pricing Methods

Linear: Price decreases gradually at a consistent rate.

Exponential: Price decreases slowly at first, then more quickly.

Stepped: Price decreases at specific intervals or stages.

1.3 Demand Adjustment

The system adjusts discounts according to demand:

Demand Level

Condition

Factor

High

Demand ratio ≥ 0.50

0.65

Normal

Demand ratio between 0.15 and 0.50

0.90

Low

Demand ratio < 0.15

1.10

1.4 Pricing Formula

The proposed price is calculated using:

Proposed Price = Initial Price × [1 − min(0.85, Progress × 0.75 × Demand Factor)]

The final price is restricted by the minimum and initial prices and cannot increase above the previous current price.

1.5 Requirements and Implementation

The Phase 1 requirement specifies price updates every 15–30 minutes. The current backend recalculates prices through a maintenance process that runs approximately every 5 seconds.

The backend supports all three pricing methods, demand adjustments, and minimum-price protection. However, the update frequency should be aligned with the required 15–30-minute interval.

Task 2 — UML Activity Diagram for Dynamic Pricing

2.1 Process Explanation

The process starts by reading the listing's initial price, minimum price, remaining time, and customer demand. The system selects the pricing method (linear, exponential, or stepped) and calculates the time-based price reduction.

Next, the system adjusts the reduction according to demand. High demand uses a factor of 0.65, low demand uses 1.10, and normal demand uses 0.90. Finally, the system calculates the discounted price, applies the minimum and maximum price limits, and updates the current price if it has changed.

2.2 Numerical Example

Sample Value

Value

Initial Price

BD 4.000

Minimum Price

BD 2.000

Current Price

BD 4.000

Initial Quantity

10

Reserved Portions

1

Demand Ratio

10% (Low)

Time Progress

50%

Demand Factor

1.10

Pricing Method

Linear

Formula:

Proposed Price = Initial Price × [1 − min(0.85, Progress × 0.75 × Demand Factor)]

Final Price = max(Minimum Price, min(Initial Price, Current Price, Proposed Price))

Final calculated price: BD 2.350 per portion.

Task 3 — Inventory and Reservation Rules

3.1 Inventory and Reservation Process

EchoEats maintains accurate inventory by updating available quantities whenever a reservation is created, cancelled, or expires.

Listing Creation: Vendor adds the available quantity.

Quantity Request: Consumer requests a specific quantity.

Availability Check: System checks available stock.

Quantity Reservation: Requested quantity is deducted immediately.

Price Locking: Current price is saved with the reservation.

Reservation Hold: Reservation remains active for 15 minutes.

Simulated Checkout: Successful checkout confirms the order and generates a pickup code.

Reservation Expiry: Unpaid reservations expire after 15 minutes, and eligible stock is returned.

Concurrent Reservations: Database transactions prevent multiple consumers from reserving the same stock.

Unavailable Listings: Expired or deactivated listings cannot accept new reservations.

3.2 Inventory and Reservation Rules Table

Action

Required Check

Expected Result

Reserve food

Enough stock available

Create hold and reserve the quantity

Reserve more than available

Requested quantity exceeds stock

Reject without changing stock

Reservation expires

Hold remains unpaid

Expire hold and release eligible stock

Complete checkout

Reservation is still active

Confirm the order

Listing becomes unavailable

Listing expired or deactivated

Block new reservations

3.3 Preventing Overselling

EchoEats uses database transactions to prevent overselling and double-booking. The system checks available quantity, deducts stock, and creates the reservation within the same transaction.

The database uses BEGIN IMMEDIATE to prevent simultaneous write transactions from claiming the same stock. Expired reservations only return stock when the listing is still active and valid.

Task 4 — Next-Phase Development Plan

The following backlog identifies features that need improvement or further development in the next phase.

Future Task / Feature

Phase 1 Requirement ID

Priority

Estimated Effort

Acceptance Criteria

Dependencies / Risks

Payment gateway integration

FR-C29, FR-C30, FR-V30, FR-V31, NFR-03, NFR-15

High

Large

Payments and refunds work securely; failed payments do not confirm orders.

Payment provider integration and testing.

Align reservation and pricing timing

FR-C24, FR-V18, NFR-11

High

Medium

Reservation expiry and price updates follow consistent timing.

Resolve the 10-minute and 15-minute requirement differences.

Improve account security

FR-C03, FR-C06, NFR-01

Medium

Medium

Add email verification and password recovery; secure deployment with HTTPS.

Email service and security configuration.

Vendor earnings and payouts

FR-V32–FR-V35

Medium

Large

Vendors can view sales, earnings, and payout status.

Payment integration and fee rules.

Location-based search and maps

FR-C08–FR-C11

Medium

Large

Consumers can find nearby listings and view them on a map.

Location permissions and map service.

Performance and reliability

NFR-08–NFR-14, NFR-20–NFR-22

Medium

Large

Meet performance, backup, uptime, and scalability targets.

Testing and deployment infrastructure.

Complete search and listing details

FR-C13–FR-C21

Medium

Medium

Verify and complete required filters, sorting, and listing information.

Review existing frontend features and fill remaining gaps.

Email notifications

FR-C32

Low

Medium

Send order and reservation confirmation emails.

Email service and reservation status.

Prioritization

High-priority tasks focus on payment security and consistent reservation and pricing behavior. Medium-priority tasks improve security, vendor services, location features, and system reliability. Email notifications are lower priority because they are not essential to the main reservation process.

Estimated effort represents the expected development work. Completion will be measured against the acceptance criteria and tested before release.

Task 5 — Explanation of Technical Decisions

EchoEats uses dynamic pricing to encourage customers to purchase food before it expires. Minimum prices protect vendors from excessive discounts, while demand-based adjustments help manage price reductions.

Inventory is updated through database transactions to prevent overselling and double-booking. Reservation prices are locked when an order is created, protecting consumers from unexpected price changes.

The next development phase will focus on improving payment security, account features, vendor payouts, and system reliability while building on the existing Phase 1 implementation.
