from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def extract_pdf_structure(pdf_path):
    sections = []
    for page_layout in extract_pages(pdf_path):
        page_num = page_layout.pageid
        page_blocks = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text().strip()
                if not text:
                    continue
                font_sizes = [obj.size for line in element for obj in line if isinstance(obj, LTChar)]
                avg_font = round(sum(font_sizes) / len(font_sizes), 2) if font_sizes else 0
                page_blocks.append({
                    "text": text,
                    "font_size": avg_font,
                    "page_number": page_num
                })
        i = 0
        while i < len(page_blocks):
            block = page_blocks[i]
            is_heading = block["font_size"] >= 12 and block["text"].istitle()
            if is_heading:
                body = ""
                for j in range(1, 4):
                    if i + j < len(page_blocks):
                        body += " " + page_blocks[i + j]["text"]
                sections.append({
                    "text": block["text"],
                    "page_number": block["page_number"],
                    "body": body.strip()
                })
            i += 1
    return sections
