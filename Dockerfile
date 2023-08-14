FROM python:3.10-slim

WORKDIR /app

# SSH stuff from https://learn.microsoft.com/en-us/azure/app-service/tutorial-custom-container?tabs=azure-cli&pivots=container-linux
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        dialog \
        ffmpeg \
        git \
        openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && echo "$SSH_PASSWD" | chpasswd

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
RUN pip install -r requirements.txt --no-cache-dir \
    && rm requirements.txt

# Copy app files
COPY *.py .
COPY .streamlit .streamlit

# Set PYTHONHASHSEED to 0 so string hashes are consistent between runs
ENV PYTHONHASHSEED=0

# Expose Streamlit port
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# SSH stuff from https://learn.microsoft.com/en-us/azure/app-service/tutorial-custom-container?tabs=azure-cli&pivots=container-linux
COPY sshd_config /etc/ssh/
COPY init.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/init.sh
EXPOSE 2222

ENTRYPOINT ["init.sh"]
