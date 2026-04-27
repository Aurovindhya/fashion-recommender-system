# Fashion Recommender System

A chatbot-powered fashion recommendation engine built with Dialogflow and deployed as a Google Cloud Function. Users describe what they are looking for through a conversational interface, and the system returns ranked product recommendations from a Myntra dataset using a custom similarity-based retrieval pipeline.

## How It Works

The user interacts with a Dialogflow chatbot and provides three inputs: the type of product they want, a preferred color, and a budget. Dialogflow extracts these as structured parameters and sends a webhook request to the Cloud Function. The function then:

1. Encodes the query using TF-IDF vectors across product category, gender, and color
2. Runs a FAISS nearest-neighbor search across the full dataset
3. Filters results by price and re-ranks by rating
4. Returns the top 5 recommendations as a formatted Telegram-compatible response

## Architecture

```
User (Telegram / Dialogflow console)
        |
   Dialogflow NLU
        |
  Webhook (Cloud Function)
        |
   FAISS vector search over Myntra dataset
        |
  Top 5 ranked recommendations
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Cloud Function webhook that handles Dialogflow requests and runs the recommendation pipeline |
| `test.py` | Data preprocessing script to extract color information from product descriptions |
| `algo-test.py` | Benchmarking script that evaluates the similarity-based recommender against a baseline |
| `myntra-data.parquet` | Preprocessed Myntra product dataset |
| `requirements.txt` | Python dependencies |

## Tech Stack

- **Language** - Python
- **NLU** - Dialogflow ES
- **Deployment** - Google Cloud Functions (via `functions-framework`)
- **Vector search** - FAISS (IndexFlatL2)
- **Text encoding** - scikit-learn TF-IDF (category, gender, color)
- **Data** - pandas, fastparquet
- **Chatbot delivery** - Telegram inline keyboard responses

## Setup

### Prerequisites

- Python 3.9+
- A Dialogflow ES agent with intents for `Type`, `color`, `price`, and `gender` parameters
- Google Cloud project with Cloud Functions enabled

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run locally

```bash
functions-framework --target get_recommendations
```

### Deploy to Google Cloud

```bash
gcloud functions deploy get_recommendations \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated
```

Point your Dialogflow webhook URL to the deployed function endpoint.

## Recommender Performance

The similarity-based FAISS retrieval pipeline was benchmarked against a baseline approach in `algo-test.py`. A bar chart of the performance comparison is included in the accompanying project report.

Copyright (c) 2026 Aurovindhya
