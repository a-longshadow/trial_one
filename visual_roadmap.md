# TaskForge Workflow – Visual Overview

Below is a simple flow diagram designed for non-technical stakeholders, illustrating the end-to-end process:

```mermaid
flowchart LR
    A[📥 Upload Transcript(s)] --> B[🤖 LLM Analysis]
    B --> C[📝 Generate Task List]
    C --> D[✏️ Editable Board UI]
    D --> E[💾 Export Styled .xlsx]
    E --> F[🔄 Reset for Next Upload]
    
    subgraph Summary
      B -->|✅ 7 tasks for 3 people| C
      D -->|↺ Re-analyze / Undo| C
    end
```

- **Step 1:** Upload transcript file(s) (`.vtt`, `.srt`, `.txt`).  
- **Step 2:** LLM extracts and summarizes action items.  
- **Step 3:** System builds a task list with Item, Assignee, Priority, Status, Due Date, Description.  
- **Step 4:** User reviews and edits in an interactive board UI; can undo or re-run analysis.  
- **Step 5:** Export the final list as a beautifully styled Excel workbook.  
- **Step 6:** The application resets, ready for the next file.

*This visual is intended to communicate the core flow without technical details.*  
