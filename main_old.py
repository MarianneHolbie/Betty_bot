from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import BertTokenizer
import tensorflow_hub as hub
import tensorflow as tf
from sentence_transformers import SentenceTransformer, SimilarityFunction
import os
import numpy as np

app = FastAPI()

# Load models
semantic_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
qa_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
qa_model = hub.load("https://tfhub.dev/see--/bert-uncased-tf2-qa/1")

class Question(BaseModel):
    question: str

class ThreadRequest(BaseModel):
    customer: str

class MessageRequest(BaseModel):
    thread_id: str
    message: str

# Mock thread and run IDs management
threads = {}

def load_corpus(corpus_path):
    corpus = []
    for filename in os.listdir(corpus_path):
        if filename.endswith(".md"):
            file_path = os.path.join(corpus_path, filename)
            with open(file_path, 'r', encoding='utf-8') as md_file:
                corpus.append(md_file.read() + '\n')
    return corpus

def semantic_search(corpus, sentence):
    semantic_model.similarity_fn_name = SimilarityFunction.COSINE
    embeddings_sen = semantic_model.encode(sentence)
    similarities = [semantic_model.similarity(embeddings_sen, semantic_model.encode(doc)) for doc in corpus]
    best_similarity_idx = np.argmax(similarities)
    return corpus[best_similarity_idx]

def q_a(question, reference):
    q_tokenized = qa_tokenizer.tokenize(question)
    ref_tokenized = qa_tokenizer.tokenize(reference)
    tokens = ['[CLS]'] + q_tokenized + ['[SEP]'] + ref_tokenized + ['[SEP]']
    input_word_ids = qa_tokenizer.convert_tokens_to_ids(tokens)
    input_mask = [1] * len(input_word_ids)
    input_type_ids = ([0] * (1 + len(q_tokenized) + 1) + [1] * (len(ref_tokenized) + 1))
    input_word_ids, input_mask, input_type_ids = map(lambda t: tf.expand_dims(tf.convert_to_tensor(t, dtype=tf.int32), 0), (input_word_ids, input_mask, input_type_ids))
    outputs = qa_model([input_word_ids, input_mask, input_type_ids])
    short_start = tf.argmax(outputs[0][0][1:]) + 1
    short_end = tf.argmax(outputs[1][0][1:]) + 1
    answer_tokens = tokens[short_start: short_end + 1]
    if not answer_tokens:
        return None
    answer = qa_tokenizer.convert_tokens_to_string(answer_tokens)
    return answer

@app.post("/answer")
async def answer_question(question: Question):
    corpus_path = ".\ZendeskArticles"
    corpus = load_corpus(corpus_path)
    reference = semantic_search(corpus, question.question)
    if reference:
        answer = q_a(question.question, reference)
        if answer:
            return {"answer": answer}
    raise HTTPException(status_code=404, detail="Answer not found")

@app.post("/start_thread")
async def start_thread(request: ThreadRequest):
    # Mock thread and run creation
    thread_id = "thread_" + request.customer
    run_id = "run_" + request.customer

    threads[thread_id] = []
    
    return {"thread_id": thread_id, "run_id": run_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
