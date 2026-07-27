import fitz #pymupdf
file_path ="data/raw/ncert_pdfs/iesc107.pdf"
doc=fitz.open(file_path)
print(len(doc))