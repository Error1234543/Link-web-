FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .
ENV EXPIRE_SECONDS=20
CMD ["python", "bot.py"]
