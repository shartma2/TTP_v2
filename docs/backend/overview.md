# Backend Overview

The backend of the Text-to-PASS Generator is implemented as a **FastAPI** application and provides the core functionality of the system. It is responsible for processing user requests, executing modules, and managing asynchronous jobs.

---

## Purpose

The backend acts as the central processing unit of the application. Its main responsibilities include:

- Accepting and handling API requests
- Managing asynchronous job execution
- Coordinating module execution
- Interacting with external services (e.g., LLM APIs)
- Returning structured results to the frontend

---

## Architectural Overview

The backend follows a modular and layered architecture:
- api/
- app/
- modules/
- logs/


### Key Layers

- **API Layer (`/api`)**  
  Defines REST endpoints and handles incoming HTTP requests

- **Application Layer (`/app`)**  
  Contains core services such as:
  - Job management
  - Module registry
  - Shared utilities (logging, exceptions)

- **Module Layer (`/modules`)**  
  Implements the domain-specific logic of the system. Each module encapsulates a specific task (e.g., generation, validation, refinement).

- **Logging (`/logs`)**  
  Stores runtime logs and generated artifacts

