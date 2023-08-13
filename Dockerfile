FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ffmpeg \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Go
RUN curl -LO https://go.dev/dl/go1.21.0.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz \
    && rm go1.21.0.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install wedl
RUN cd / \
    && git clone https://github.com/gnojus/wedl.git \
    && cd wedl \
    && make
ENV WEDL_PATH=/wedl/wedl

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt \
    && rm requirements.txt

# Copy app files
COPY *.py .
COPY .streamlit .streamlit

# Set PYTHONHASHSEED to 0 so string hashes are consistent between runs
ENV PYTHONHASHSEED=0

# Expose Streamlit port
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
