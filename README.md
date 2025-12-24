# Claim Processing Service (`claim_process`)

A backend service built with **FastAPI** to process insurance/dental claims, compute net fees, and expose high-performance analytics on provider earnings.

---

## Overview

`claim_process` ingests a single claim containing multiple service lines, validates and persists the data, computes net fees, and maintains an optimized aggregation to retrieve the **top 10 providers by net fees**.

The service is **dockerized**, uses **PostgreSQL + SQLModel**, and is designed with correctness, performance, and scalability in mind.

---

## Setup & Running the Project

### Prerequisites
- Docker
- Docker Compose

### Start the application

Build and start the API and database using Docker Compose:

docker-compose up --build

Once running:
- API base URL: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

Running Tests

To run tests locally (outside Docker):

pytest -v

If running tests inside the Docker container:

docker-compose exec api pytest -v

---

## Features

- Ingest claims with multiple service lines
- Generate a unique ID per claim
- Validate input data with flexible, extensible rules
- Compute net fees per service line
- Persist normalized claim data to a relational database
- Maintain a pre-aggregated provider net fee table for fast analytics
- Expose a rate-limited API to retrieve top 10 providers by net fees
- Designed to safely integrate with a downstream payments service

---

## Tech Stack

- **FastAPI** – API framework
- **SQLModel** – ORM
- **PostgreSQL** – Relational database
- **Docker & Docker Compose** – Containerization
- **SlowAPI** – Rate limiting
- **Pytest** – Test framework

---