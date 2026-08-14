
<p align="center">
  <img width="1335" height="784" alt="Thumbnail" src="https://github.com/user-attachments/assets/7fdf04f8-f8f7-4e47-9b76-a54d287e9319" />
</p>

<h1 align="center">📦 Supply Chain Intelligence System</h1>
<h3 align="center">An End-to-End Demand Forecasting, Inventory, Procurement & Agentic Analytics Platform</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688.svg" />
  <img src="https://img.shields.io/badge/Streamlit-Frontend-FF4B4B.svg" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-336791.svg" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED.svg" />
  <img src="https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg" />
  <img src="https://img.shields.io/badge/Deployed%20on-Azure-0078D4.svg" />
</p>

---

## 🧭 Overview

This project goes beyond a conventional machine-learning forecasting notebook — it is a full **Supply Chain Intelligence System** that connects **demand forecasting, inventory intelligence, supplier analysis, procurement planning, simulation, and agentic natural-language analytics** into a single, production-deployed platform.

Given historical sales and supply-chain data, the system answers real operational questions:

- What products are likely to be in demand?
- Which SKUs are at risk of stockout?
- When should procurement happen, and how much should be ordered?
- Do existing procurement orders already cover future requirements?
- Which suppliers should be used?
- How will today's decisions affect inventory in the future?

The system was designed, built, containerized, and deployed end-to-end — from raw data to a live cloud application with CI/CD.

---

## 📊 Dataset

| Attribute | Details |
|---|---|
| **Scope** | ~200 SKUs across 7 product categories |
| **Time Range** | Historical sales data from **2022 to 2024** |
| **Demand Pattern** | Highly **intermittent demand** (large proportion of zero-demand periods) |
| **Fields** | Product details, SKU, category, subcategory, price, availability, units sold, revenue, stock levels, reorder level, safety stock, suppliers, lead times, order quantities, procurement & delivery info |

---

## 🔮 Forecasting Approach

The forecasting strategy evolved through several iterations before settling on a model suited to intermittent demand:

1. **Per-SKU Prophet models** — explored first, but impractical to scale to ~200 SKUs.
2. **Nixtla MLForecast + LightGBM (global model)** — trained across all SKUs simultaneously using lag features, rolling/expanding statistics, exponentially weighted statistics, and calendar features.
3. **Nixtla StatsForecast + CrostonClassic** *(final approach)* — chosen specifically because it's built for intermittent demand, with `SeasonalNaive` used as a baseline.

Sales history was transformed into continuous weekly time series per SKU using the standard `unique_id | ds | y` format, with missing weeks treated as zero demand.

### ✅ Final Model Performance

| Metric | Value |
|---|---|
| **MAE** | 2.9634629 |
| **RMSE** | 3.327645 |
| **MASE** | 0.653956 |

Experiments and model artifacts were tracked using **MLflow**.

---

## 🏗️ System Workflow

```
Historical Data → Preprocessing → Intermittent-Demand Forecasting → Forecast Evaluation
   → Inventory Intelligence → Stockout-Risk Classification → Supplier Intelligence
   → Procurement Planning → Sales & Inventory Simulation → Agentic NL Analytics
```

### 1. Data Processing
Cleaning, missing-value handling, weekly aggregation, and continuous time-series construction per SKU.

### 2. Demand Forecasting
StatsForecast (CrostonClassic) as the primary model, SeasonalNaive as baseline, evaluated using MAE, RMSE, SMAPE, MASE, and WMAPE.

### 3. Inventory Intelligence
Combines forecasts with `Current_Stock`, `Reorder_Level`, and `Safety_Stock` to classify each SKU into an operational state:

| State | Meaning |
|---|---|
| 🔴 `CRITICAL` | Immediate stockout risk |
| 🟠 `REORDER_NOW` | Replenishment required now |
| 🟡 `AT_RISK` | May run short soon |
| 🟢 `SUFFICIENT` | Stock covers projected demand |

### 4. Supplier & Procurement Intelligence
Compares **existing procurement orders** (pending / in-transit / delivered) against **newly calculated requirements** before recommending new orders — avoiding duplicate procurement — and suggests suppliers based on lead time and performance.

### 5. Sales & Supply-Chain Simulation
Simulates future sales, inventory depletion, procurement, shipment movement, supplier lead times, replenishment, and stockout conditions to project future inventory outcomes.

### 6. Agentic Analytics Chatbot
A LangChain/LangGraph-orchestrated agent lets users ask natural-language questions about the supply chain database instead of writing SQL:

```
User Question → Intent Detection → Schema Retrieval → SQL Generation
   → SQL Execution (via PostgreSQL MCP) → Result Formatting → NL Response
```

An explicit schema definition (`backend/schemas/analytics_schema.json`) was introduced to prevent SQL/schema hallucination.

---

## 🧰 Tech Stack

| Layer | Technologies |
|---|---|
| **Forecasting / ML** | Nixtla StatsForecast, CrostonClassic, MLForecast, LightGBM, Scikit-learn, MLflow |
| **Data** | Pandas, NumPy |
| **Agentic AI** | LangChain, LangGraph, PostgreSQL MCP, langchain-mcp-adapters |
| **LLMs** | Ollama (Llama 3.2, Qwen, Gemma), Groq |
| **Backend** | FastAPI, SQLAlchemy / SQLModel, Pydantic |
| **Frontend** | Streamlit |
| **Database** | PostgreSQL (`master_data`, `processed_data`, `forecast_data`, `evaluation_data`) |
| **Visualization** | Plotly, Matplotlib |
| **Infra / DevOps** | Docker, Docker Compose, Docker Hub, GitHub Actions, Microsoft Azure (Ubuntu 24.04 LTS VM) |

---

## 🖥️ Application Modules

| Module | Description |
|---|---|
| **Analytics Agent** | Ask natural-language questions about supply-chain data |
| **Table Viewer** | Browse raw and processed tables |
| **Inventory & Supplier Reports** | Stock levels, reorder status, supplier performance |
| **Procurement Orders** | Track pending / in-transit / delivered orders |
| **Simulation** | Run future sales & inventory simulations |
| **ML Pipeline** | Trigger preprocessing, training, forecasting, and evaluation |

---

## 🐳 Deployment Architecture

The system is fully containerized and deployed on an **Azure Virtual Machine (Ubuntu 24.04 LTS)**:

| Service | Container | Port |
|---|---|---|
| Frontend (Streamlit) | `frontend` | `8501` |
| Backend (FastAPI) | `backend` | `8000` |
| MLflow | `mlflow` | `5000` |
| PostgreSQL | `postgres` | `5432` (internal only) |

- Frontend ↔ Backend communicate via Docker service names (not `127.0.0.1`).
- PostgreSQL is **not** exposed to the internet — accessible only within the Docker network.
- Persistent Docker volumes protect `postgres_data` and `mlflow_artifacts` across container recreation.

### CI/CD Pipeline (GitHub Actions)

On every push to `main`:

1. Checkout repository
2. Authenticate with Docker Hub
3. Build & push backend image
4. Build & push frontend image
5. SSH into Azure VM
6. Pull latest images
7. Recreate **only** backend & frontend containers
   *(PostgreSQL and MLflow containers are deliberately preserved to protect production data)*

Docker Hub acts as the image registry, GitHub Actions as the CI/CD automation layer, and Azure as the production runtime.

> **Note:** The Azure VM can be shut down after demos to avoid ongoing costs — the source code, Docker configuration, database backup, and CI/CD workflow remain available for redeployment at any time.

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/gyrfalcon55/supply-chain-intelligence-system.git
cd supply-chain-intelligence-system

# Configure environment variables (DB, API keys, etc.)
.env

# Build and start the full stack (ensure all env variables are kept in .env)
docker compose --env-file .env -f docker/docker-compose.yml up --build -d
```

| Service | URL |
|---|---|
| Streamlit Frontend | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| MLflow UI | http://localhost:5000 |

---

## 🧪 Testing

The project includes a **25-test pytest suite** covering both API and application-level functionality. The tests validate backend availability, table-view APIs, sales/supplier/inventory dashboards, report generation, procurement operations, simulation, ML pipeline endpoints, agent components, and ML/feature-engineering components.

The API tests use a configurable `API_URL`, with the default pointing to the local FastAPI server:

```bash
API_URL=http://127.0.0.1:8000
```

Run the full suite against the local FastAPI + PostgreSQL environment:

```bash
pytest -v
```

> **Note:** The test suite is intentionally **not** run against the Azure production database. Some tests — particularly procurement, simulation, and ML-pipeline tests — can modify database state or trigger processing. Running only locally keeps production data isolated while still providing a full regression and integration-testing layer during development.

**Summary:** 25 automated pytest tests covering APIs, agents, database-backed functionality, procurement, simulation, and ML components — executed against the local application environment to validate functionality without modifying production data.

<img src="https://img.shields.io/badge/Tests-25%20passing-brightgreen.svg" />
---

## 📌 Roadmap / Future Improvements

- [ ] Expand forecasting benchmarks across additional intermittent-demand models
- [ ] Add automated retraining triggers
- [ ] Extend the analytics agent with multi-turn conversational memory
- [ ] Add role-based access control for procurement approvals

---

## 🏛️ Project Architecture

<p align="center">
  <img width="1536" height="1024" alt="full workflow" src="https://github.com/user-attachments/assets/e4480af2-ea59-450d-bc45-6716660d832d" />
</p>

---

<p align="center">Built as an end-to-end Supply Chain Intelligence Platform — from raw data to production-style deployment.</p>

---
## Author

- shaik juanid
- portfolio - [sjunaid.in](https://sjunaid.in)
