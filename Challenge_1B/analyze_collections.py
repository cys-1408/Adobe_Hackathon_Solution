import json, os
from parser import extract_pdf_structure
from embedder import get_embedding, embed_all
from ranker import rank_sections
from datetime import datetime

def process_collection(folder):
    input_path = f"{folder}/challenge1b_input.json"
    with open(input_path) as f:
        input_data = json.load(f)
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]
    query_text = f"{persona}. Task: {job}"
    query_emb = get_embedding(query_text)
    all_texts, all_meta = [], []
    for doc in input_data["documents"]:
        pdf_path = os.path.join(folder, "PDFs", doc["filename"])
        doc_name = doc["filename"]
        sections = extract_pdf_structure(pdf_path)
        print(f"[DEBUG] {doc_name}: {len(sections)} section candidates extracted.")
        for s in sections:
            print(f"  - (p.{s['page_number']}) {s['text'][:60]}")
        for s in sections:
            if any(skip in s["text"].lower() for skip in ["table of contents", "references", "overview"]):
                continue
            combined_text = f"{s['text']}: {s['body']}"
            all_texts.append(combined_text)
            all_meta.append({**s, "document": doc_name})
    if not all_texts or not all_meta:
        print(f"No valid sections found in {folder}. Skipping.")
        return
    section_embs = embed_all(all_texts)
    top_sections = rank_sections(section_embs, all_meta, query_emb)
    output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in input_data["documents"]],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "section_title": s["section_title"],
                "importance_rank": s["importance_rank"],
                "page_number": s["page_number"]
            } for s in top_sections
        ],
        "subsection_analysis": [
            {
                "document": s["document"],
                "refined_text": f"{s['section_title']}: {s['body']}",
                "page_number": s["page_number"]
            }
            for s in top_sections
        ]
    }
    output_path = os.path.join(folder, "challenge1b_output.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Output written: {output_path}")

if __name__ == "__main__":
    collections = [d for d in os.listdir() if d.startswith("Collection")]
    if not collections:
        print("No collection folders found (e.g. 'Collection_1').")
    for folder in collections:
        print(f"\nProcessing: {folder}")
        process_collection(folder)
