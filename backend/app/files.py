import io
def extract(name: str, data: bytes) -> str:
    n = name.lower()
    if n.endswith(".docx"):
        import docx
        return "\n\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs if p.text.strip())
    if n.endswith(".pdf"):
        import fitz
        return "\n\n".join(pg.get_text() for pg in fitz.open(stream=data, filetype="pdf"))
    if n.endswith((".txt", ".md")):
        return data.decode("utf-8", "ignore")
    raise ValueError("Supported: .txt .md .docx .pdf")
