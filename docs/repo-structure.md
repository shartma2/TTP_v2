# Repository Structure

This section provides a brief overview of the project structure of the Text-to-PASS Generator.

---

## Overview

The repository is organized into four main directories:
- backend
- frontend
- config
- docs
- docker-compose.yaml
- mkdocs.yml
- README.md


---

## Backend

The `backend` directory contains the FastAPI application that implements the core logic of the system.

Key components include:

- **API Layer (`/api`)**  
  Defines REST endpoints (e.g., job creation and status retrieval)

- **Application Layer (`/app`)**  
  Contains core services such as the job service, module registry, and utility functions

- **Modules (`/modules`)**  
  Implements the main functionality:
  - CoT (Chain-of-Thought generation)
  - Pipeline (generation, validation, repair)
  - Refine (human-in-the-loop improvements)
  - Export (format conversion)
  - Rendering (diagram generation)

- **Logs (`/logs`)**  
  Stores generated artifacts and runtime logs

---

## Frontend

The `frontend` directory contains the Next.js application that provides the user interface.

Key parts:

- **App Router (`/app`)**  
  Main application structure including pages and layout

- **API Routes (`/app/api`)**  
  Proxy layer forwarding requests to the backend

- **Modules (`/app/modules`)**  
  UI components representing backend functionality (e.g., pipeline, refine, export)

- **Utilities (`/app/util`)**  
  Helper functions (e.g., job polling, rendering results)

---

## Config

The `config` directory contains environment configuration templates:

- `backend.env.example` – Backend configuration (e.g., API keys)
- `frontend.env.example` – Frontend configuration (e.g., backend URL)

These files must be copied and adapted before running the system.

---

## Docs

The `docs` directory contains the MkDocs documentation files.

The documentation structure is defined in `mkdocs.yml`.

---

## Infrastructure Files

- **`docker-compose.yaml`**  
  Defines and orchestrates the backend and frontend services

- **`mkdocs.yml`**  
  Configuration file for generating the documentation site

---

## Summary

The project follows a clear separation of concerns:

- **Backend** → processing logic and LLM integration  
- **Frontend** → user interface and interaction  
- **Config** → environment-specific settings  
- **Docs** → structured project documentation  

This modular structure supports extensibility, maintainability, and clear system boundaries.