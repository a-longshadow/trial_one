import os
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

load_dotenv()

# Default model - can be made configurable later if needed
DEFAULT_MODEL = "llama3.1-8b"

# Max characters for the transcript to leave room for prompts and stay within token limits
# 8192 token limit. Approx 4 chars/token. Prompts take some tokens.
# Let's aim for transcript text to be around ~2000 tokens * 4 chars/token = 8000 chars.
MAX_TRANSCRIPT_CHARS = 8000

# System prompt to guide the LLM
SYSTEM_PROMPT = """
You are a highly precise data extraction engine. Your sole purpose is to extract action items from meeting transcripts and output ONLY a valid JSON list of task objects. Do NOT include any introduction, commentary, or explanation before or after the JSON list.

Each task object in the list MUST contain the following fields EXACTLY:
- "item": (string) Concise summary of the specific action item.
- "assignee": (string) The person or group assigned. 
    - Use the speaker label associated with commitment statements (e.g., "I will...", "I can take that...") as the primary source for the assignee.
    - If a task is assigned via a question (e.g., "Can you do X?"), only extract the task if there is a clear acceptance (e.g., "Yes", "Sure", "I will") from the person addressed in the subsequent dialogue. Assign the task to the person who accepted.
    - If no assignee can be determined with reasonable confidence, default to "Unassigned".
- "priority": (string) Must be one of "High", "Medium", or "Low". Default to "Medium" if not explicitly stated.
- "status": (string) Default to "Todo". Other potential values if mentioned: "Working on it", "Stuck", "Waiting for review", "Done".
- "dueDate": (string) The target completion date. Look for explicit dates (format YYYY-MM-DD), relative dates ("by EOW", "next week", "Q3" -> "End of Q3"), or use "TBD" if no date/timeframe is mentioned.
- "description": (string) A brief elaboration of the task.
- "source_excerpt": (string) The specific sentence(s) from the transcript that directly led to this task extraction. This is crucial for traceability.
- "confidence": (string) Your confidence in the accuracy of the extraction. Must be one of "High", "Medium", or "Low". Base this ONLY on the clarity and explicitness of the task mention, assignment, and date in the source text.

Example of a single task object:
{ "item": "Finalize Q2 budget", "assignee": "Alice", "priority": "High", "status": "Todo", "dueDate": "2025-06-30", "description": "Alice to finalize the Q2 budget.", "source_excerpt": "Alice: Okay, I will finalize the Q2 budget by the end of June.", "confidence": "High" }

Strictly adhere to this structure and field requirements for every object in the JSON list. Output the JSON list and nothing else.
"""

def extract_tasks_from_transcript(transcript_text: str) -> list:
    """
    Sends the transcript text to the Cerebras LLM and attempts to extract tasks.
    Returns a list of task dictionaries or an empty list if an error occurs or no tasks are found.
    """
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        print("Error: CEREBRAS_API_KEY environment variable not set.")
        # Returning an error structure that the frontend can display
        # Or, could raise an exception to be caught in app.py
        return [{"item": "Configuration Error", "description": "CEREBRAS_API_KEY not set on server.", "priority": "High", "status": "Error", "assignee": "Admin", "dueDate": ""}]

    try:
        client = Cerebras(api_key=api_key)

        # Truncate transcript_text if it's too long
        if len(transcript_text) > MAX_TRANSCRIPT_CHARS:
            print(f"Original transcript length: {len(transcript_text)} chars. Truncating to {MAX_TRANSCRIPT_CHARS} chars.")
            truncated_transcript_text = transcript_text[:MAX_TRANSCRIPT_CHARS]
        else:
            truncated_transcript_text = transcript_text

        user_prompt = f"""
Transcript:
---
{truncated_transcript_text}
---
Extract all action items from this transcript and provide them in the specified JSON format.
"""
        print(f"Sending request to Cerebras API with model: {DEFAULT_MODEL}")
        # print(f"User prompt (first 200 chars): {user_prompt[:200]}") # For debugging prompt length issues

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            model=DEFAULT_MODEL,
            temperature=0.0, # Lowest temperature for maximum determinism
            max_tokens=4096, 
        )

        raw_response_content = chat_completion.choices[0].message.content
        print(f"Raw LLM response content: {raw_response_content}")

        # Attempt to parse the response as JSON
        # The LLM should ideally return only JSON, but sometimes includes extra text or markdown
        # Basic cleaning: find the start and end of the JSON list or object
        json_start_index = raw_response_content.find('[')
        json_end_index = raw_response_content.rfind(']')
        
        if json_start_index != -1 and json_end_index != -1 and json_end_index > json_start_index:
            json_string = raw_response_content[json_start_index : json_end_index+1]
            try:
                tasks = json.loads(json_string)
                if isinstance(tasks, list):
                    print(f"Successfully parsed {len(tasks)} tasks from LLM response.")
                    return tasks
                else:
                    print("Error: LLM response was valid JSON but not a list as expected.")
                    return [{"item": "LLM Formatting Error", "description": "Response was not a JSON list.", "priority": "High", "status": "Error", "assignee": "System", "dueDate": ""}]
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from LLM response: {e}")
                print(f"Problematic JSON string: {json_string}")
                return [{"item": "LLM JSON Error", "description": f"Could not decode JSON: {e}", "priority": "High", "status": "Error", "assignee": "System", "dueDate": ""}]
        else:
            print("Error: Could not find valid JSON list in LLM response.")
            return [{"item": "LLM Response Error", "description": "No valid JSON list found in response.", "priority": "High", "status": "Error", "assignee": "System", "dueDate": ""}]

    except Exception as e:
        print(f"An error occurred while calling the Cerebras API: {e}")
        # Return an error task to be displayed on the frontend
        return [{"item": "API Call Error", "description": str(e), "priority": "High", "status": "Error", "assignee": "System", "dueDate": ""}] 