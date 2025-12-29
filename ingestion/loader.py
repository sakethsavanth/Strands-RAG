import fitz

def load_pdf(path: str):
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        pages.append({
            "page": i + 1,
            "text": page.get_text()
        })
    return pages
