
import logging,os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from google import genai

load_dotenv()
api_key=os.getenv('API_KEY')
if not api_key:
    raise ValueError("Chưa tìm thấy API_KEY trong file .env!")

# config Gemini
client = genai.Client(api_key=api_key)

embed_model = SentenceTransformer('all-MiniLM-L6-v2')
qdrant_client = QdrantClient(host='qdrant_vector_db', port=6333)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
def call_gemini(prompt):
    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-lite-latest"
    ]

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Lỗi với model {model_name}: {e}")

    return "Xin lỗi, hệ thống AI đang quá tải. Vui lòng thử lại sau."
class ChatRequest(BaseModel):
    message: str

app = FastAPI(
    title="Veggie Chatbot",
    description="Chatbot support seeking product",
    version="1.0.0"
    )


@app.post("/chat")
async def chat_with_veggie(request : ChatRequest):
    user_query = request.message
    logger.info(f"Đang xử lý câu hỏi: {user_query}")

    try:
        query_vector = embed_model.encode(user_query).tolist()
        chat_results = qdrant_client.query_points(
            collection_name='veggie_products',
            query=query_vector,
            limit=5
        ).points

        context_data = ""

        for hit in chat_results:
            p = hit.payload
            if p is not None:
                m = p.get("metadata", {})
                if m.get("type") == "policy":
                    context_data += f"[CHÍNH SÁCH]: {p.get('content')}\n"
                else:
                    context_data += f"[SẢN PHẨM]: {p.get('content')} - Giá: {m.get('price', 'Liên hệ')} VNĐ\n"
                    
        prompt = f"""
            Bạn là một nhân viên tư vấn bán hàng thân thiện của cửa hàng rau củ Veggie.
            Dựa vào thông tin sản phẩm dưới đây, hãy trả lời câu hỏi của khách hàng một cách tự nhiên.
            Nếu không có sản phẩm phù hợp, hãy lịch sự báo cho khách biết.

            Thông tin sản phẩm đang có:
            {context_data}

            Câu hỏi của khách: {user_query}
            Trả lời:
            """
    
        answer = call_gemini(prompt)
        return {
            "answer": answer,
            "debug_sources": [hit.payload.get('content') for hit in chat_results if hit.payload is not None]
        }    
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")
        raise HTTPException(status_code=500, detail="Bot đang bận, thử lại sau nhé Quý!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
