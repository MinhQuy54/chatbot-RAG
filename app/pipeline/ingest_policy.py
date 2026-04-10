import os, pdfplumber
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()


PDF_PATH = 'app/data/veggie_policy.pdf'
COLLECTION_NAME = "veggie_products"
model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host="localhost", port=6333)

def ingest_policy():
    print(f"--- Bắt đầu xử lý file: {PDF_PATH} ---")

    full_text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + '\n'

    # chunk_size=500 ký tự, overlap=50 để không mất ngữ cảnh giữa các đoạn
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    chunks = text_splitter.split_text(full_text)
    print(f"Đã chia thành {len(chunks)} doan nho.")

    points = []
    for i, chunk in enumerate(chunks):
        vector = model.encode(chunk).tolist()
        points.append(models.PointStruct(
            id= i + 1000,
            vector=vector,
            payload={
                "content": chunk,
                "metadata": {
                    "type": "policy",
                    "source": os.path.basename(PDF_PATH)
                }
            }
        ))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("--- Hoàn thành nạp dữ liệu Policy vào Qdrant! ---")

if __name__ == "__main__":
    ingest_policy()

