# AgriMithran

AgriMithran is an AI assistant for Tamil Nadu agriculture schemes. It retrieves
relevant passages from a local FAISS vector index, generates a structured answer,
and evaluates that answer. The application has a Streamlit user interface and a
FastAPI backend.

## Features

- Search for Tamil Nadu agriculture schemes, subsidies, eligibility, and
  application instructions.
- Choose Tamil or English for AI-generated answers; Tamil is the default.
- Retrieve passages from the local FAISS index and show their source information.
- View faithfulness, answer relevance, retrieval relevance, and overall
  evaluation scores.
- Switch between light and dark themes.
- Use a custom agriculture icon and locally stored farmland background.

## Project layout

| Path | Purpose |
| --- | --- |
| `app.py` | Streamlit interface, theme styling, and API client |
| `backend/api.py` | FastAPI app and `/health` and `/api/search` endpoints |
| `backend/config.py` | Project paths, index/source settings, and `.env` loading |
| `backend/guardrails.py` | Restricted-query keyword check |
| `backend/index_builder.py` | Downloads source pages and builds or refreshes the FAISS index |
| `backend/rag_service.py` | Loads the local index; retrieves, generates, and evaluates answers |
| `backend/schemas.py` | Validated API request and response models |
| `assets/agri_mithran_icon.svg` | Application icon |
| `assets/farmland_background.svg` | Locally stored page background illustration |
| `data/tamilnadu.pdf` | Local PDF source for index building |
| `faiss_tn_agri_index/` | Existing FAISS index files |

## Requirements and configuration

- Python with the project dependencies installed.
- An OpenAI API key for answer generation and AI evaluation.
- The local `faiss_tn_agri_index` (`index.faiss` and `index.pkl`).
- Internet access the first time the Hugging Face embedding model is downloaded,
  or when rebuilding the index from web sources.

Create a `.env` file in the project root:

```dotenv
OPENAI_API_KEY=your-openai-api-key
```

Do not commit `.env` or expose API keys publicly.

Install dependencies using the project virtual environment from PowerShell:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the application

Start the FastAPI backend in one terminal:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.api:app --reload
```

Start the Streamlit interface in a second terminal:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

Open the Streamlit URL printed in the terminal (usually
`http://localhost:8501`). The API runs at `http://127.0.0.1:8000`; its interactive
documentation is at `http://127.0.0.1:8000/docs`.

By default, Streamlit connects to `http://127.0.0.1:8000`. To use a different API
address, set `AGRI_API_URL`, for example:

```powershell
$env:AGRI_API_URL = "http://127.0.0.1:8000"
```

## Rebuild the local index

The API loads the existing index at startup and does not download sources or
rebuild it. To build or refresh the index, run this command from the project
root:

```powershell
.\venv\Scripts\python.exe -m backend.index_builder
```

Index building fetches the configured agriculture scheme web pages and
`data/tamilnadu.pdf`, splits their contents into chunks, embeds them, and saves
the result under `faiss_tn_agri_index/`. Rebuilding replaces the files in that
index directory.

## API

### `GET /health`

Returns the API process status:

```json
{"status": "ok"}
```

### `POST /api/search`

Example request:

```json
{
  "query": "What subsidy is available for certified seeds?",
  "language": "Tamil"
}
```

`query` must contain 1–1000 characters after trimming whitespace. `language`
accepts `Tamil` or `English` and defaults to `Tamil`. Restricted or off-topic
keywords are rejected with HTTP 400; invalid request data receives HTTP 422.

The response contains:

- `answer`: scheme name, funding pattern, eligibility, and how to apply.
- `evaluation`: metric scores, PASS/FAIL verdict, reason, and document counts.
- `sources`: retrieved passages and their source names/URLs.

## Evaluation metrics

- **Faithfulness** and **answer relevance** are AI-estimated on a 0–100 scale.
- **Retrieval relevance** is the percentage of retrieved documents marked
  relevant by the relevance grader.
- **Overall score** is the arithmetic mean of those three scores.
- The verdict is **PASS** when all three scores are at least 70; otherwise it is
  **FAIL**.

These are model-based quality estimates, not a substitute for checking scheme
details against the cited official sources.
