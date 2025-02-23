FROM python:3.10

WORKDIR /src

RUN pip install --upgrade pip setuptools wheel

# Copy dependency list
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app files
COPY . .

# Ensure the .env file is copied (optional but explicit)
COPY .env .env

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application with Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
