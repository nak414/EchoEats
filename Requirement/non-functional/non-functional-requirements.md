# EchoEats Non-Functional Requirements

Author:Jude Abudayeh (F2400350)

Sprint: 1 Requirements Analysis and Initial Design

Applies to: the consumer app, the vendor app, the backend and the database

### 3.1 Security and Data Privacy

- NFR-01: The system shall encrypt all data transmitted between the apps and the server using HTTPS (TLS 1.2 or higher).
- NFR-02: The system shall store passwords only as salted hashes (e.g. bcrypt) and never in plain text.
- NFR-03: The system shall not store full card details; all card payments shall be handled by a PCI-DSS compliant payment provider.
- NFR-04: The system shall use role-based access control so that consumers can only access their own data and vendors can only manage their own listings and reservations.
- NFR-05: The system shall end a user session automatically after 30 minutes of inactivity.
- NFR-06: The system shall use a consumer's location only to show nearby food, only after the consumer gives permission, and shall not share it with vendors or third parties.
- NFR-07: The system shall allow users to request deletion of their account and personal data, which shall be completed within 30 days.

### 3.2 Performance

- NFR-08: The system shall load the Consumer Home screen with nearby listings within 3 seconds for 95% of requests on a standard 4G connection.
- NFR-09: The system shall return search and filter results within 2 seconds for 95% of requests.
- NFR-10: The system shall confirm or reject a reservation request within 2 seconds.
- NFR-11: The system shall show updated dynamic prices to consumers within 1 minute of the pricing engine's scheduled update (every 15–30 minutes).

### 3.3 Reliability and Availability

- NFR-12: The system shall be available at least 99.5% of the time each month, excluding scheduled maintenance.
- NFR-13: Scheduled maintenance shall be announced at least 24 hours in advance and performed outside peak hours (11:00–14:00 and 18:00–22:00).
- NFR-14: The system shall back up the database at least once every 24 hours and be able to restore service within 4 hours of a major failure.
- NFR-15: If the payment gateway is unavailable, the system shall inform the consumer and shall not create a paid order or charge the consumer.

### 3.4 Usability

- NFR-16: A new consumer shall be able to find food and complete a reservation within 5 minutes without any training.
- NFR-17: A consumer shall be able to reach the reservation step from the Home screen in no more than 3 taps.
- NFR-18: The system shall use a consistent layout, clear labels and readable font sizes (minimum 14 pt body text) across all screens.
- NFR-19: The system shall display clear error messages that explain what went wrong and how to fix it.

### 3.5 Scalability

- NFR-20: The system shall support at least 5,000 concurrent users without falling below the performance targets in Section 3.2.
- NFR-21: The system architecture shall allow servers to be added (horizontal scaling) to handle growth in users and vendors without redesign.
- NFR-22: The system shall support at least 1,000 vendors and 20,000 active listings at the same time.

### 3.6 Accurate Inventory and Reservation Data

- NFR-23: The system shall prevent double-booking: consumers shall not be able to reserve more than the remaining available quantity of a listing, even when several consumers reserve at the same moment.
- NFR-24: The system shall update available quantities across all consumer and vendor screens within 5 seconds of a reservation, cancellation or vendor edit.
- NFR-25: The system shall keep reservation and payment records consistent so that a reservation is only confirmed after successful payment and payment retries do not result in duplicate charges.
- NFR-26: The system shall automatically hide listings once their expiry/pickup cutoff time has passed.
- NFR-27: The system shall keep the price charged to the consumer equal to the locked reservation price, regardless of later price updates.
