FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies first to leverage Docker layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The news-reader-agent uses Playwright; install the Chromium browser and its
# system dependencies. (Harmless for the other two projects.)
RUN playwright install --with-deps chromium

COPY . .

# Default to the news reader; override at run time, e.g.:
#   docker run --env-file .env -w /app/job-hunter-agent <image> python main.py
WORKDIR /app/news-reader-agent
CMD ["python", "main.py"]
