from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import sys

# ── 1. Load & chunk PDF ───────────────────────────────────────────────────────
print("Loading document...")
loader = PyPDFLoader("data/sample.pdf")
documents = loader.load()

if not documents:
    print("ERROR: No content found in PDF. Check the file path.")
    sys.exit(1)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"Split into {len(chunks)} chunks.")

# ── 2. Embeddings & vector store ──────────────────────────────────────────────
print("Building vector store...")
embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma.from_documents(chunks, embedding)
retriever = db.as_retriever(search_kwargs={"k": 5})

# ── 3. Load T5 directly — NO pipeline() ───────────────────────────────────────
print("Loading language model...")
model_path = "./models/flan-t5-small"   # ← changed from base to small
tokenizer = T5Tokenizer.from_pretrained(model_path, local_files_only=True)
model = T5ForConditionalGeneration.from_pretrained(model_path, local_files_only=True)
model.eval()
print("Model ready.\n")

# ── 4. Generate answer ────────────────────────────────────────────────────────
def generate_answer(prompt: str) -> str:
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=False
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

# ── 5. RAG query function ─────────────────────────────────────────────────────
def run_query(query: str) -> str:
    query = query.lower()

    if "refund" in query:
        query = query.replace("refund", "return")

    docs = retriever.invoke(query)

    if not docs:
        return "Escalating to human support..."

    context = "\n\n".join([doc.page_content for doc in docs])
    context = context[:1500]

    prompt = (
        "You are a strict customer support assistant.\n"
        "ONLY answer using the provided context.\n"
        "If the answer is NOT clearly present, say: I don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )

    response = generate_answer(prompt)


    if not response:
        return "Escalating to human support..."

    response_lower = response.lower()

    # If model hallucinates
    if "i don't know" in response_lower:
        return "Escalating to human support..."

    # If answer not in context → reject
    if not any(sentence.lower() in context.lower() for sentence in response.split(".")):
        return "Escalating to human support..."

    return response
# ── 6. Chat loop ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("RAG Customer Support Bot (Offline)")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue

        if query.lower() == "exit":
            print("Goodbye!")
            break

        answer = run_query(query)
        print(f"Bot: {answer}\n")