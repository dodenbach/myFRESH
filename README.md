# Semantic PDF Search with Streamlit

This repository includes a simple Streamlit application that lets you upload PDF files, index them with embeddings from OpenAI, store them in Pinecone, and perform semantic search.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set the following environment variables with your API keys:

- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENV` – Pinecone environment (e.g. `us-west1-gcp`)
- `PINECONE_INDEX` – name of the index to use (defaults to `pdf-search`)

3. Run the Streamlit app:

```bash
streamlit run app.py
```

The app allows you to upload PDFs, which are then chunked into roughly 200–300 word blocks and indexed in Pinecone under the namespace you provide. You can then ask questions, and the app will return the top three most relevant text chunks along with similarity scores.
