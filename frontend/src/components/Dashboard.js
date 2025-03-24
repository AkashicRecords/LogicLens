import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SystemMetrics from './SystemMetrics';
import LogViewer from './LogViewer';
import TestResults from './TestResults';
import './Dashboard.css';

// Change API URL to use port 8000
const API_BASE_URL = 'http://localhost:8000/api';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('metrics');
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE_URL}/metrics`);
        setMetrics(response.data.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching metrics:', err);
        setError('Failed to fetch system metrics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, []);

  // ... existing code ...
}

export default Dashboard; 