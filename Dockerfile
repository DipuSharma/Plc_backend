# Use official Python image
FROM python:3.10

# Set the working directory
WORKDIR /src

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Default command (for FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
