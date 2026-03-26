# Text-to-PASS Generator (TTP_v2)

This project is a bachelor thesis at the **University of Münster**, created by **Simon Hartmann (CC2026)**.

The goal of TTP_v2 is to transform natural-language process descriptions into structured PASS artifacts and provide an end-to-end workflow for generation, validation, refinement, and export.

## Container architecture

The system is designed as two Docker containers:

- **Backend container** (FastAPI): asynchronous job execution, module orchestration, validation/repair logic, and artifact logging.
- **Frontend container** (Next.js): user interface for creating jobs, monitoring status, viewing results, refining models, and downloading exports.

## Core capabilities

- **Chain-of-Thought generation** for text-based reasoning outputs.
- **Pipeline execution** with staged `generate -> validate -> repair` flow for PASS model processing.
- **Human-in-the-loop refinement** based on previously generated jobs.
- **Export module** for producing results in multiple formats (e.g., `.json`, `.txt`, `.owl`).
- **Asynchronous job handling** with status tracking (`queued`, `running`, `done`, `failed`).

## License

This project is released under the **MIT License**.

## Disclaimer

Large parts of this documentation were created with AI agent support. While reviewed, it may still contain mistakes or outdated details.

If you find an error, please open an issue or report it in the discussions panel.