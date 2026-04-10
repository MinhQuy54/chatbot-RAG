import json

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

COLLECTION_NAME = "veggie_products"
JSONL_FILE = "app/data/products_for_rag.jsonl"
QDRANT_HOST = "qdrant_vector_db"

model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host=QDRANT_HOST, port=6333)


def ingest_data():
    if not client.collection_exists(COLLECTION_NAME):
        print(f"Đang tạo collection mới: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    points = []
    print(f"Bắt đầu xử lý Embedding từ file: {JSONL_FILE}...")

    with open(JSONL_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            vector = model.encode(data["content"]).tolist()

            points.append(
                PointStruct(
                    id=i, 
                    vector=vector,
                    payload={
                        "doc_id": data["doc_id"],
                        "content": data["content"],
                        "metadata": data["metadata"],
                    },
                )
            )
    
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Đã nạp thành công {len(points)} sản phẩm vào Qdrant!")
    else:
        print("Không có dữ liệu để nạp. Quý kiểm tra file JSONL nhé!")

if __name__ == "__main__":
    ingest_data()
