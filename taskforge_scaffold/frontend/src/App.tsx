import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import TaskBoard from './components/TaskBoard';
import ExcelDownload from './components/ExcelDownload';

function App() {
  const [tasks, setTasks] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState('');
  return (
    <div>
      <UploadForm onProcess={(tasks, url) => { setTasks(tasks); setDownloadUrl(url); }} />
      {tasks.length > 0 && <TaskBoard tasks={tasks} />}
      {downloadUrl && <ExcelDownload url={downloadUrl} />}
    </div>
  );
}

export default App;
