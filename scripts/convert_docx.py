
import sys
from docx import Document

def docx_to_markdown(docx_path, md_path):
    try:
        doc = Document(docx_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n\n"
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Puntos de dolor y estructura organizacional\n\n")
            f.write(text)
        print(f"Successfully converted {docx_path} to {md_path}")
    except Exception as e:
        print(f"Error converting DOCX: {e}")

if __name__ == "__main__":
    docx_to_markdown(
        r"c:\Users\quint\Desktop\ScrapEntidades\Puntos de dolor y estructura organizacional, conocer en profundidad a la organización.docx",
        r"c:\Users\quint\Desktop\ScrapEntidades\docs\requerimientos_profundos.md"
    )
