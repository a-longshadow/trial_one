# TaskForge UI/UX Framework

A comprehensive design system and workflow for TaskForge’s core application, combining **Apple.com clarity** with **Google Workspace structure** to support the six-step flow:

1. **Ingest** – Upload transcripts
2. **Analyze** – LLM extracts action items
3. **Generate** – Smart task board creation
4. **Edit** – In-app inline adjustments
5. **Export** – Styled .xlsx download
6. **Reset** – Ready for next upload

---

## 1. Design Principles

1. **Clarity & Focus**  
   - Single primary CTA per screen  
   - Minimal chrome, contextual information only
2. **Consistency**  
   - 8-pt grid, shared spacing (0.5rem increments)  
   - Atomic Design: Atoms → Molecules → Organisms
3. **Feedback & Forgiveness**  
   - Inline toasts and error markers  
   - Undo / Reset functions on destructive actions
4. **Accessibility**  
   - WCAG 2.1 AA contrast  
   - Full keyboard support, focus states, ARIA labels
5. **Performance & Responsiveness**  
   - Mobile-first; bottom nav on small screens  
   - Skeleton loaders during LLM steps

---

## 2. Design Tokens

```css
:root {
  /* Colors */
  --tf-bg: #0f1114;
  --tf-surface: #22262b;
  --tf-accent: #ff5a2c;
  --tf-success: #c8f169;
  --tf-text: #ffffff;
  --tf-muted: #5a6b7c;

  /* Spacing */
  --space-1: 0.5rem;
  --space-2: 1rem;
  --space-3: 1.5rem;
  --space-4: 2rem;

  /* Typography */
  --font-sans: 'IBM Plex Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --text-base: 1rem;
  --text-lg: 1.125rem;
}
```

---

## 3. Layout & Grid

- **Container:** max-width 1280px; gutters `clamp(1rem,4vw,2rem)`  
- **Columns:** 12-column grid → 1 col on <640px  
- **Header:** 64px fixed top; collapses on scroll

---

## 4. Core Components

| Component   | Purpose & Props                                    |
|-------------|----------------------------------------------------|
| **Button**  | Variants: primary, secondary, text; hover/active   |
| **Input**   | Text/date/dropdown; focus & error states           |
| **FileUpload** | Drag/drop or click; preview + size + errors     |
| **DataTable** | Editable grid: inline edits, undo/redo, sorting  |
| **Toast**    | Non-blocking alerts: success, error, info        |
| **Modal**    | For “Re-analyze” settings; ESC/close dismiss     |
| **Skeleton** | Placeholder rows during LLM calls                 |
| **Avatar**   | Circle initials for assignees (32px)             |

---

## 5. Screen Flows & Wireframes

### 5.1 Upload Screen

```
+-------------------------+
| [TaskForge logo] [Help] |
| [Drag or Browse .vtt/.srt/.txt] |
|     [Upload Button]     |
+-------------------------+
```

### 5.2 Analysis Screen

```
+-------------------------+
| 🤖 Extracting tasks... [Cancel] |
| [Skeleton Table Rows]    |
+-------------------------+
```

### 5.3 Task Board Screen

```
+-------------------------+
| ✅ 7 tasks for 3 people  [Re-analyze] [Reset] |
| [Editable Table]        |
| + Add row (light gray)  |
| [Export .xlsx Button]   |
+-------------------------+
```

---

## 6. Interaction Patterns

- **Inline Validation:** Real-time feedback on date/assignee errors  
- **Keyboard Shortcuts:** Ctrl+S (export), Ctrl+Z/Y (undo/redo)  
- **Responsive:** Horizontal scroll on tablet; card stack on mobile

---

## 7. Accessibility

- Tab navigation, focus ring `2px solid var(--tf-accent)`  
- `aria-live` regions for toasts  
- `prefers-reduced-motion` support

---

**Next Steps:**
1. Build Figma component library
2. Develop atomic React components
3. Perform usability testing (5 users)

_Last updated: 8 May 2025_
