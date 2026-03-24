# ============================================================
# Dockerfile - Package EvalX into a container
# ============================================================
#
# Think of this like a RECIPE for building a shipping box:
#   1. Start with a base (Python)
#   2. Copy our code into the box
#   3. Install libraries
#   4. Tell Docker how to START the app
#
# To use:
#   docker build -t evalx .
#   docker run -p 8000:8000 --env-file .env evalx

# Step 1: Start with Python (the base)
FROM python:3.12-slim

# Step 2: Set working directory inside container
WORKDIR /app

# Step 3: Copy requirements first (Docker caches this step)
COPY requirements.txt .

# Step 4: Install libraries
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy all code
COPY . .

# Step 6: Tell Docker our app uses port 8000
EXPOSE 8000

# Step 7: Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
