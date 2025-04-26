# Dockerfile (Simplified with requirements.txt)

# 1. ใช้ Python base image
FROM python:3.11-slim

# 2. ตั้งค่า Environment Variables พื้นฐาน
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. ตั้งค่า Working Directory
WORKDIR /code

# 4. ติดตั้ง System dependencies ที่จำเป็น
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy ไฟล์ requirements.txt
COPY requirements.txt /code/

# 6. ติดตั้ง Python dependencies ด้วย pip จาก requirements.txt
#    pip จะหาเวอร์ชันล่าสุดที่เข้ากันได้เอง
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copy source code ของแอปพลิเคชัน
COPY ./app /code/app

# 8. Expose Port
EXPOSE 8000

# 9. Command ที่จะรัน
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]