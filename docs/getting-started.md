# Getting Started

This section explains how to set up and run the Text-to-PASS Generator locally using Docker.

## Prerequisites

The only requirement to run the application is a working installation of **Docker Engine**.  
If you are using **Docker Desktop**, it already includes Docker Engine and is fully sufficient.

Please follow the official installation guide for your operating system:  
👉 [https://docs.docker.com/engine/install/](URL)

Make sure Docker is installed and running before proceeding.

---

## Environment Configuration

Before starting the application, the required environment variables must be configured.

Example configuration files are provided in the `/config` directory:

- `backend.env.example`
- `frontend.env.example`

Copy these files and rename them to:
config/backend.env
config/frontend.env


Then fill in the required values (e.g., API keys).

👉 See the **Configuration** section of the documentation for more details.

---

## Starting the Application

To start the application, navigate to the project root directory and run:

```bash
docker compose up --build
```

This command:

- Builds the Docker images (if necessary)
- Starts all defined services (backend and frontend)

### When to use `--build`

Use the `--build` flag when:

- Running the project for the first time
- Changes were made to source code or dependencies

Otherwise, you can start the containers without rebuilding:
```bash
docker compose up
```

### Running in detached mode

To run the containers in the background, use:
```bash
docker compose up -d
```

This is useful when you do not need to monitor logs in the terminal.

---

## Accessing the Application

Once the containers are running:

- The **frontend (web interface)** is available at:  
[http://localhost:3001](URL)

- The **backend API** runs internally on port `8000` and is accessed by the frontend via Docker networking.

### Running Containers

The following containers will be active:

- **backend**  
  FastAPI service responsible for job execution and module processing

- **frontend**  
  Next.js application providing the user interface

To verify running containers, use:

```bash
docker ps
```

---

This setup provides a fully containerized environment and requires no additional local dependencies.