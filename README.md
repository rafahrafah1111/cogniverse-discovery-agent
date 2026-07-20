# 🤖 CogniVerse AI Discovery Agent

An interactive, AI-driven discovery consultant designed to conduct discovery interviews with business stakeholders, capture domain workflows, extract structured operational insights, and automatically identify AI & automation opportunities.

---

## 🌟 Key Features

- **Interactive Discovery Dialogue**: Natural, conversational multi-turn interviews guided by state tracking.
- **Dynamic Topic & State Management**: Tracks progress across 5 main discovery stages (`About You`, `Department Performance & KPIs`, `Key Workflows & Pain Points`, `Systems & Data Landscape`, `Governance & Adoption`).
- **Structured JSON Extraction**: Automated entity extraction using LLMs (`llama3.2` via Ollama) paired with custom fallback extractors for reliable, non-duplicate state persistence.
- **RESTful API**: Built with **FastAPI** providing `/start`, `/chat`, and `/export/{session_id}` endpoints.
- **Interactive UI**: Clean, responsive frontend built using **Streamlit**.

---

## 🏗️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic v2
- **Frontend**: Streamlit
- **LLM Engine**: Ollama (`llama3.2`)
- **Session & State Management**: Custom In-Memory State Tracker

---

## 🚀 Getting Started

### 1. Prerequisites

Make sure you have Python 3.10+ installed along with **Ollama** running locally:

```bash
ollama pull llama3.2
