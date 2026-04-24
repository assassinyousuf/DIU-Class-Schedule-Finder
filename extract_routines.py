import pypdf
import os
import json

def extract_text_from_pdf(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

files = [
    "Routine-CSE-Bi-1st-82-103-Jan-Jun-2026-Updated-270326 (1).pdf",
    "Routine-CSE-Bi-1st-84-104-Broken-Jan-Jun-2026-Updated-300326 (3).pdf",
    "Routine-CSE-Tri-1st-Spring-2026-Updated-270326 (1).pdf"
]

results = {}
for f in files:
    path = os.path.join(r"e:\CPC\routine", f)
    if os.path.exists(path):
        print(f"Extracting {f}...")
        results[f] = extract_text_from_pdf(path)
    else:
        print(f"File not found: {f}")

with open("extracted_routines.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)
