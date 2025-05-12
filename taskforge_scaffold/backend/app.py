from flask import Flask, jsonify, request
from flask_cors import CORS 
from parsers import parse_transcript 
from llm_agent import extract_tasks_from_transcript
import re # Import regex for de-duplication cleaning
from pydantic import BaseModel, Field, ValidationError, field_validator # Import Pydantic components
from typing import List, Literal, Optional
import os # Import os for environment variables

# Determine the correct static folder path relative to this app.py file
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, '..', 'frontend', 'build')

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/')

# --- CORS Configuration ---
# Allow all origins if in development, otherwise restrict to specified origin
# For production, set CORS_ORIGINS environment variable (e.g., "http://localhost:3000,https://yourdomain.com")
# In development, if CORS_ORIGINS is not set, it will default to allowing all for convenience.
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS')
if CORS_ALLOWED_ORIGINS:
    origins = [origin.strip() for origin in CORS_ALLOWED_ORIGINS.split(',')]
    CORS(app, resources={r"/api/*": {"origins": origins}})
    print(f"CORS configured for origins: {origins}")
else:
    CORS(app) # Default to all origins if not specified (OK for dev, review for prod)
    print("CORS_ORIGINS not set, allowing all origins (defaulting for dev). Set CORS_ORIGINS for production.")

# Set max file size (e.g., 10 MB)
MAX_FILE_SIZE_MB = 10
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024

# --- Pydantic Model Definition ---
# Define the structure we expect for each task from the LLM
class TaskModel(BaseModel):
    item: str = Field(..., min_length=1) # Ensure item is not empty
    assignee: str = Field(..., min_length=1) # Ensure assignee is not empty
    priority: Literal["High", "Medium", "Low"]
    status: str # Keep status flexible for now, or use Literal if fixed set is enforced
    dueDate: str # Renamed from dueDate in model to match LLM output key
    description: str
    source_excerpt: str = Field(..., min_length=1) # Added required source_excerpt
    confidence: Optional[Literal["High", "Medium", "Low"]] = "Medium"

    # Optional: Add validators for specific fields if needed
    # @field_validator('dueDate')
    # def check_date_format(cls, v):
    #     # Example: Basic check for YYYY-MM-DD or TBD (can be expanded)
    #     if v != "TBD" and not re.match(r'^^\d{4}-\d{2}-\d{2}$', v):
    #         # More robust validation might be needed for relative dates from LLM
    #         print(f"Warning: dueDate '{v}' doesn't strictly match YYYY-MM-DD or TBD.")
    #         # raise ValueError('dueDate must be YYYY-MM-DD or TBD') 
    #     return v

def normalize_task_item(item_text):
    """Helper function to normalize task item text for de-duplication."""
    if not item_text:
        return ""
    # Lowercase, remove punctuation (except maybe hyphens if needed), collapse whitespace
    text = item_text.lower()
    text = re.sub(r'[^\w\s-]', '', text) # Keep word chars, whitespace, hyphen
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Use getlist to handle multiple files with the same key 'file'
    files = request.files.getlist('file')

    if not files or all(f.filename == '' for f in files):
        return jsonify(error="No selected file(s)"), 400

    all_transcript_text = ""
    processed_files_count = 0
    skipped_files = []

    # Process each uploaded file
    for file in files:
        if file and file.filename != '':
            try:
                print(f"Processing file: {file.filename}, content-type: {file.content_type}")
                # parse_transcript now handles different types and raises ValueError on failure/unsupported
                transcript_text = parse_transcript(file)
                all_transcript_text += f"\n\n--- Transcript from: {file.filename} ---\n\n" + transcript_text
                processed_files_count += 1
                print(f"Successfully parsed and appended: {file.filename}")
            except ValueError as e: # Catch specific parsing/type errors from parser
                print(f"Skipping file {file.filename} due to parsing error: {e}")
                skipped_files.append(file.filename + f" (Skipped: {e})")
            except Exception as e: # Catch other unexpected errors during file processing
                print(f"Unexpected error processing file {file.filename}: {e}")
                skipped_files.append(file.filename + f" (Unexpected Error: {e})")
                # Continue processing other files

    # Check if any files were successfully processed
    if processed_files_count == 0:
         error_message = "No processable files (.txt, .vtt, .srt) were found or all failed during parsing."
         if skipped_files:
             error_message += " Skipped files: " + ", ".join(skipped_files)
         return jsonify(error=error_message), 400

    print(f"Combined text from {processed_files_count} file(s) for LLM processing.")

    # Process the combined text with the LLM
    try:
        print("Attempting to extract tasks using LLM...")
        extracted_tasks_raw = extract_tasks_from_transcript(all_transcript_text)
        
        validated_tasks = []
        validation_errors = []

        if extracted_tasks_raw and isinstance(extracted_tasks_raw, list):
            # Check for the specific error structure returned by llm_agent on API key or other critical errors
            if len(extracted_tasks_raw) == 1 and extracted_tasks_raw[0].get("status") == "Error":
                print(f"LLM agent returned a critical error: {extracted_tasks_raw[0]}")
                tasks_to_return = extracted_tasks_raw # Pass the error task directly
            else:
                # Validate each task object using Pydantic
                for i, task_data in enumerate(extracted_tasks_raw):
                    try:
                        # Add default confidence if missing before validation (alternative to Optional field)
                        # task_data.setdefault('confidence', 'Medium') 
                        validated_task = TaskModel.model_validate(task_data)
                        # .model_dump() includes fields with defaults even if not in input
                        validated_tasks.append(validated_task.model_dump()) 
                    except ValidationError as e:
                        print(f"Validation Error for task #{i}: {e}. Data: {task_data}")
                        validation_errors.append(f"Task {i+1}: {e.errors()}") 
                
                print(f"Successfully validated {len(validated_tasks)} tasks out of {len(extracted_tasks_raw)} received from LLM.")

                # --- De-duplication Logic (applied to validated tasks) --- 
                unique_tasks = []
                seen_items = set()
                for task in validated_tasks:
                    item_text = task.get('item') # Use .get for safety, though Pydantic ensures it exists
                    if isinstance(item_text, str):
                        normalized_item = normalize_task_item(item_text)
                        if normalized_item and normalized_item not in seen_items:
                            seen_items.add(normalized_item)
                            unique_tasks.append(task)
                        elif normalized_item:
                            print(f"Duplicate task item found and removed after validation: '{item_text[:50]}...'")
                    # No else needed, Pydantic validated 'item' exists and is str
                print(f"Returning {len(unique_tasks)} tasks after de-duplication.")
                tasks_to_return = unique_tasks
        else:
            print(f"LLM agent did not return a valid list of tasks. Response: {extracted_tasks_raw}")
            tasks_to_return = [{
                "item": "LLM Response Issue", 
                "description": "LLM did not return a list of tasks as expected.", 
                "priority": "Medium", 
                "status": "Error", 
                "assignee": "System", 
                "dueDate": "",
                "confidence": "Low" # Add confidence here too
             }]

        # Prepend skipped file info and validation errors if any
        info_tasks = []
        if skipped_files:
             info_tasks.append({
                "item": "Skipped Files Info", 
                "description": "Some files were skipped during parsing: " + ", ".join(skipped_files),
                "priority": "Medium", "status": "Info", "assignee": "System", "dueDate": "", "confidence": "High"
             })
        if validation_errors:
             info_tasks.append({
                "item": "Validation Errors", 
                "description": "Some tasks returned by the LLM failed validation: " + "; ".join(validation_errors),
                "priority": "High", "status": "Error", "assignee": "System", "dueDate": "", "confidence": "High"
             })            
        
        # Combine info tasks and actual tasks
        final_tasks = info_tasks + tasks_to_return

        return jsonify(tasks=final_tasks), 200

    except Exception as e:
        print(f"Error processing combined text in app.py: {e}")
        # Return a generic error task list to the frontend
        error_task = [{
            "item": "Unhandled Server Error", 
            "description": f"An unexpected error occurred on the server: {str(e)}", 
            "priority": "High", 
            "status": "Error", 
            "assignee": "System", 
            "dueDate": ""
        }]
        # Use 500 for server errors
        return jsonify(tasks=error_task), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    else:
        return app.send_static_file('index.html')

if __name__ == '__main__':
    # Debug mode should be False in production
    # Use an environment variable to control debug mode and port
    # Example: FLASK_DEBUG=True FLASK_RUN_PORT=5002 python app.py
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    print(f"Starting Flask app with debug_mode={debug_mode} on port={port}")
    app.run(debug=debug_mode, port=port, host='0.0.0.0') # host='0.0.0.0' to be accessible externally
