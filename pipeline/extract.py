import os
import json
import logging
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = '/app/data'
os.makedirs(DATA_DIR, exist_ok=True)

DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("Không tìm thấy DATABASE_URL")

engine = create_engine(DB_URL)

def extract_data_to_json(output_file):
    logger.info("--- Bắt đầu trích xuất dữ liệu từ MySQL ---")
    try:
        with engine.connect() as connection:
            # Dùng .mappings() để truy cập row['column_name'] cho dễ
            query = text("SELECT id, name, description, price, category_id FROM app_product WHERE category_id = 1")
            result = connection.execute(query).mappings() 
            
            count = 0
            with open(output_file, "w", encoding='utf-8') as f:
                for row in result:
                    # Xử lý dữ liệu an toàn
                    name = row['name']
                    desc = row['description'] if row['description'] else "Không có mô tả"
                    price = float(row['price']) if row['price'] else 0.0
                    cat_id = row['category_id']

                    # Tạo nội dung để đem đi nhúng (Embedding)
                    context_text = f"Tên sản phẩm: {name}\nMô tả: {desc}"

                    doc = {
                        "doc_id": f"prod_{row['id']}",
                        "content": context_text,
                        "metadata": {
                            "category": cat_id,
                            "price": price,
                            "type": "product_info"
                        }
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                    count += 1

            logger.info(f"Thành công! Đã trích xuất {count} sản phẩm vào file: {output_file}")
            
    except Exception as e:
        logger.error(f"Lỗi khi extract data: {e}")

if __name__ == '__main__':
    output_path = os.path.join(DATA_DIR, 'products_for_rag.jsonl')
    extract_data_to_json(output_path)