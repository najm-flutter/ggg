# استخدم صورة بايثون الرسمية كصورة أساسية
FROM python:3.11-slim

# تعيين دليل العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات إلى دليل العمل
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# نسخ كود التطبيق إلى دليل العمل
COPY . .

# تعيين المنفذ الذي سيستمع عليه التطبيق
EXPOSE 80

# الأمر الافتراضي لتشغيل التطبيق باستخدام Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
