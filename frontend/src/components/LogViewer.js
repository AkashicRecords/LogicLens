import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LogViewer.css';

// Change API URL to use port 8000
const API_BASE_URL = 'http://localhost:8000/api';

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [component, setComponent] = useState('');
  const [level, setLevel] = useState('');
  // eslint-disable-next-line no-unused-vars
  const [filter, setFilter] = useState({
    level: 'all',
    component: 'all',
    search: ''
  });

  const fetchLogs = async () => {
    try {
      setLoading(true);
      let url = `${API_BASE_URL}/logs`;
      const params = {};
      
      if (filter.level !== 'all') {
        params.level = filter.level;
      }
      
      if (filter.component !== 'all') {
        params.component = filter.component;
      }
      
      const response = await axios.get(url, { params });
      
      if (response.data.success && response.data.data) {
        let filteredLogs = response.data.data;
        
        if (filter.search) {
          const searchTerm = filter.search.toLowerCase();
          filteredLogs = filteredLogs.filter(log => 
            log.message.toLowerCase().includes(searchTerm)
          );
        }
        
        setLogs(filteredLogs);
        setError(null);
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to fetch logs. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchLogs();
    
    // Refresh logs every 30 seconds
    const interval = setInterval(fetchLogs, 30000);
    
    return () => clearInterval(interval);
  }, [filter]);

  const handleFilter = (e) => {
    e.preventDefault();
    fetchLogs();
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (err) {
      return timestamp;
    }
  };

  const getLevelClass = (level) => {
    switch (level?.toUpperCase()) {
      case 'ERROR': return 'log-level-error';
      case 'WARNING': return 'log-level-warning';
      case 'INFO': return 'log-level-info';
      case 'DEBUG': return 'log-level-debug';
      default: return '';
    }
  };

  return (
    <div className="log-viewer">
      <h2>Log Viewer</h2>
      
      <div className="log-filter">
        <form onSubmit={handleFilter}>
          <div className="filter-group">
            <label>
              Component:
              <input 
                type="text" 
                value={component} 
                onChange={(e) => setComponent(e.target.value)} 
                placeholder="Filter by component"
              />
            </label>
            
            <label>
              Level:
              <select value={level} onChange={(e) => setLevel(e.target.value)}>
                <option value="">All Levels</option>
                <option value="DEBUG">Debug</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="ERROR">Error</option>
              </select>
            </label>
            
            <button type="submit">Filter</button>
            <button type="button" onClick={() => {
              setComponent('');
              setLevel('');
              setTimeout(fetchLogs, 0);
            }}>Reset</button>
          </div>
        </form>
      </div>
      
      {loading && <div className="loading">Loading logs...</div>}
      {error && <div className="error">{error}</div>}
      
      {!loading && !error && logs.length === 0 && (
        <div className="no-logs">No logs found</div>
      )}
      
      {logs.length > 0 && (
        <div className="logs-table-container">
          <table className="logs-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Level</th>
                <th>Component</th>
                <th>Message</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, index) => (
                <tr key={index} className={getLevelClass(log.level)}>
                  <td>{formatTimestamp(log.timestamp)}</td>
                  <td>{log.level}</td>
                  <td>{log.component}</td>
                  <td>{log.message}</td>
                  <td>
                    {log.details && Object.keys(log.details).length > 0 && (
                      <details>
                        <summary>View Details</summary>
                        <pre>{JSON.stringify(log.details, null, 2)}</pre>
                      </details>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      <div className="refresh-controls">
        <button onClick={fetchLogs}>Refresh Logs</button>
      </div>
    </div>
  );
};

export default LogViewer; 