# TaskForge Scaffold

This project is a scaffold for the TaskForge application, designed to help you quickly get started with development and testing on your localhost.

It includes a React frontend and a Python Flask backend.

## Project Structure

```
taskforge_scaffold/
├── backend/
│   ├── app.py            # Flask backend application
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html    # Main HTML page for React app
│   ├── src/
│   │   ├── App.css       # Styles for the App component (includes design tokens)
│   │   ├── App.js        # Main React application component (Upload Screen)
│   │   ├── index.js      # React entry point
│   │   └── reportWebVitals.js # Performance monitoring
│   └── package.json      # Frontend dependencies and scripts
└── README.md             # This file
```

## Prerequisites

- Node.js and npm (or yarn) for the frontend.
- Python 3 and pip for the backend.
- A `.env` file in the `backend` directory for API keys if your LLM agent requires them (e.g., `LLM_API_KEY=your_key_here`). The `llm_agent.py` should be adapted to load this.
- (For Production) A WSGI server like Gunicorn: `pip install gunicorn`

## Environment Variables

For optimal configuration and security, the application uses environment variables:

### Backend (`taskforge_scaffold/backend/`)
Create a `.env` file in this directory or set system environment variables:
- `FLASK_DEBUG`: (boolean, e.g., `True` for development, `False` for production). Defaults to `False`.
- `FLASK_RUN_PORT`: (integer, e.g., `5001`). Defaults to `5001`.
- `CORS_ORIGINS`: (string, comma-separated list of allowed frontend origins, e.g., `http://localhost:3000,https://your-frontend-domain.com`). If not set, defaults to all origins (suitable for local development). **Crucial for production.**
- `LLM_API_KEY` (or other keys required by `llm_agent.py`): Specific keys needed for the LLM integration.

### Frontend (`taskforge_scaffold/frontend/`)
Create a `.env` file in this directory or set system environment variables for build time:
- `REACT_APP_API_BASE_URL`: (string, e.g., `http://localhost:5001` for local dev, or your production backend URL `https://api.yourdomain.com`). Defaults to `http://localhost:5001` in the code if not set.

## Setup and Running

### 1. Backend (Flask)

Navigate to the backend directory:
```bash
cd taskforge_scaffold/backend
```

Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
```

Install dependencies:
```bash
pip install -r requirements.txt
```
**Recommendation for production**: Pin your dependencies by running `pip freeze > requirements.txt` after confirming stable versions.

**For Development:**
Run the backend server (it will use defaults or variables from a local `.env` file):
```bash
python app.py
```
Example with explicit environment variables:
```bash
FLASK_DEBUG=True FLASK_RUN_PORT=5002 CORS_ORIGINS=http://localhost:3000 python app.py
```
You should see a message indicating the Flask development server is running.

**For Production (using Gunicorn):**
Ensure Gunicorn is installed: `pip install gunicorn`
Run the backend server with Gunicorn (adjust workers as needed):
```bash
# Example: Make sure FLASK_DEBUG=False is set in your environment or .env
gunicorn --bind 0.0.0.0:$FLASK_RUN_PORT app:app
# Or with a specific port if FLASK_RUN_PORT is not set:
# gunicorn --bind 0.0.0.0:5001 app:app
```

### 2. Frontend (React)

In a new terminal window, navigate to the frontend directory:
```bash
cd taskforge_scaffold/frontend
```

Install dependencies:
```bash
npm install
# or if you use yarn:
# yarn install
```
**Recommendation for production/CI**: Use `npm ci` which installs from `package-lock.json`.


**For Development:**
Set your API base URL if it differs from the default:
```bash
# Example for .env file in frontend directory:
# REACT_APP_API_BASE_URL=http://localhost:5001
```
Run the frontend development server (defaults to http://localhost:3000):
```bash
npm start
# or if you use yarn:
# yarn start
```
This should automatically open the TaskForge upload page in your default web browser.

**For Production:**
Set your production API base URL:
```bash
# Example for .env file in frontend directory (used during build):
# REACT_APP_API_BASE_URL=https://your-backend-api.com
```
Build the static assets:
```bash
npm run build
```
The optimized static files will be in the `build/` directory. Deploy these files using a static web server (e.g., Nginx, Vercel, Netlify, AWS S3/CloudFront).

## Deployment Overview

1.  **Configure Backend**:
    *   Set environment variables: `FLASK_DEBUG=False`, `FLASK_RUN_PORT` (e.g., 8000 if behind a reverse proxy), `CORS_ORIGINS` (to your frontend domain), and any `LLM_API_KEY`s.
    *   Run the backend using a WSGI server like Gunicorn: `gunicorn --workers 4 --bind 0.0.0.0:YOUR_CHOSEN_PORT app:app`.
2.  **Configure Frontend**:
    *   Set the `REACT_APP_API_BASE_URL` environment variable to point to your deployed backend API.
    *   Build the frontend: `npm run build`.
3.  **Serve Frontend**:
    *   Deploy the contents of the `taskforge_scaffold/frontend/build/` directory using a static file server or hosting platform.
4.  **Web Server (Optional but Recommended)**:
    *   Consider using a web server like Nginx in front of your Gunicorn backend to handle SSL termination, serve static files (if colocated, though not typical for React builds), and act as a reverse proxy.

## Development Workflow

The application is based on the following core flow (from `roadmap.md`):

1.  **Ingest Transcripts:** Upload `.vtt`, `.srt`, `.txt` files via the UI.
2.  **LLM Analysis:** The backend (not yet fully implemented) will extract actions.
3.  **Smart Task Generation:** Tasks with predefined fields will be created.
4.  **In-App Editing:** A board UI (to be developed) will allow task editing.
5.  **Export as Spreadsheet:** Tasks can be exported to a styled `.xlsx` file.
6.  **Reset & Ready for Next:** Clear session data.

The UI/UX is guided by `ui_ux_framework.md`, aiming for clarity and a modern feel.

---
_This scaffold was generated to kickstart the TaskForge project._
