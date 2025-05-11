import React from 'react';
// Import routing components
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom'; 
import TaskBoard from './components/TaskBoard';

// Mock data (can be removed if backend provides all tasks, or kept for fallback)
// const mockTasks = [
//   {
//     item: "Draft initial project proposal",
//     assignee: "Alice",
//     priority: "High",
//     status: "Working on it",
//     dueDate: "2025-05-15",
//     description: "Create the first draft of the project proposal document for internal review."
//   },
//   {
//     item: "Set up client meeting",
//     assignee: "Bob",
//     priority: "Medium",
//     status: "Stuck",
//     dueDate: "2025-05-20",
//     description: "Client is unresponsive, need to follow up or escalate."
//   },
//   {
//     item: "Review design mockups",
//     assignee: "Charlie",
//     priority: "High",
//     status: "Waiting for review",
//     dueDate: "2025-05-12",
//     description: "Provide feedback on the latest set of UI mockups from the design team."
//   },
//   {
//     item: "Finalize Q2 budget",
//     assignee: "Alice",
//     priority: "Low",
//     status: "Done",
//     dueDate: "2025-04-30",
//     description: "Q2 budget has been finalized and approved."
//   }
// ];

// Main App component that will contain routing logic
function App() {
  return (
    <Routes>
      <Route path="/" element={<UploadScreen />} />
      <Route path="/board" element={<TaskBoardScreen />} />
    </Routes>
  );
}

// Component for the Upload Screen logic
function UploadScreen() {
  const [selectedFiles, setSelectedFiles] = React.useState([]);
  const [isProcessing, setIsProcessing] = React.useState(false);
  const [progress, setProgress] = React.useState(0);
  const [error, setError] = React.useState(null);
  const [isDraggingOver, setIsDraggingOver] = React.useState(false);
  const progressIntervalRef = React.useRef(null);
  const navigate = useNavigate(); // Hook for navigation
  const MAX_FILES_COUNT = 5; // New constant for max files

  const MAX_FILE_SIZE_MB = 10;
  const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
  const ACCEPTED_FILE_TYPES = ".vtt,.srt,.txt,.pdf,.docx";
  const ACCEPTED_FILE_TYPES_ARRAY = ACCEPTED_FILE_TYPES.split(',');

  const validateFile = (file) => {
    if (!file) return "No file selected.";
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ACCEPTED_FILE_TYPES_ARRAY.includes(fileExtension)) {
      return `Invalid file type (${file.name}). Please upload one of: ${ACCEPTED_FILE_TYPES}`;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return `File (${file.name}) is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`;
    }
    return null;
  };

  const handleFileSelect = (files) => {
    if (!files || files.length === 0) {
      setSelectedFiles([]);
      setError(null);
      return;
    }

    const newFilesArray = Array.from(files);

    if (newFilesArray.length > MAX_FILES_COUNT) {
      setError(`You can only upload a maximum of ${MAX_FILES_COUNT} files at a time.`);
      setSelectedFiles([]); // Clear selection
      return;
    }

    let validationError = null;
    const validFiles = [];
    for (const file of newFilesArray) { // Use newFilesArray here
        const err = validateFile(file);
        if (err) {
            validationError = err;
            break;
        } else {
            validFiles.push(file);
        }
    }
    if (validationError) {
        setError(validationError);
        setSelectedFiles([]);
    } else {
        setSelectedFiles(validFiles);
        setError(null);
        setIsProcessing(false);
        setProgress(0);
    }
  };

  const handleFileChange = (event) => {
    handleFileSelect(event.target.files);
    event.target.value = null;
  };

  const handleDragEnter = (event) => { event.preventDefault(); event.stopPropagation(); setIsDraggingOver(true); };
  const handleDragLeave = (event) => { 
    event.preventDefault(); event.stopPropagation(); 
    if (!event.currentTarget.contains(event.relatedTarget)) setIsDraggingOver(false); 
  };
  const handleDragOver = (event) => { event.preventDefault(); event.stopPropagation(); setIsDraggingOver(true); };
  const handleDrop = (event) => {
    event.preventDefault(); event.stopPropagation(); setIsDraggingOver(false);
    handleFileSelect(event.dataTransfer?.files);
  };

  const playNotificationSound = () => {
    try { new Audio('/notification.mp3').play().catch(e => console.error("Error playing sound:", e)); }
    catch (e) { console.error("Could not play audio:", e); }
  };

  const clearProgressInterval = () => {
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
  };

  const handleProcessFile = async () => {
    if (!selectedFiles || selectedFiles.length === 0) return;
    clearProgressInterval();
    setIsProcessing(true);
    setProgress(0);
    setError(null);

    progressIntervalRef.current = setInterval(() => {
      setProgress(prev => (prev >= 95 ? (clearProgressInterval(), prev) : prev + 5));
    }, 150);

    const formData = new FormData();
    selectedFiles.forEach(file => formData.append('file', file));

    try {
      // const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';
      // const response = await fetch(`${apiBaseUrl}/api/upload`, {
      const response = await fetch('/api/upload', { // API call to relative path
        method: 'POST',
        body: formData,
      });
      clearProgressInterval();
      if (!response.ok) {
        let errorMsg = `Server error: ${response.status}`;
        try { const errData = await response.json(); errorMsg = errData.error || JSON.stringify(errData) || errorMsg; }
        catch (parseError) { errorMsg = response.statusText || errorMsg; }
        throw new Error(errorMsg);
      }
      const data = await response.json();
      setProgress(100);
      playNotificationSound();
      // Navigate to TaskBoardScreen with tasks data
      navigate('/board', { state: { tasks: data.tasks || [] } }); 
    } catch (err) {
      console.error("Error processing file:", err);
      setError(err.message || "An unexpected error occurred.");
      clearProgressInterval();
      setIsProcessing(false);
      setProgress(0);
    }
  };

  const currentYear = new Date().getFullYear();
  const getProgressBarColor = (percentage) => {
    if (percentage < 34) return '#ff6347';
    if (percentage < 67) return '#ffa500';
    if (percentage < 91) return '#90ee90';
    return '#2e8b57';
  };

  // JSX for UploadScreen
  return (
    <div className="container">
      <header className="app-header">
        <Link to="/" style={{ textDecoration: 'none', color: 'var(--tf-accent)', display: 'flex', alignItems: 'center' }}>
          <img src="/assets/logo.png" alt="TaskForge Logo" style={{ height: '60px', marginRight: '15px', verticalAlign: 'middle' }} />
          <h1>TaskForge</h1>
        </Link>
        <span style={{ cursor: 'pointer' }}>Help</span> 
      </header>
      <main className="upload-screen">
        <div 
          className={`file-upload-area ${isDraggingOver ? 'dragging-over' : ''} ${selectedFiles.length > 0 ? 'has-files' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <p>Drag & Drop or Browse .vtt, .srt, .txt, .pdf, .docx files (Max {MAX_FILE_SIZE_MB}MB each, {MAX_FILES_COUNT} files max)</p>
          <input
            type="file"
            accept={ACCEPTED_FILE_TYPES}
            style={{ display: 'none' }}
            id="fileInput"
            onChange={handleFileChange}
            multiple
          />
          <button onClick={() => document.getElementById('fileInput').click()} className="button button-secondary">
            Browse Files
          </button>
          {selectedFiles.length > 0 && (
            <div className="file-display-area" style={{ textAlign: 'left', marginTop: '1rem', maxHeight: '150px', overflowY: 'auto', border: '1px solid var(--tf-muted)', padding: 'var(--space-1)', borderRadius: '4px' }}>
              <strong>Selected files ({selectedFiles.length}):</strong>
              <ul>
                {selectedFiles.map((file, index) => (
                  <li key={index} style={{ fontSize: '0.875rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        {error && (
          <div className="error-message-container">
            <p>{error}</p>
          </div>
        )}
        <button
          className="button button-primary upload-button"
          disabled={selectedFiles.length === 0 || isProcessing}
          onClick={handleProcessFile}
        >
          {isProcessing ? `Processing... ${progress}%` : `Process ${selectedFiles.length} File(s)`}
        </button>
        {isProcessing && (
          <div className="progress-bar-container" style={{ width: '100%', backgroundColor: '#e0e0e0', borderRadius: '4px', marginTop: '1rem' }}>
            <div
              className="progress-bar"
              style={{
                width: `${progress}%`,
                height: '20px',
                backgroundColor: getProgressBarColor(progress),
                borderRadius: '4px',
                textAlign: 'center',
                color: progress > 50 ? 'white' : 'black',
                lineHeight: '20px',
                transition: 'width 0.15s ease-in-out, background-color 0.3s ease'
              }}
            >
              {progress}%
            </div>
          </div>
        )}
      </main>
      <footer className="app-footer">
        <p>&copy; {currentYear} TaskForge</p>
      </footer>
    </div>
  );
}

// New component to handle displaying the TaskBoard, receives tasks via route state
function TaskBoardScreen() {
  const location = useLocation();
  const navigate = useNavigate();
  const tasks = location.state?.tasks; // Get tasks from navigation state

  const handleProcessAnother = () => {
    navigate('/'); // Navigate back to the upload screen
  };

  React.useEffect(() => {
    if (!tasks) {
      console.warn("No tasks found in location state, redirecting to home.");
      navigate('/');
    }
  }, [tasks, navigate]);

  if (!tasks) {
    return null; 
  }

  return <TaskBoard tasks={tasks} onBack={handleProcessAnother} />;
}

export default App; 