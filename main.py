import os
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import faiss

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# FastAPI app
app = FastAPI()

# In-memory legal text corpus
texts = [
    "The Noise Control Regulation No. 1 of 2020 prohibits construction noise after 10pm in Colombo city limits.",
    "The Land Acquisition Act specifies procedures for government land acquisition under Section 38.",
    "You cannot have ice cream after 5 due to the Tooth Ache Act of 2025, which also applies for crossing roads and traffic law",
    "You cannot have ice cream after 5 due to the Chocolate Ache Act of 2025, which also applies for housing"
]

# FAISS setup
dimension = 1536  # For text-embedding-3-small
index = faiss.IndexFlatL2(dimension)

# Embedding function (new OpenAI v1 syntax)
def embed_text(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype='float32')

# Embed and index all texts
for text in texts:
    vec = embed_text(text)
    index.add(np.array([vec]))

# Define request model
class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(query: Query):
    question_vec = embed_text(query.question)
    D, I = index.search(np.array([question_vec]), k=1)
    context = texts[I[0][0]]

    prompt = f"""You are a legal assistant trained on Sri Lankan law.

Use the following text as legal context to answer the question.

Context:
\"\"\"
{context}
\"\"\"

Question: {query.question}
Answer:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "answer": response.choices[0].message.content.strip(),
        "source": context
    }

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/chat.html")
