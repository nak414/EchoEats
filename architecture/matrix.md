# EchoEats — Architectural Trade-off Analysis

**Architectures Compared:** Layered Modular Monolith vs. Microservices

**Evaluation Method:** Weighted decision matrix based on Chapter 10. Each architecture is scored from 1 (weak) to 5 (strong), with weights totaling 1.00.

## 1. Weighted Decision Matrix

| Quality Criterion | Weight | Layered Modular Monolith | Microservices |
|---|---:|---:|---:|
| Scalability | 0.25 | 3 | 5 |
| Security | 0.25 | 4 | 3 |
| Maintainability | 0.20 | 4 | 3 |
| Team Fit | 0.30 | 5 | 2 |
| **Weighted Result** | **1.00** | **4.05/5** | **3.20/5** |

### Weighted Calculations

**Layered Modular Monolith:**

(0.25 × 3) + (0.25 × 4) + (0.20 × 4) + (0.30 × 5) = **4.05/5**

**Microservices:**

(0.25 × 5) + (0.25 × 3) + (0.20 × 3) + (0.30 × 2) = **3.20/5**

## 2. Justification of Scores

| Criterion | Layered Modular Monolith | Microservices |
|---|---|---|
| **Scalability** | **3/5:** Supports increasing demand by adding resources, but all backend modules scale together. | **5/5:** Individual services, such as food search and dynamic pricing, can scale independently. |
| **Security** | **4/5:** Centralized authentication and role-based access simplify security management within one backend. | **3/5:** Services can restrict access independently, but additional network communication requires more security controls. |
| **Maintainability** | **4/5:** Separate modules make features easier to organize and maintain, although updates generally require redeploying the backend. | **3/5:** Services can be updated independently, but integration, monitoring, and testing require additional coordination. |
| **Team Fit** | **5/5:** Managing one backend is more practical for a six-member student team with limited time and resources. | **2/5:** Multiple deployments and service communication increase development complexity. |

## 3. Architectural Trade-offs for EchoEats

**Layered Modular Monolith:** Provides simpler deployment and coordination between closely connected features, particularly reservations, inventory, and checkout. For instance, shared database transactions can help prevent double bookings and maintain accurate stock levels.

**Microservices:** Offers greater flexibility for independent scaling and deployment. However, coordinating inventory updates, 15-minute reservation holds, and payment results across separate services requires additional communication and consistency mechanisms.

## 4. Final Architectural Decision

**Recommended Architecture: Layered Modular Monolith (4.05/5)**

The Layered Modular Monolith achieved the highest weighted score, making it more suitable for EchoEats' current development stage. Team Fit received the highest weight (30%), followed by Scalability and Security (25% each), and Maintainability (20%).

Although Microservices offers better independent scalability, the Layered Modular Monolith provides a more practical balance between system requirements, development simplicity, security management, and team resources.

*Note: The scores represent an architectural assessment based on EchoEats' requirements and development constraints, rather than measured system performance.*
