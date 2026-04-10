import os
import json
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = 'app/data'
os.makedirs(DATA_DIR, exist_ok=True)

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("Không tìm thấy DATABASE_URL")

engine = create_engine(DB_URL)

def extract_data_to_json(output_file):
    logger.info("--- Bắt đầu trích xuất dữ liệu (bao gồm Stock) ---")
    try:
        with engine.connect() as connection:
            # Lấy thêm cột p.stock
            query = text("""
                SELECT p.id, p.name, p.description, p.price, p.stock, c.name as category_name 
                FROM app_product p
                JOIN app_category c ON p.category_id = c.id
            """)
            result = connection.execute(query).mappings() 
            
            count = 0
            with open(output_file, "w", encoding='utf-8') as f:
                for row in result:
                   
                    stock_status = "Còn hàng" if row['stock'] > 0 else "Hết hàng"
                    
                    context_text = (
                        f"Sản phẩm: {row['name']}\n"
                        f"Loại: {row['category_name']}\n"
                        f"Giá: {float(row['price'])} VNĐ\n"
                        f"Tình trạng: {stock_status} (Số lượng: {row['stock']})\n"
                        f"Mô tả: {row['description'] if row['description'] else 'Không có mô tả'}"
                    )

                    doc = {
                        "doc_id": f"prod_{row['id']}",
                        "content": context_text,
                        "metadata": {
                            "category": row['category_name'],
                            "price": float(row['price']),
                            "stock": int(row['stock']),
                            "type": "product_info"
                        }
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                    count += 1
            logger.info(f"Đã trích xuất {count} sản phẩm thành công!")

    except Exception as e:
        logger.error(f"Lỗi khi extract data: {e}")

if __name__ == '__main__':
    output_path = os.path.join(DATA_DIR, 'products_for_rag.jsonl')
    extract_data_to_json(output_path)