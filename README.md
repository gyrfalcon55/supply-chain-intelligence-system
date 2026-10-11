<p align="center">
  <img width="1456" height="720" alt="supplychain thumbnail" src="https://github.com/user-attachments/assets/630b4ad8-27f4-426c-b1c4-3e07b4f640fd" />
</p>

<h1 align="center">Supply Chain Intelligence System</h1>
<p align="center">
  <strong>An end-to-end platform for demand forecasting, inventory intelligence, procurement planning, simulation, and agentic analytics.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688.svg" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB.svg" alt="React" />
  <img src="https://img.shields.io/badge/Vite-Build%20Tool-646CFF.svg" alt="Vite" />
  <img src="https://img.shields.io/badge/Tailwind%20CSS-Styling-06B6D4.svg" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791.svg" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Containerization-2496ED.svg" alt="Docker" />
  <img src="https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF.svg" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/Azure-Deployment-0078D4.svg" alt="Microsoft Azure" />
</p>

---

## Overview

The Supply Chain Intelligence System is an applied AI and data platform designed to connect demand forecasting with operational supply-chain workflows. It brings together data preparation, intermittent-demand forecasting, inventory-risk classification, supplier analysis, procurement recommendations, sales simulation, and natural-language analytics.

The platform is designed to answer questions such as:

- Which products are likely to be needed in upcoming periods?
- Which SKUs are at risk of running out of stock?
- When should replenishment happen, and what quantities should be ordered?
- Do active procurement orders already cover expected requirements?
- Which suppliers are suitable for a replenishment order?
- How could simulated sales and deliveries affect future inventory?

The architecture keeps critical calculations—such as forecasting, inventory classification, and procurement quantities—in deterministic application logic. LLM-based agents support natural-language analytics and workflow orchestration rather than replacing business rules.

## Dataset

| Attribute | Details |
|---|---|
| Scope | Approximately 200 SKUs across 7 product categories |
| Historical period | 2022–2024 |
| Demand profile | Intermittent demand, including periods with zero sales |
| Data domains | Products, sales, inventory, suppliers, lead times, procurement, and delivery information |

## Key Features

### Demand forecasting

- Aggregates historical sales into continuous weekly time series per SKU.
- Uses **StatsForecast with CrostonClassic** as the primary intermittent-demand forecasting method.
- Uses **SeasonalNaive** as a baseline.
- Evaluates forecasts using MAE, RMSE, SMAPE, MASE, and WMAPE.
- Tracks experiments and artifacts with MLflow.

Reported model metrics:

| Metric | Value |
|---|---:|
| MAE | 2.9635 |
| RMSE | 3.3276 |
| MASE | 0.6540 |

These metrics reflect the reported evaluation for the project dataset; results may vary with data splits and pipeline changes.

### Inventory intelligence

Inventory rules combine forecasts with current stock, reorder levels, and safety stock to assign operational statuses.

| Status | Meaning |
|---|---|
| `CRITICAL` | Immediate stockout risk |
| `REORDER_NOW` | Replenishment is required |
| `AT_RISK` | Inventory may run short soon |
| `SUFFICIENT` | Current stock covers projected requirements |

### Supplier and procurement intelligence

- Reviews current procurement orders before recommending additional orders.
- Helps avoid duplicate orders when active orders already cover requirements.
- Consolidates replenishment needs and supports supplier assignment.
- Includes a human-in-the-loop workflow for reviewing, editing, submitting, and approving procurement recommendations.
- Preserves procurement transactions and order history.

### Sales and inventory simulation

The simulation interface is intended to model the effects of sales, inventory depletion, procurement progress, shipment arrivals, and replenishment over time. Actual simulation behavior depends on the backend implementation and its current state.

### Agentic analytics

The Analytics Agent allows users to ask natural-language questions about supply-chain data. Its workflow uses LangChain/LangGraph and PostgreSQL MCP integration to support schema-aware SQL generation, query execution, and result formatting.

An explicit analytics schema is maintained at `backend/schemas/analytics_schema.json` to reduce schema-related generation errors.

### LLM routing and guardrails

The backend architecture includes LiteLLM for model routing/fallback and NeMo Guardrails for input/output checks. SQL safety validation and PII masking are intended to provide additional controls around model-assisted analytics. These controls should be reviewed and tested against the actual deployment configuration before production use.

## Technology Stack

| Layer | Technologies |
|---|---|
| Forecasting and ML | Nixtla StatsForecast, CrostonClassic, MLForecast, LightGBM, scikit-learn, MLflow |
| Data processing | Python, Pandas, NumPy |
| Agentic AI | LangChain, LangGraph, PostgreSQL MCP, `langchain-mcp-adapters` |
| LLM integration | Groq, Gemini, LiteLLM |
| Guardrails | NeMo Guardrails |
| Backend API | FastAPI, Pydantic, SQLAlchemy / SQLModel |
| Frontend | React, Vite, Tailwind CSS, React Router |
| Visualization | Recharts, Plotly, Matplotlib |
| Database | PostgreSQL |
| Infrastructure | Docker, Docker Compose, Docker Hub, GitHub Actions, Microsoft Azure |

## Application Modules

| Module | Purpose |
|---|---|
| Analytics Agent | Ask natural-language questions about supply-chain data |
| View Tables | Browse supplier, inventory, and sales-order records |
| Inventory & Supplier Reports | Inspect stock levels, inventory status, and supplier metrics |
| Procurement Orders | Review and approve procurement recommendations |
| Sales Simulation | Run and inspect sales/inventory simulation actions exposed by the backend |
| ML Pipeline | Trigger pipeline jobs and inspect their status and metrics |

## Architecture

```text
Historical Sales & Supply-Chain Data
                |
                v
     Data Validation and Processing
                |
                v
  Weekly Demand Forecasting (CrostonClassic)
                |
                v
      Forecast Evaluation + MLflow
                |
                v
 Inventory Risk + Supplier Intelligence
                |
                v
 Procurement Recommendations and Approval
                |
                v
     Sales / Inventory Simulation

React + Vite Frontend <----> FastAPI Backend <----> PostgreSQL
                                  |
                                  +---- LangGraph Analytics Agent
                                  |          |
                                  |          +---- PostgreSQL MCP
                                  |
                                  +---- LiteLLM model routing
                                  |
                                  +---- NeMo Guardrails
```

## Frontend Setup (React + Vite)

### Requirements

- Node.js 18 or newer (Node.js 20+ recommended)
- npm
- A running FastAPI backend with the endpoints listed below

### Install and run

From the React frontend directory:

```bash
npm install
```

Copy `.env.example` to `.env` and configure the backend URL:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

### Production build

```bash
npm run build
npm run preview
```

The production-ready static assets are generated in `dist/`.

### Frontend environment variable

| Variable | Purpose | Default |
|---|---|---|
| `VITE_API_URL` | Base URL of the FastAPI backend | `http://127.0.0.1:8000` |

If the frontend and backend run on different origins, configure FastAPI CORS middleware to allow the frontend origin (for local development, usually `http://localhost:5173`).

## Backend API Integration

The React frontend currently calls these backend paths:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/chat` | Analytics Agent conversation |
| `POST` | `/table_view` | Retrieve table records |
| `GET` | `/sales_orders` | Sales-order data and available plot data |
| `GET` | `/suppliers` | Supplier data and available plot data |
| `GET` | `/inventory` | Inventory data and available plot data |
| `POST` | `/reports` | Inventory/supplier report data |
| `POST` | `/procurement_orders` | Generate or retrieve procurement recommendations |
| `POST` | `/procurement_orders/final_list` | Submit the reviewed procurement list |
| `POST` | `/simulation/run_day` | Run a simulation step |
| `POST` | `/ml_pipeline` | Start an ML pipeline job |
| `GET` | `/ml_pipeline/status/{job_id}` | Retrieve pipeline job status |

The frontend expects these routes and payloads to match the backend. If your backend uses different routes or response shapes, update `src/lib/api.js` and the relevant page components.

### Table-view performance

The View Tables page requests up to 100 records using the `limit` field. For large tables—especially sales data—the backend must enforce the limit in its database query (for example, using SQL `LIMIT`) rather than loading all records and truncating the response afterward. If pagination is implemented, use a validated `limit` and `offset` on the backend and request each page from the frontend as needed.

## Backend and Full-Stack Deployment

The backend project includes FastAPI, PostgreSQL, MLflow, model-routing configuration, and Docker-based deployment components. The exact commands and environment variables depend on the backend repository's `docker/` configuration.

For the full-stack Docker setup, the original project command is:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up --build -d
```

Before running it:

1. Create the required `.env` file using the environment-variable names expected by the Compose file.
2. Set database credentials and required LLM provider keys.
3. Confirm that the Docker Compose file and referenced Dockerfiles exist in the repository.
4. Keep PostgreSQL credentials and API keys out of source control.

The previously used deployment architecture included the React/Streamlit-era frontend service, FastAPI backend, MLflow, LiteLLM, and PostgreSQL. Update service names, ports, and Docker configuration to match the current React frontend before deploying the converted UI.

### Local service URLs

| Service | Typical local URL |
|---|---|
| React + Vite frontend | `http://localhost:5173` |
| FastAPI backend | `http://127.0.0.1:8000` |
| FastAPI OpenAPI docs | `http://127.0.0.1:8000/docs` |
| MLflow UI, if enabled | `http://localhost:5000` |

## Testing

The backend project has a reported 25-test `pytest` suite covering API and application functionality, including table views, reports, procurement operations, simulation, pipeline endpoints, agent components, and ML components.

Run tests from the backend repository/environment where its dependencies are installed:

```bash
pytest -v
```

For local API tests, the project has used an `API_URL` environment variable with a default of `http://127.0.0.1:8000`.

Tests that mutate procurement, simulation, or pipeline state should be run against a local development database—not a production database.

## Project Structure (Frontend)

```text
.
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env.example
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css
    ├── components/
    │   ├── Layout.jsx
    │   └── UI.jsx
    ├── lib/
    │   └── api.js
    └── pages/
        ├── ChatPage.jsx
        ├── TablesPage.jsx
        ├── ReportsPage.jsx
        ├── ProcurementPage.jsx
        ├── SimulationPage.jsx
        └── PipelinePage.jsx
```

## Roadmap

- [ ] Benchmark additional intermittent-demand forecasting methods
- [ ] Add automated retraining triggers
- [ ] Extend the analytics agent with multi-turn conversational memory
- [ ] Add role-based access control for procurement approvals
- [ ] Implement server-side pagination for all large table views
- [ ] Align Docker deployment and CI/CD with the React + Vite frontend

## Author

**Shaik Junaid**  
Portfolio: [sjunaid.in](https://sjunaid.in)

---

<p align="center">
  Built as an end-to-end supply-chain intelligence platform, connecting forecasting, operational workflows, and agentic analytics.
</p>
