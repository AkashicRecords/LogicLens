import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SystemMonitoring.css';

const SystemMonitoring = () => {
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetchMetrics(),
      fetchHistory(),
      fetchSystemInfo()
    ]).then(() => {
      // Set up auto-refresh every 10 seconds
      const interval = setInterval(() => {
        fetchMetrics();
        // Refresh history less frequently
        if (Math.random() < 0.3) fetchHistory();
      }, 10000);
      return () => clearInterval(interval);
    });
  }, []);

  const fetchMetrics = async () => {
    setError(null);
    try {
      const response = await axios.get('http://localhost:5000/api/monitoring/metrics');
      setMetrics(response.data);
    } catch (err) {
      console.error('Error fetching metrics:', err);
      setError('Failed to fetch system metrics');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/monitoring/history', {
        params: { count: 30 }
      });
      setHistory(response.data.metrics || []);
    } catch (err) {
      console.error('Error fetching metrics history:', err);
    }
  };

  const fetchSystemInfo = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/monitoring/system');
      setSystemInfo(response.data);
    } catch (err) {
      console.error('Error fetching system info:', err);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (percent) => {
    if (percent >= 90) return '#dc3545'; // Danger
    if (percent >= 70) return '#ffc107'; // Warning
    return '#28a745'; // Good
  };

  const renderMetricCard = (title, value, unit, percent = null, icon = null) => {
    return (
      <div className="metric-card">
        {icon && <div className="metric-icon">{icon}</div>}
        <div className="metric-title">{title}</div>
        <div className="metric-value">
          {value} <span className="metric-unit">{unit}</span>
        </div>
        {percent !== null && (
          <div className="metric-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${percent}%`,
                  backgroundColor: getStatusColor(percent)
                }}
              ></div>
            </div>
            <div className="progress-text">{percent}%</div>
          </div>
        )}
      </div>
    );
  };

  const renderSystemInfo = () => {
    if (!systemInfo) return null;

    return (
      <div className="system-info-section">
        <h3>System Information</h3>
        <div className="system-info-cards">
          <div className="info-card">
            <div className="info-label">Hostname</div>
            <div className="info-value">{systemInfo.hostname}</div>
          </div>
          <div className="info-card">
            <div className="info-label">Platform</div>
            <div className="info-value">{systemInfo.platform}</div>
          </div>
          <div className="info-card">
            <div className="info-label">CPU Cores</div>
            <div className="info-value">{systemInfo.cpu_count}</div>
          </div>
          <div className="info-card">
            <div className="info-label">Total Memory</div>
            <div className="info-value">{formatBytes(systemInfo.memory_total)}</div>
          </div>
          <div className="info-card">
            <div className="info-label">Python Version</div>
            <div className="info-value">{systemInfo.python_version}</div>
          </div>
        </div>
      </div>
    );
  };

  const renderCurrentMetrics = () => {
    if (!metrics) return null;

    const systemMetrics = metrics.system;
    const appMetrics = metrics.application;

    return (
      <div className="current-metrics-section">
        <h3>Current System Metrics</h3>
        <div className="metrics-grid">
          {renderMetricCard(
            'CPU Usage',
            systemMetrics.cpu_percent,
            '%',
            systemMetrics.cpu_percent,
            '💻'
          )}
          {renderMetricCard(
            'Memory Usage',
            systemMetrics.memory_percent,
            '%',
            systemMetrics.memory_percent,
            '🧠'
          )}
          {renderMetricCard(
            'Disk Usage',
            systemMetrics.disk_percent,
            '%',
            systemMetrics.disk_percent,
            '💾'
          )}
          {renderMetricCard(
            'Memory Available',
            formatBytes(systemMetrics.memory_available),
            '',
            null,
            '📊'
          )}
          {renderMetricCard(
            'Network Sent',
            formatBytes(systemMetrics.network_bytes_sent),
            '',
            null,
            '📤'
          )}
          {renderMetricCard(
            'Network Received',
            formatBytes(systemMetrics.network_bytes_recv),
            '',
            null,
            '📥'
          )}
        </div>

        <h3>Application Metrics</h3>
        <div className="metrics-grid">
          {renderMetricCard(
            'App CPU Usage',
            appMetrics.process_cpu_percent,
            '%',
            appMetrics.process_cpu_percent,
            '⚙️'
          )}
          {renderMetricCard(
            'App Memory',
            formatBytes(appMetrics.process_memory_rss),
            '',
            null,
            '📈'
          )}
          {renderMetricCard(
            'Threads',
            appMetrics.process_threads,
            '',
            null,
            '🧵'
          )}
          {renderMetricCard(
            'Connections',
            appMetrics.process_connections,
            '',
            null,
            '🔌'
          )}
        </div>
      </div>
    );
  };

  const renderMetricsHistory = () => {
    if (history.length === 0) return null;

    // Chart data preparation would go here in a real implementation
    // For now, we'll just show a simple text representation

    return (
      <div className="metrics-history-section">
        <h3>Metrics History</h3>
        <div className="history-preview">
          <p>History data available for {history.length} data points.</p>
          <p>Latest readings:</p>
          <ul>
            {history.slice(0, 3).map((point, index) => (
              <li key={index}>
                {new Date(point.timestamp).toLocaleTimeString()}: 
                CPU {point.system.cpu_percent}%, 
                Memory {point.system.memory_percent}%, 
                Disk {point.system.disk_percent}%
              </li>
            ))}
          </ul>
          <p className="note">
            Note: In a production environment, this would display interactive charts 
            showing trends over time.
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="system-monitoring">
      <h2>System Monitoring</h2>
      
      {loading && !metrics && <div className="loading">Loading system metrics...</div>}
      {error && <div className="error">{error}</div>}
      
      {systemInfo && renderSystemInfo()}
      {metrics && renderCurrentMetrics()}
      {history.length > 0 && renderMetricsHistory()}
      
      <div className="refresh-controls">
        <button onClick={() => {
          setLoading(true);
          Promise.all([fetchMetrics(), fetchHistory()]).finally(() => setLoading(false));
        }}>
          Refresh Metrics
        </button>
      </div>
    </div>
  );
};

export default SystemMonitoring; 