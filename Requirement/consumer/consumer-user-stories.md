EchoEats – Consumer User Stories
Author: Jude Abudayeh (F2400350)
Sprint: 1 – Requirements Analysis and Initial Design
Related files: consumer-functional-requirements.md, ../non-functional/non-functional-requirements.md
---
US-C01 – Registration and Login
User Story: As a consumer, I want to create an account and log in, so that I can use EchoEats and manage my reservations.
Acceptance Criteria:
The consumer can register with their name, email address, phone number and a password, and selects the "Consumer" account type.
The system rejects registration if the email is already in use, or if the password has fewer than 8 characters or does not include at least one letter and one number. A clear error message is shown.
The consumer receives a verification email and can log in only after verifying their email.
A registered consumer can log in with their email and password and is taken to the Consumer Home screen.
After 5 failed login attempts, the account is temporarily locked for 15 minutes.
The consumer can reset a forgotten password through a link sent to their email.
US-C02 – Find Nearby Discounted Food
User Story: As a consumer, I want to find discounted food from nearby vendors on a list or map, so that I can buy affordable meals close to me.
Acceptance Criteria:
When the consumer allows location access, the home screen shows available listings sorted by distance, nearest first.
The consumer can switch to a map view that shows pins for nearby vendors with active listings.
Each listing shows the food name, vendor name, distance, original price and current discounted price.
If location access is denied, the consumer can type an area or address manually instead.
Expired, sold-out or removed listings are not shown.
US-C03 – Search and Filter Food
User Story: As a consumer, I want to search and filter available food based on my preferences, so that I can easily find what I am looking for.
Acceptance Criteria:
The consumer can search by keyword (food name, vendor name or category).
The consumer can filter by distance, price range, food category (e.g. bakery, meals, desserts), dietary tags (e.g. vegetarian, vegan, gluten-free) and pickup time.
The consumer can sort results by distance, lowest price, biggest discount or soonest expiry.
Multiple filters can be applied together, and the consumer can clear all filters with one action.
If no listings match, the system shows a "No results found" message.
US-C04 – View Food Details and Current Dynamic Price
User Story: As a consumer, I want to view food details and the current updated price, so that I can compare deals before making a purchase.
Acceptance Criteria:
The Food Details screen shows the food name, photo, description, dietary tags, vendor name and address, available quantity, and pickup/expiry time.
The screen shows the original price, the current discounted price and the discount percentage.
The current price reflects the latest dynamic pricing update and shows when it was last updated.
If the price changes while the consumer is viewing the screen, the new price is displayed after the screen refreshes.
A "Reserve" button is shown only when the item is still available.
US-C05 – Reserve Food
User Story: As a consumer, I want to reserve available food, so that I can collect it before it expires or sells out.
Acceptance Criteria:
The consumer can select a quantity up to the available amount and tap "Reserve".
The reservation price is locked at the price shown when the consumer taps "Reserve", even if the dynamic price changes afterwards.
The reserved quantity is held for the consumer for 10 minutes while they complete payment, and a countdown timer is shown.
If payment is not completed within the hold time, the reservation is cancelled and the quantity is returned to the listing.
The consumer cannot reserve more than the available quantity, and two consumers cannot reserve the same last item.
The consumer can view their active and past reservations in "My Reservations".
US-C06 – Payment and Pickup Information
User Story: As a consumer, I want to pay for my reserved food and receive pickup details, so that I can complete my purchase and collect my order.
Acceptance Criteria:
The checkout screen shows the selected food, quantity, locked price and total amount before payment.
The consumer can pay through the integrated online payment option (e.g. debit/credit card).
After successful payment, the consumer receives an order confirmation with a unique pickup code, vendor address, map location and pickup time window.
The confirmation is shown in the app and sent by email/notification.
If payment fails, the consumer sees an error message and can retry while the reservation hold is still active.
The consumer can cancel a paid order before the vendor's cancellation cutoff and receive a refund.
