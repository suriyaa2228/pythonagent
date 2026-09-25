# Python Playwright Rule-Based & AI-Powered Automation Platform

Welcome to the Playwright Automation Agent repository!

This project provides a complete hybrid test automation platform featuring:
- **FastAPI Backend & Web Dashboard** (`playwright-agent/backend` & `playwright-agent/frontend`)
- **Rule-Based State Machine & Orchestrator** for deterministic test execution
- **AI Multi-Agent System (RAG, Planner, Code Generator, Self-Healer, MCP)**
- **Playwright Page Object Model Framework** with 38+ Page Classes and 25+ Pytest suites (`playwright-agent/backend/python_playwright`)
- **Interactive HTML Extent Reporting** with automated failure screenshots

---

## Quick Navigation

For detailed architecture diagrams, multi-agent AI system documentation, API endpoints, and step-by-step setup instructions, please see the primary project documentation:

👉 **[playwright-agent/README.md](playwright-agent/README.md)**

---

## Quick Start Guide

### 1. Navigate to backend directory & install dependencies
```powershell
cd playwright-agent
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r backend/python_playwright/requirements.txt
playwright install
```

### 2. Start the FastAPI Server
```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 3. Open the Web Dashboard & API Docs
- **Web UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
