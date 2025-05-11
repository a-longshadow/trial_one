import io
import webvtt
from docx import Document # Import Document for docx parsing
from PyPDF2 import PdfReader # Import PdfReader for pdf parsing
# Removed UploadFile type hint as it's specific to async frameworks like FastAPI/Starlette
# For Flask, the file object from request.files is a FileStorage object

def parse_transcript(file_storage) -> str:
    filename = file_storage.filename
    print(f"Attempting to parse: {filename}")

    if filename.endswith('.vtt'):
        try:
            # Reset stream position in case it was read before
            file_storage.seek(0) 
            reader = webvtt.read_buffer(io.BytesIO(file_storage.read()))
            text = "\n".join([cue.text for cue in reader])
            print("Parsed VTT successfully.")
            return text
        except Exception as e:
            print(f"Error parsing VTT file {filename}: {e}. Trying raw text.")
            # Fallback to reading as text if VTT parsing fails
            file_storage.seek(0)
            return file_storage.read().decode(errors='ignore')

    elif filename.endswith('.txt') or filename.endswith('.srt'): # Treat SRT as plain text for now
        try:
            file_storage.seek(0)
            text = file_storage.read().decode(errors='ignore')
            print(f"Parsed {filename.split('.')[-1].upper()} as plain text.")
            return text
        except Exception as e:
            print(f"Error reading text file {filename}: {e}")
            raise # Re-raise the exception if basic text reading fails
    
    elif filename.endswith('.docx'):
        try:
            file_storage.seek(0)
            # python-docx reads directly from a file-like object
            document = Document(file_storage)
            full_text = []
            for para in document.paragraphs:
                full_text.append(para.text)
            text = '\n'.join(full_text)
            print("Parsed DOCX successfully.")
            return text
        except Exception as e:
            print(f"Error parsing DOCX file {filename}: {e}")
            # Optionally return empty string or raise error
            # For now, raise error to be caught in app.py
            raise ValueError(f"Could not parse DOCX file: {e}") from e

    elif filename.endswith('.pdf'):
        try:
            file_storage.seek(0)
            reader = PdfReader(file_storage)
            full_text = []
            for page in reader.pages:
                full_text.append(page.extract_text() or "") # Add fallback for empty pages
            text = "\n".join(full_text)
            print(f"Parsed PDF successfully ({len(reader.pages)} pages).")
            return text
        except Exception as e:
            print(f"Error parsing PDF file {filename}: {e}")
            raise ValueError(f"Could not parse PDF file: {e}") from e

    else:
        print(f"Unsupported file type for parsing: {filename}")
        # Raise an error for unsupported types to be handled in app.py
        raise ValueError(f"Unsupported file type: {filename.split('.')[-1]}")
