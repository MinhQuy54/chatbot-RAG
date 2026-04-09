from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "veggie_products"
QDRANT_HOST = "localhost" #

def run_search(query_text):
    print(f"\n--- Đang tìm kiếm: '{query_text}' ---")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client : QdrantClient= QdrantClient(host=QDRANT_HOST, port=6333)

    query_vector = model.encode(query_text).tolist()
    print(f"Danh sách hàm của client: {dir(client)}")

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector, 
        limit=3
    )
    results = response.points

    if not results:
        print("Không tìm thấy sản phẩm nào phù hợp.")
    else:
        for i, hit in enumerate(results):
            payload = hit.payload
            
            if payload is not None:
                content = payload.get('content', 'Không có tên')
                metadata = payload.get('metadata', {})
                price = metadata.get('price', 0)
                
                print(f"{i+1}. {content} (Score: {hit.score:.4f})")
                print(f"   Giá: {price} VNĐ")
            else:
                print(f"{i+1}. Point này không có dữ liệu payload.")
                
            print("-" * 20)

if __name__ == "__main__":
    user_query = input("Nhập câu hỏi tìm sản phẩm: ")
    run_search(user_query)