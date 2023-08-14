#!/bin/bash
set -e

echo "Starting SSH..."
service ssh start

echo "Running streamlit..."
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
