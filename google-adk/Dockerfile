FROM python:3.11-slim

# ffmpeg is required by the YouTube shorts maker's video assembler
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Launch the ADK dev web UI. Mount/select a project folder
# (financial-advisor or youtube-shorts-maker) as the agents root.
EXPOSE 8000
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000"]
