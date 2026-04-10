from qdrant_client import QdrantClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os

load_dotenv()
api_key=os.getenv('API_KEY')
if not api_key:
    raise ValueError("Chưa tìm thấy API_KEY trong file .env!")

# config Gemini
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel('models/gemini-1.5-flash')


COLLECTION_NAME = "veggie_products"
QDRANT_HOST = "localhost" #

def run_search(query_text):
    print(f"\n--- Đang tìm kiếm: '{query_text}' ---")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client: QdrantClient = QdrantClient(host=QDRANT_HOST, port=6333)

    query_vector = model.encode(query_text).tolist()

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector, 
        limit=3
    )
    results = response.points

    if not results:
        print("Không tìm thấy sản phẩm nào phù hợp.")
    else:
        # CHỖ NÀY: Khởi tạo context_data NGOÀI vòng lặp
        context_data = "" 
        
        for i, hit in enumerate(results):
            payload = hit.payload
            if payload is not None:
                content = payload.get('content', 'Không có tên')
                metadata = payload.get('metadata', {})
                price = metadata.get('price', 0)
                
                # Cộng dồn dữ liệu của cả 3 sản phẩm vào context
                context_data += f"- {content} - Giá: {price} VNĐ. \n"
                print(f"Đã tìm thấy: {content}") # In ra để debug
            print("-" * 20)
        
        # Sửa lại prompt và gọi model
        prompt = f"""
            Bạn là một nhân viên tư vấn bán hàng thân thiện của cửa hàng rau củ Veggie.
            Dựa vào thông tin sản phẩm dưới đây, hãy trả lời câu hỏi của khách hàng một cách tự nhiên.
            Nếu không có sản phẩm phù hợp, hãy lịch sự báo cho khách biết.

            Thông tin sản phẩm đang có:
            {context_data}

            Câu hỏi của khách: {query_text}
            Trả lời:
            """
        
        try:
            model_instance = genai.GenerativeModel('gemini-1.5-flash')
            response = model_instance.generate_content(prompt)
            print("\n[Chatbot Veggie]:", response.text)
        except Exception as e:
            print(f"\nLỗi gọi Gemini: {e}")

if __name__ == "__main__":
    user_query = input("Nhập câu hỏi tìm sản phẩm: ")
    run_search(user_query)