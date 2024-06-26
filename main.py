from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import os
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Chargement des modèles
try:
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    semantic_model = SentenceTransformer("distilbert-base-nli-mean-tokens")
except Exception as e:
    logging.error(f"Erreur lors du chargement des modèles: {e}")

class Question(BaseModel):
    question: str

class ThreadRequest(BaseModel):
    customer: str

class MessageRequest(BaseModel):
    thread_id: str
    message: str

# Gestion des threads (simulée)
threads = {}

def load_corpus(corpus_path):
    corpus = []
    for filename in os.listdir(corpus_path):
        if filename.endswith(".md"):
            with open(os.path.join(corpus_path, filename), 'r', encoding='utf-8') as file:
                corpus.append(file.read())
    return corpus

def semantic_search(corpus, query):
    try:
        query_embedding = semantic_model.encode([query])[0]
        corpus_embeddings = semantic_model.encode(corpus)
        similarities = np.dot(corpus_embeddings, query_embedding)
        best_match_index = np.argmax(similarities)
        return corpus[best_match_index]
    except Exception as e:
        logging.error(f"Erreur lors de la recherche sémantique: {e}")
        raise

@app.post("/answer")
async def answer_question(question: Question):
    try:
        corpus_path = "..\ZendeskArticles"
        corpus = load_corpus(corpus_path)
        context = semantic_search(corpus, question.question)
        
        result = qa_pipeline(question=question.question, context=context)
        
        if result['score'] > 0.1:  # Vous pouvez ajuster ce seuil
            return {"answer": result['answer']}
        else:
            raise HTTPException(status_code=404, detail="Réponse non trouvée ou score de confiance trop bas")
    except Exception as e:
        logging.error(f"Erreur dans /answer: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
    
@app.post("/start_thread")
async def start_thread(request: ThreadRequest):
    thread_id = f"thread_{request.customer}"
    threads[thread_id] = []
    return {"thread_id": thread_id}

@app.post("/send_message")
async def send_message(request: MessageRequest):
    if request.thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread non trouvé")
    
    threads[request.thread_id].append(request.message)
    
    # Ici, vous pouvez ajouter la logique pour traiter le message et générer une réponse
    # Par exemple, en utilisant le modèle QA sur l'historique du thread
    
    return {"response": "Message reçu et traité"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)