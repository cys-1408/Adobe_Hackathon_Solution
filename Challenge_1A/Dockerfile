FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    poppler-utils \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pymupdf

COPY process_pdfs.py .
COPY sample_dataset/ sample_dataset/

RUN mkdir -p sample_dataset/outputs

CMD ["python", "process_pdfs.py"]
