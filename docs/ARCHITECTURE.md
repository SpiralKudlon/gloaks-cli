# System Architecture

## 🏛️ High-Level Design

Gloaks operates on a synchronous, modular execution pipeline. It is designed to be **fail-safe**, meaning the failure of one module (e.g., GeoIP lookup timeout) does not crash the entire scanning process.

```mermaid
graph TD
    A[User Input] --> B{DNS Resolver}
    B -- Valid IP --> C[Controller]
    B -- Invalid --> D[Exit Gracefully]
    C --> E[Module: Geo-IP]
    C --> F[Module: Header Analysis]
    C --> G[Module: TCP Scanner]
    E --> H[Console Output]
    F --> H
    G --> H