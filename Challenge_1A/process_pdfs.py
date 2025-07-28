import os
import json
import fitz
from pathlib import Path
import re
from collections import Counter

def extract_pdf_structure(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        all_blocks = []
        page_texts = {}
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            page_text = page.get_text()
            page_texts[page_num + 1] = page_text
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_size = 0
                        line_flags = 0
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                line_text += text + " "
                                line_size = max(line_size, span["size"])
                                line_flags |= span["flags"]
                        line_text = line_text.strip()
                        if line_text and len(line_text) > 1:
                            all_blocks.append({
                                "text": line_text,
                                "size": round(line_size, 1),
                                "flags": line_flags,
                                "page": page_num + 1,
                                "bbox": line.get("bbox", [0,0,0,0])
                            })
        doc.close()
        if not all_blocks:
            return {"title": "", "outline": []}
        title = extract_title_improved(all_blocks, page_texts)
        headings = extract_headings_improved(all_blocks, page_texts)
        return {
            "title": title,
            "outline": headings
        }
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {str(e)}")
        return {"title": "", "outline": []}
def extract_title_improved(all_blocks, page_texts):
    first_pages_blocks = [b for b in all_blocks if b["page"] <= 2]
    if not first_pages_blocks:
        return ""
    title_candidates = []
    sizes = [b["size"] for b in first_pages_blocks]
    max_size = max(sizes) if sizes else 0
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    for block in first_pages_blocks:
        text = clean_text(block["text"])
        if (len(text) >= 5 and 
            len(text) <= 100 and
            block["size"] >= avg_size + 2 and  # Larger than average
            not text.isdigit() and
            not re.match(r'^[^a-zA-Z]*$', text) and
            not text.lower().startswith(('page ', 'copyright', '©'))):
            title_candidates.append({
                "text": text,
                "size": block["size"],
                "page": block["page"],
                "score": calculate_title_score(text, block)
            })
    if title_candidates:
        title_candidates.sort(key=lambda x: x["score"], reverse=True)
        return title_candidates[0]["text"]
    page1_blocks = [b for b in all_blocks if b["page"] == 1]
    for block in page1_blocks:
        text = clean_text(block["text"])
        if (len(text) >= 10 and 
            len(text) <= 200 and
            not text.isdigit() and
            any(c.isalpha() for c in text)):
            return text
    return ""

def calculate_title_score(text, block):
    score = 0
    score += block["size"] * 2
    if 10 <= len(text) <= 80:
        score += 10
    elif 5 <= len(text) <= 100:
        score += 5
    if re.match(r'^[A-Z][a-zA-Z\s\-&]+$', text):
        score += 15
    if text.isupper() and len(text) > 5:
        score += 10
    if block["page"] == 1:
        score += 20
    elif block["page"] == 2:
        score += 10
    if any(pattern in text.lower() for pattern in ['copyright', 'page ', 'version', '©']):
        score -= 20
    return score
def extract_headings_improved(all_blocks, page_texts):
    headings = []
    seen_texts = set()
    sizes = [b["size"] for b in all_blocks]
    size_counter = Counter(sizes)
    body_size = size_counter.most_common(1)[0][0] if sizes else 12
    heading_patterns = [
        (r'^\d+\.\s+[A-Z].*', "H1"),
        (r'^\d+\.\d+\s+[A-Z].*', "H2"),
        (r'^\d+\.\d+\.\d+\s+[A-Z].*', "H3"),
        (r'^(?:Table of Contents|Acknowledgements|References|Revision History|Introduction)(?:\s|$)', "H1"),
        (r'^Chapter\s+\d+', "H1"),
        (r'^[A-Z][A-Z\s]{3,}$', "H1"),
    ]
    for block in all_blocks:
        text = block["text"].strip()
        size = block["size"]
        flags = block["flags"]
        page = block["page"]
        if len(text) < 3 or len(text) > 200:
            continue
        text_key = (text.lower().strip(), page)
        if text_key in seen_texts:
            continue
        is_heading = False
        level = "H3"
        for pattern, pattern_level in heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                is_heading = True
                level = pattern_level
                break
        if not is_heading and size > body_size + 1.5:
            is_heading = True
            if size > body_size + 4:
                level = "H1"
            elif size > body_size + 2.5:
                level = "H2"  
            else:
                level = "H3"
            if flags & 16:  # Bold
                if size > body_size + 2:
                    level = "H1"
                else:
                    level = "H2"
        if is_heading:
            if not any(c.isalpha() for c in text):
                continue
            skip_patterns = [
                r'^\d+$',
                r'^[^a-zA-Z]*$',
                r'.*\.\s*$',
                r'^©.*',
                r'^page\s+\d+',
            ]
            if any(re.match(pattern, text, re.IGNORECASE) for pattern in skip_patterns):
                continue
            clean_heading_text = clean_text(text)
            if clean_heading_text and len(clean_heading_text) >= 3:
                headings.append({
                    "level": level,
                    "text": clean_heading_text + " ",
                    "page": page
                })
                seen_texts.add(text_key)
    headings.sort(key=lambda x: (x["page"], x["text"]))
    return headings
def clean_text(text):
    text = re.sub(r'\s+', ' ', text.strip())
    return text
def process_pdfs():
    input_dir = Path("/sample_dataset/pdfs")
    output_dir = Path("/sample_dataset/outputs")
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process")
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}")
        result = extract_pdf_structure(str(pdf_file))
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"Saved {output_file.name}")
def process_pdfs_local():
    input_dir = Path("sample_dataset/pdfs")
    output_dir = Path("sample_dataset/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    print(f"Found {len(pdf_files)} PDF files to process")
    for pdf_file in pdf_files:
        print(f"\n=== Processing {pdf_file.name} ===")
        result = extract_pdf_structure(str(pdf_file))
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        print(f"Title: '{result['title']}'")
        print(f"Found {len(result['outline'])} headings:")
        for i, heading in enumerate(result['outline']):
            print(f"  {i+1:2d}. {heading['level']}: {heading['text'].strip()} (page {heading['page']})")
if __name__ == "__main__":
    print("Starting improved PDF processing...")
    process_pdfs_local()
    print("PDF processing completed!")