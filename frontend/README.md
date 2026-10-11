# Supply Chain Intelligence — React + Vite + Tailwind CSS

React/Vite frontend conversion of the supplied Streamlit UI. It includes Analytics Agent, View Tables, Inventory & Supplier Reports, Procurement Orders, Sales Simulation, and ML Pipeline pages.

## Requirements
- Node.js 18+ (Node 20+ recommended)
- The project's FastAPI backend running and exposing the existing endpoints

## Run locally
1. Extract the ZIP and open this folder in a terminal.
2. Install packages: `npm install`
3. Copy `.env.example` to `.env` and set `VITE_API_URL` to the FastAPI base URL if needed. The default is `http://127.0.0.1:8000`.
4. Start Vite: `npm run dev`
5. Open the URL printed by Vite (usually `http://localhost:5173`).

## Production build
- `npm run build` creates the static site in `dist/`.
- `npm run preview` previews that build locally.

## Backend endpoints used
`POST /chat`, `POST /table_view`, `GET /sales_orders`, `GET /suppliers`, `GET /inventory`, `POST /reports`, `POST /procurement_orders`, `POST /procurement_orders/final_list`, `POST /simulation/run_day`, `POST /ml_pipeline`, `GET /ml_pipeline/status/{job_id}`.

The frontend preserves these endpoint paths and payloads from the provided Python UI. If your backend uses a different host, configure `VITE_API_URL`. CORS must allow the Vite origin (`http://localhost:5173`) when calling the backend directly.

## Important notes
- Procurement `planning_date` is retained in `localStorage` when returned by the simulation endpoint so it can be used on the procurement page, similar to the original shared Streamlit session state.
- The original ML page polls job status until `Completed` or `Failed`; this conversion uses browser polling and can be stopped by navigating away.
- The original `requirements.txt` only contained Streamlit plotting dependencies; it is not needed by this React frontend.
