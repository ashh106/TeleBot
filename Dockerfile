# Use slim Python base
FROM python:3.11-slim

WORKDIR /app

# Copy only code + requirements
COPY requirements.txt run.py Ustatus.py db_connect.py config.py ./

# Install just the minimal deps
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Expose (for Render health checks, optional)
ENV PORT=8080

# Run both the Flask server and your bot in parallel
CMD ["sh", "-c", "python Ustatus.py & python run.py"]
