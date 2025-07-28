## Challenge 1B - PDF Section Extractor and Ranker

This project processes collections of PDFs to extract and rank the most relevant sections based on a given persona and task. It uses NLP embeddings via `sentence-transformers` and PDF parsing via `pdfminer.six`.


## Setup Instructions

### Python Setup (Manual)

1. **Clone the repo**

   git clone <your_repo_url>

   cd Challenge_1B

2. **Create virtual environment (optional but recommended)**
    
    python -m venv venv 
    source venv/bin/activate

3. **Install dependencies**

    pip install -r requirements.txt

4. **Run the script**

    python analyze_collections.py

5. **Run with Docker**

   Build the image : docker build -t challenge1b-app .
   Run the container : docker run --rm -v ${PWD}:/app challenge1b-app


## Key Components
parser.py: Extracts headings and bodies from PDFs based on font size heuristics.

embedder.py: Generates sentence embeddings using intfloat/e5-small-v2.

ranker.py: Uses cosine similarity to rank the relevance of each section.