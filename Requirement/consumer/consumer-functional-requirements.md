EchoEats – Consumer Functional Requirements
Author: Jude Abudayeh (F2400350)
Sprint: 1 – Requirements Analysis and Initial Design
Traces to: consumer-user-stories.md
---
2.1 Registration and Account Management (US-C01)
ID	Requirement
FR-C01	The system shall allow a consumer to register using full name, email address, phone number and password, and to select the "Consumer" account type.
FR-C02	The system shall validate that the email address is unique and that the password has at least 8 characters, including at least one letter and one number.
FR-C03	The system shall send a verification link to the consumer's email and shall not allow login until the email is verified.
FR-C04	The system shall authenticate consumers using their email and password and direct them to the Consumer Home screen after successful login.
FR-C05	The system shall lock a consumer account for 15 minutes after 5 consecutive failed login attempts.
FR-C06	The system shall allow a consumer to reset their password through a time-limited link sent to their registered email.
FR-C07	The system shall allow a consumer to view and edit their profile details and log out.
2.2 Food Discovery – Location and Map (US-C02)
ID	Requirement
FR-C08	The system shall request the consumer's permission to access device location before using it.
FR-C09	The system shall display active food listings within a default radius of 5 km of the consumer's location, sorted from nearest to farthest.
FR-C10	The system shall provide a map view showing the location of vendors with active listings, and shall show a listing summary when a vendor pin is selected.
FR-C11	The system shall allow the consumer to enter an address or area manually when location access is not granted.
FR-C12	The system shall display only listings that are active, not expired and have an available quantity greater than zero.
2.3 Search and Filtering (US-C03)
ID	Requirement
FR-C13	The system shall allow consumers to search listings by keyword matching food name, vendor name or category.
FR-C14	The system shall allow consumers to filter listings by distance, price range, food category, dietary tags and pickup time.
FR-C15	The system shall allow consumers to sort results by distance, current price, discount percentage or expiry time.
FR-C16	The system shall allow multiple filters to be combined and shall provide a single option to clear all filters.
FR-C17	The system shall display a "No results found" message when no listings match the search or filters.
2.4 Food Details and Dynamic Prices (US-C04)
ID	Requirement
FR-C18	The system shall display, for each listing, the food name, photo, description, dietary tags, vendor name and address, available quantity and pickup/expiry time.
FR-C19	The system shall display the original price, the current dynamic price and the discount percentage for each listing.
FR-C20	The system shall display the latest price produced by the dynamic pricing engine and the time the price was last updated.
FR-C21	The system shall never display a current price lower than the vendor's minimum price.
2.5 Reservations (US-C05)
ID	Requirement
FR-C22	The system shall allow a consumer to reserve a quantity of an item that is no greater than the currently available quantity.
FR-C23	The system shall lock the reservation price when the temporary reservation is created, even if the dynamic price changes before payment is completed.
FR-C24	The system shall hold the reserved quantity for 10 minutes pending payment and display a countdown timer to the consumer.
FR-C25	The system shall automatically cancel unpaid reservations when the hold expires and return the quantity to the listing.
FR-C26	The system shall reduce the listing's available quantity immediately when a reservation is created, so the same unit cannot be reserved by two consumers.
FR-C27	The system shall allow a consumer to view their active, completed and cancelled reservations.
2.6 Payment and Pickup (US-C06)
ID	Requirement
FR-C28	The system shall display an order summary (item, quantity, locked price and total) before the consumer confirms payment.
FR-C29	The system shall process consumer payments through an integrated third-party payment gateway.
FR-C30	The system shall confirm a reservation only after the payment gateway reports a successful payment.
FR-C31	The system shall generate a unique pickup code for each paid order and show it with the vendor address, map location and pickup time window.
FR-C32	The system shall send the order confirmation and pickup details to the consumer by in-app notification and email.
FR-C33	The system shall display an error message and allow the consumer to retry when a payment fails, as long as the reservation hold is still active.
FR-C34	The system shall allow a consumer to cancel a paid order before the vendor's cancellation cutoff and shall issue a refund to the original payment method.
