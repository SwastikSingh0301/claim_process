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

## API Contract

This section documents the public API endpoints exposed by the service. It lists the path, method, expected request body, response shape, common error responses, and notes about rate-limiting and behaviour.

### POST /claims

- Purpose: Ingest a single claim that contains one or more service lines. The API validates, persists, computes net fees, and updates provider aggregates.
- Path: `/claims`
- Method: `POST`
- Request body: JSON matching the `ClaimCreateRequest` model

Request shape:

```json
{
	"claim_reference": "optional-string",
	"lines": [
		{
			"service_date": "2023-10-01T00:00:00Z",
			"submitted_procedure": "D0120",
			"quadrant": "UR",                  
			"plan_group": "GROUP123",
			"subscriber_id": "SUB123",
			"provider_npi": "1234567890",
			"provider_fees": "100.00",
			"allowed_fees": "80.00",
			"member_coinsurance": "10.00",
			"member_copay": "5.00"
		}
	]
}
```

- Success response (200): `ClaimCreateResponse`

Example success response:

```json
{
	"claim_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
	"message": "Claim processed successfully"
}
```

- Common errors:
	- `400 Bad Request` — validation errors or malformed request body (returns a message explaining the validation error).
	- `500 Internal Server Error` — unexpected failure during processing.

### GET /providers/top

- Purpose: Return the top 10 provider NPIs ranked by total net fees.
- Path: `/providers/top`
- Method: `GET`
- Rate limiting: This endpoint is rate-limited. The limit is configured in application settings (`settings.rate_limit_per_minute`) and enforced via the app's rate limiter.
- Behaviour: Uses a pre-aggregated table `provider_net_fee_aggregate` for fast reads. Returns up to 10 providers sorted by total net fee cents descending.

Response shape: an array of `TopProviderResponse` objects

```json
[
	{
		"provider_npi": "1234567890",
		"total_net_fee_cents": 123456
	},
	{
		"provider_npi": "0987654321",
		"total_net_fee_cents": 98765
	}
]
```

Common errors:
- `429 Too Many Requests` — when the rate limit is exceeded for the client.
- `500 Internal Server Error` — unexpected server/database failures.


