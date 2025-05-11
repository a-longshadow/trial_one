import React from 'react';
import { Link } from 'react-router-dom';
import * as XLSX from 'xlsx'; // Import xlsx library

const TaskBoard = ({ tasks, onBack }) => {
  // Handle error tasks (can be refined)
  const errorTask = tasks?.find(task => task.status === 'Error');
  if (errorTask) {
    tasks = [errorTask]; // Show only the error task if one exists
  }

  const handleDownloadExcel = () => {
    console.log("Preparing Excel download for tasks:", tasks);
    if (!tasks || tasks.length === 0 || (tasks.length === 1 && tasks[0]?.status === 'Error')) {
      alert("No valid tasks to download.");
      return;
    }

    // Filter out any Info/Error tasks if necessary, or adjust columns
    const tasksToExport = tasks.filter(task => task.status !== 'Error' && task.status !== 'Info');
    if (tasksToExport.length === 0) {
      alert("No data tasks found to export.");
      return;
    }

    // Define headers (ensure they match task object keys)
    const headers = ["item", "assignee", "priority", "status", "dueDate", "confidence", "description"];
    // Create worksheet data: headers first, then task data
    const wsData = [
      headers.map(h => h.charAt(0).toUpperCase() + h.slice(1)), // Capitalize headers
      ...tasksToExport.map(task => headers.map(header => task[header] ?? '')) // Map task data, handle undefined
    ];

    const ws = XLSX.utils.aoa_to_sheet(wsData);

    // Optional: Set column widths (example, adjust as needed)
    const colWidths = [
      { wch: 40 }, // Item
      { wch: 20 }, // Assignee
      { wch: 10 }, // Priority
      { wch: 15 }, // Status
      { wch: 15 }, // Due Date
      { wch: 10 }, // Confidence
      { wch: 60 }  // Description
    ];
    ws['!cols'] = colWidths;

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Tasks");

    // Generate filename
    const fileName = `TaskForge_Board_${new Date().toISOString().split('T')[0]}.xlsx`;

    // Trigger download
    XLSX.writeFile(wb, fileName);
  };

  if (!tasks || tasks.length === 0 || (tasks.length === 1 && errorTask)) {
    // Centering container for empty state or error
    const message = errorTask ? `Error: ${errorTask.item} - ${errorTask.description}` : "No tasks were extracted from the transcript.";
    return (
      <div className="empty-error-container">
        <div className="empty-error-content">
          <Link to="/" style={{ textDecoration: 'none', color: 'var(--tf-accent)' }}>
            <h2>Task Board</h2>
          </Link>
          <p>{message}</p>
          <button onClick={onBack} className="button button-secondary">Process Another File</button>
        </div>
        <footer className="app-footer">
            <p>&copy; {new Date().getFullYear()} TaskForge</p>
        </footer>
      </div>
    );
  }

  const currentYear = new Date().getFullYear();

  return (
    <div className="task-board-container">
      <header className="app-header">
        <Link to="/" style={{ textDecoration: 'none', color: 'var(--tf-accent)', display: 'flex', alignItems: 'center' }}>
          <img src="/assets/logo.png" alt="TaskForge Logo" style={{ height: '60px', marginRight: '15px', verticalAlign: 'middle' }} />
           <h1>TaskForge</h1>
        </Link>
        <span className="task-board-header-subtitle" style={{ fontSize: 'var(--text-lg)', marginLeft: '10px', color: 'var(--tf-text)' }}>- Task Board</span>
        <button 
            onClick={handleDownloadExcel} 
            className="button button-secondary" 
            style={{marginLeft: '20px'}} // Add some space
            disabled={!tasks || tasks.length === 0 || (tasks.length === 1 && tasks[0]?.status === 'Error')} // Disable if no data
        >
            Download .xlsx
        </button>
        <button onClick={onBack} className="button button-secondary" style={{marginLeft: 'auto'}}>Process New File</button>
      </header>
      <main>
        <table className="task-table">
          <thead>
            <tr>
              <th>Item</th>
              <th>Assignee</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Due Date</th>
              <th>Confidence</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task, index) => (
              <tr key={index}>
                <td>{task.item}</td>
                <td>{task.assignee}</td>
                <td>{task.priority}</td>
                <td>{task.status}</td>
                <td>{task.dueDate}</td>
                <td>{task.confidence}</td>
                <td>{task.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
      <footer className="app-footer">
        <p>&copy; {currentYear} TaskForge</p>
      </footer>
    </div>
  );
};

export default TaskBoard; 