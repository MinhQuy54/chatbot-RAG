FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app 

# Sửa lỗi chính tả: requirements.txt
COPY requirements.txt .

# Nâng cấp pip và cài đặt thư viện
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào thư mục /app/app
COPY ./app ./app

EXPOSE 8080

# Chạy server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]