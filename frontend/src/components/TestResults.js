import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TestResults.css';

// Change API URL to use port 8000
const API_BASE_URL = 'http://localhost:8000/api';

const TestResults = () => {
  const [testSuites, setTestSuites] = useState([]);
  const [selectedSuite, setSelectedSuite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    fetchTestSuites();
    
    // Refresh test results every 60 seconds
    const interval = setInterval(fetchTestSuites, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchTestSuites = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/test-results`);
      if (response.data.success && response.data.data) {
        setTestSuites(response.data.data.suites || []);
        // Auto-select the first suite if one exists and none is selected
        if (response.data.data.suites && response.data.data.suites.length > 0 && !selectedSuite) {
          setSelectedSuite(response.data.data.suites[0]);
        }
      }
    } catch (err) {
      console.error('Error fetching test results:', err);
      setError('Failed to fetch test results. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSuite = (suite) => {
    setSelectedSuite(suite);
  };

  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString();
    } catch (err) {
      return timestamp;
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 0.001) {
      return `${(seconds * 1000).toFixed(2)}ms`;
    } else if (seconds < 1) {
      return `${(seconds * 1000).toFixed(0)}ms`;
    } else if (seconds < 60) {
      return `${seconds.toFixed(2)}s`;
    } else {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    }
  };

  const getStatusClass = (status) => {
    switch (status?.toUpperCase()) {
      case 'PASSED': return 'status-passed';
      case 'FAILED': return 'status-failed';
      case 'SKIPPED': return 'status-skipped';
      case 'RUNNING': return 'status-running';
      default: return '';
    }
  };

  const renderSuitesList = () => {
    if (testSuites.length === 0) {
      return <div className="no-suites">No test suites available</div>;
    }

    return (
      <div className="test-suites-list">
        <h3>Test Suites</h3>
        <div className="suites-list">
          {testSuites.map(suite => (
            <div 
              key={suite.id} 
              className={`suite-item ${selectedSuite && selectedSuite.id === suite.id ? 'selected' : ''} ${getStatusClass(suite.status)}`}
              onClick={() => handleSelectSuite(suite)}
            >
              <div className="suite-name">{suite.name}</div>
              <div className="suite-status">{suite.status}</div>
              <div className="suite-summary">
                {suite.summary.total} tests 
                {suite.summary.passed > 0 && <span className="passed"> {suite.summary.passed} passed</span>}
                {suite.summary.failed > 0 && <span className="failed"> {suite.summary.failed} failed</span>}
                {suite.summary.skipped > 0 && <span className="skipped"> {suite.summary.skipped} skipped</span>}
              </div>
              <div className="suite-time">{formatTimestamp(suite.start_time)}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTestDetails = () => {
    if (!selectedSuite) return null;

    return (
      <div className="test-details">
        <div className="test-suite-header">
          <h3>{selectedSuite.name}</h3>
          <div className={`suite-status-badge ${getStatusClass(selectedSuite.status)}`}>
            {selectedSuite.status}
          </div>
        </div>

        <div className="test-suite-info">
          <div className="info-item">
            <span className="info-label">Start Time:</span>
            <span className="info-value">{formatTimestamp(selectedSuite.start_time)}</span>
          </div>
          {selectedSuite.end_time && (
            <div className="info-item">
              <span className="info-label">End Time:</span>
              <span className="info-value">{formatTimestamp(selectedSuite.end_time)}</span>
            </div>
          )}
          <div className="info-item">
            <span className="info-label">Duration:</span>
            <span className="info-value">{formatDuration(selectedSuite.summary.duration)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Total Tests:</span>
            <span className="info-value">{selectedSuite.summary.total}</span>
          </div>
        </div>

        <div className="test-results-summary">
          <div className="summary-item passed">
            <div className="summary-count">{selectedSuite.summary.passed}</div>
            <div className="summary-label">PASSED</div>
          </div>
          <div className="summary-item failed">
            <div className="summary-count">{selectedSuite.summary.failed}</div>
            <div className="summary-label">FAILED</div>
          </div>
          <div className="summary-item skipped">
            <div className="summary-count">{selectedSuite.summary.skipped}</div>
            <div className="summary-label">SKIPPED</div>
          </div>
        </div>

        {selectedSuite.tests && selectedSuite.tests.length > 0 ? (
          <div className="tests-table-container">
            <table className="tests-table">
              <thead>
                <tr>
                  <th>Test Name</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {selectedSuite.tests.map((test, index) => (
                  <tr key={index} className={getStatusClass(test.status)}>
                    <td>{test.name}</td>
                    <td>{test.status}</td>
                    <td>{formatDuration(test.duration)}</td>
                    <td>
                      {test.message && (
                        <details>
                          <summary>View Message</summary>
                          <pre>{test.message}</pre>
                        </details>
                      )}
                      {test.metadata && Object.keys(test.metadata).length > 0 && (
                        <details>
                          <summary>View Metadata</summary>
                          <pre>{JSON.stringify(test.metadata, null, 2)}</pre>
                        </details>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-tests">No test results available for this suite</div>
        )}
      </div>
    );
  };

  return (
    <div className="test-results">
      <h2>Test Results</h2>
      
      {loading && <div className="loading">Loading test data...</div>}
      {error && <div className="error">{error}</div>}
      
      {!loading && !error && (
        <div className="test-results-container">
          <div className="test-results-sidebar">
            {renderSuitesList()}
            <div className="refresh-controls">
              <button onClick={fetchTestSuites}>Refresh Tests</button>
            </div>
          </div>
          <div className="test-results-content">
            {renderTestDetails()}
          </div>
        </div>
      )}
    </div>
  );
};

export default TestResults; 