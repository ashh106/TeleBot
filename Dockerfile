# Use an official slim Python image as the base
FROM python:3.11-slim

# Install system dependencies and the Rust toolchain
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

# Add Cargo (Rust's package manager) to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Set the working directory inside the container
WORKDIR /app

# Copy your entire project into the container's /app directory
COPY . /app

# Upgrade pip and install all Python dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Command to run your Telegram bot (adjust run.py if needed)
CMD ["python", "run.py", "Ustatus.py"]
