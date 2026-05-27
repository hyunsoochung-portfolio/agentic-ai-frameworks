FROM python:3.11-slim

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the projects.
COPY . .

# Default to the hand-coded agent loop. Override at run time to start a
# different project, e.g.:
#   docker run --rm -it --env-file .env <image> python crewai-setup/main.py
CMD ["python", "from-scratch-agent/main.py"]
