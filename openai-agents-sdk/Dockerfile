FROM python:3.11-slim

# uvx (from uv) is used to launch the local MCP stdio server in the ChatGPT clone.
# Graphviz is used by draw_graph() in the sdk-fundamentals examples.
RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default to the ChatGPT clone; override CMD to run a different project.
EXPOSE 8501
CMD ["streamlit", "run", "chatgpt-clone/app.py", "--server.address=0.0.0.0"]
