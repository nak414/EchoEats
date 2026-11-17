# EchoEats — Architectural Trade-off Analysis

**Alternatives:** Layered Modular Monolith vs. Microservices

**Method:** Weighted decision matrix based on Chapter 10. Scores range from 1 (weak) to 5 (strong), and weights total 1.00.

## 1. Weighted Decision Matrix

| Quality Criterion | Weight | Layered Modular Monolith | Microservices |
|---|---:|---:|---:|
| Scalability | 0.25 | 3 | 5 |
| Security | 0.25 | 4 | 3 |
| Maintainability | 0.20 | 4 | 3 |
| Team Fit | 0.30 | 5 | 2 |
| **Weighted Result** | **1.00** | **4.05/5** | **3.20/5** |

**Weighted Calculations**

Modular Monolith: (0.25 × 3) + (0.25 × 4) + (0.20 × 4) + (0.30 × 5) = **4.05**

Microservices: (0.25 × 5) + (0.25 × 3) + (0.20 × 3) + (0.30 × 2) = **3.20**

## 2. Justification of Scores

| Criterion | Layered Modular Monolith | Microservices |
|---|---|---|
| **Scalability** | **3/5:** Can support more users by adding resources, but backend modules scale together. | **5/5:** Individual services, such as food search and dynamic pricing, can scale independently. |
| **Security** | **4/5:** Centralized authentication and role-based access simplify security management. | **3/5:** Separate services can restrict access, but additional network connections require more security controls. |
| **Maintainability** | **4/5:** Separate modules simplify development and updates, although the backend is generally redeployed together. | **3/5:** Services support independent updates, but integration, monitoring, and testing are more complex. |
| **Team Fit** | **5/5:** One backend is more manageable for a six-member student team with limited time. | **2/5:** Separate deployments and service coordination increase development effort. |

## 3. Architectural Trade-offs for EchoEats

**Layered Modular Monolith:** Supports simpler deployment and coordination between reservations, inventory, and payments. For instance, shared database transactions can help prevent double bookings when consumers reserve the same food item.

**Microservices:** Provides greater flexibility for independent scaling and deployment. However, coordinating reservation holds, inventory updates, and payment results across services would require additional communication and consistency mechanisms.

## 4. Final Architectural Decision

**Recommended Architecture: Layered Modular Monolith (4.05/5)**

The Layered Modular Monolith is more suitable for EchoEats' current development stage because it separates the main system functions while keeping implementation and deployment manageable. Team Fit receives the highest weight (30%), followed by Scalability and Security (25% each), and Maintainability (20%).

Although Microservices offers better independent scalability, the Layered Modular Monolith provides a more practical balance of development simplicity, security management, and coordination between closely connected features.

*The scores represent design-based evaluations, not measured system performance.*
