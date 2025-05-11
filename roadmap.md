# TaskForge – Finalized Workflow Roadmap

> **Core Flow**  
> Ingest – Analyze – Generate – Edit – Export – Reset

---

## 1. Ingest Transcripts  
- **Acceptable formats:** `.vtt`, `.srt`, `.txt` (plus `.pdf`, `.docx` selection enabled; backend parsing TBD).
- **Batch Mode:** Upload multiple files; transcripts are merged for analysis.

## 2. LLM Analysis  
- **Extract actions:** ChatGPT scans every sentence ending in obligation verbs.  
- **Quick Summary banner:**  
  > ✅ *7 tasks extracted for 3 teammates*

## 3. Smart Task Generation  
- **Fields produced:**  
  1. **Item**  
  2. **Assignee** (mapped via SQLite)  
  3. **Priority** (High | Medium | Low)  
  4. **Status** (Stuck | Working on it | Waiting for review | Done)  
  5. **Due Date** (ISO YYYY-MM-DD)  
  6. **Brief Description**  
- **De-duplication & sanitization** runs automatically, tuned by your prompt.

## 4. In-App Editing  
- **Editable board UI** replicates Monday's look & feel.  
- **Inline "Re-analyze"** re-runs the LLM with tweaked rules—no re-upload needed.  
- **Undo / Reset** lets you revert to the original extraction.

## 5. Export as Spreadsheet  
- **Common board** for all teammates (separate tabs per assignee + "Unassigned").  
- **Styling:** dark header, colored priority/status pills, frozen header, dropdowns.  
- **Post-export tag:**  
  > 📄 *Last saved: 2025-05-08 14:32 by you*

## 6. Reset & Ready for Next  
- **Session clears** previous data & temp files.  
- **UI resets** to upload state, ready for next transcript or batch.

---

### Visual Quick-Flow

```
[Upload Transcript(s)]
         ↓
[LLM Analysis → ✅ "7 tasks for 3 people"]
         ↓
[Auto-Generate Task List (6 fields)]
         ↓
[Editable Board UI]
    ↳ [Undo / Reset]   [Re-analyze]
         ↓
[Export → Styled .xlsx + "Last saved…"]
         ↓
[Reset → Ready for next upload]
```

*All steps run offline; APIs plug in later without touching this core flow.*  
_Last updated: 8 May 2025_