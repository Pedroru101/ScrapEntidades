
import sys
from pypdf import PdfReader

def pdf_to_markdown(pdf_path, md_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Transcription\n\n")
            f.write(text)
        print(f"Successfully converted {pdf_path} to {md_path}")
    except Exception as e:
        print(f"Error converting PDF: {e}")

if __name__ == "__main__":
    pdf_to_markdown(
        r"c:\Users\quint\Desktop\ScrapEntidades\Meeting Transcription.pdf",
        r"c:\Users\quint\Desktop\ScrapEntidades\docs\transcripcion_reunion.md"
    )
