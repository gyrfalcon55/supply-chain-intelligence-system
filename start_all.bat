@echo off
REM start_all.bat — launches Uvicorn, MLflow, and Streamlit in separate windows with venv activated

set "VENV=D:\Artificial Intelligence\SupplyChainManagementProject\project\Scripts\activate.bat"
set "BACKEND_DIR=D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\backend"
set "ROOT_DIR=D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai"
set "FRONTEND_DIR=D:\Artificial Intelligence\SupplyChainManagementProject\supply-chain-ai\frontend\app"

start "Uvicorn - Backend" cmd /k "cd /d "%BACKEND_DIR%" && call "%VENV%" && python run.py"

start "MLflow" cmd /k "cd /d "%ROOT_DIR%" && call "%VENV%" && mlflow ui --port 5000"

start "Streamlit - Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && call "%VENV%" && streamlit run streamlit_app.py --server.port 8501"

echo All services launched in separate windows.