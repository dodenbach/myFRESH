import os
from typing import List
import streamlit as st
import pdfplumber
import openai
import pinecone

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')  # e.g. 'us-west1-gcp'
PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'pdf-search')

openai.api_key = OPENAI_API_KEY

# Initialize Pinecone
if PINECONE_API_KEY and PINECONE_ENV:
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    if PINECONE_INDEX not in pinecone.list_indexes():
        pinecone.create_index(PINECONE_INDEX, dimension=3072, metric='cosine')
    index = pinecone.Index(PINECONE_INDEX)
else:
    index = None


def extract_text_from_pdf(file) -> str:
    """Extract all text from a PDF file-like object."""
    text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or '')
    return '\n'.join(text)


def chunk_text(text: str, max_words: int = 250) -> List[str]:
    """Split text into chunks of approximately ``max_words`` words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = ' '.join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks


def embed_text(texts: List[str]) -> List[List[float]]:
    """Create embeddings for a list of texts using OpenAI."""
    response = openai.Embedding.create(
        input=texts,
        model='text-embedding-3-large'
    )
    return [record['embedding'] for record in response['data']]


def upsert_chunks(chunks: List[str], namespace: str):
    """Embed chunks and upsert them into Pinecone."""
    if not index:
        st.error('Pinecone index not configured')
        return

    embeddings = embed_text(chunks)
    to_upsert = [
        (f'{namespace}-{i}', embedding, {'text': chunk})
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    index.upsert(vectors=to_upsert, namespace=namespace)


def query_pinecone(question: str, namespace: str):
    """Query Pinecone for similar chunks based on a question."""
    if not index:
        st.error('Pinecone index not configured')
        return []

    embedding = embed_text([question])[0]
    result = index.query(vector=embedding, top_k=3, include_metadata=True, namespace=namespace)
    return result.matches


# Streamlit App
st.title('PDF Semantic Search with Pinecone and OpenAI')

namespace = st.text_input('User namespace', value='default')

uploaded_file = st.file_uploader('Upload PDF', type=['pdf'])

if uploaded_file is not None:
    st.write('Processing file...')
    text = extract_text_from_pdf(uploaded_file)
    chunks = chunk_text(text)
    upsert_chunks(chunks, namespace)
    st.success(f'Uploaded and indexed {len(chunks)} chunks.')

question = st.text_input('Ask a question about your documents:')
if st.button('Search') and question:
    matches = query_pinecone(question, namespace)
    if matches:
        st.subheader('Top Matches')
        for match in matches:
            st.write(f"Score: {match.score:.4f}")
            st.write(match.metadata.get('text', ''))
            st.write('---')
    else:
        st.write('No matches found.')
