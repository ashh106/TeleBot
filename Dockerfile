# # Use an official slim Python image as the base
# FROM python:3.11-slim

# # Install system dependencies and the Rust toolchain
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
#     && rm -rf /var/lib/apt/lists/*

# # Add Cargo (Rust's package manager) to PATH
# ENV PATH="/root/.cargo/bin:${PATH}"

# # Set the working directory inside the container
# WORKDIR /app

# # Copy your entire project into the container's /app directory
# COPY . /app

# # Upgrade pip and install all Python dependencies from requirements.txt
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

# # Command to run your Telegram bot (adjust run.py if needed)
# CMD ["python", "run.py", "Ustatus.py"]


# Dockerfile

# 1) Base image
FROM python:3.11-slim

# 2) Install system deps for SQLite and runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libsqlite3-0 \
 && rm -rf /var/lib/apt/lists/*

# 3) Set working dir
WORKDIR /app

# 4) Copy minimal requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 5) Copy your bot code
COPY . .

# 6) Expose the port your Flask webhook listens on
ENV PORT=8080
EXPOSE 8080

# 7) Run both Flask (for webhooks/healthcheck) and your polling bot
#    Adjust if you’re using only polling or only webhook approach.
CMD ["sh", "-c", "\
      flask run --host=0.0.0.0 --port=$PORT & \
      python run.py \
    "]
