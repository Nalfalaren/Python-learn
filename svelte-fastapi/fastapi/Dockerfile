# 1. Use an official Python image
FROM python:3.12-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy dependency list and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the FastAPI source code
COPY . .

# 5. Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
