# PDF Structure Extractor

This project processes PDF documents to extract the **document title** and **structured outline/headings** using font sizes, styles, and content-based heuristics. The results are saved as structured JSON files.

## Features

- Detects the most probable **document title**.
- Extracts hierarchical **headings (H1, H2, H3)** from the document content.
- Supports multiple PDFs in batch.
- Automatically saves results as `.json` in a specified output folder.

## Installation

   1. **Clone this repository or download the files.**

   2. **Install dependencies:**

         pip install -r requirements.txt

         Requires Python 3.8 to 3.11


## How It Works

    Uses PyMuPDF (fitz) to extract text and font information.

    Determines the title based on font size, position, and content scoring.

    Classifies headings based on:

    Font size hierarchy

    Text patterns (e.g., 1. Introduction, Chapter 2, etc.)

    Font weight (bold)

Ensure your PDFs are text-based (not scanned images).
