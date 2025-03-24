import React, { useState } from 'react';
import './App.css';
import AIAnalysis from './components/AIAnalysis';
import LogViewer from './components/LogViewer';
import TestResults from './components/TestResults';
import SystemMonitoring from './components/SystemMonitoring';

function App() {
  const [activeTab, setActiveTab] = useState('analysis');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'logs':
        return <LogViewer />;
      case 'tests':
        return <TestResults />;
      case 'monitoring':
        return <SystemMonitoring />;
      case 'analysis':
      default:
        return <AIAnalysis />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>LogicLens Dashboard</h1>
      </header>
      
      <nav className="App-nav">
        <button 
          className={activeTab === 'analysis' ? 'active' : ''} 
          onClick={() => setActiveTab('analysis')}
        >
          AI Analysis
        </button>
        <button 
          className={activeTab === 'logs' ? 'active' : ''} 
          onClick={() => setActiveTab('logs')}
        >
          Logs
        </button>
        <button 
          className={activeTab === 'tests' ? 'active' : ''} 
          onClick={() => setActiveTab('tests')}
        >
          Test Results
        </button>
        <button 
          className={activeTab === 'monitoring' ? 'active' : ''} 
          onClick={() => setActiveTab('monitoring')}
        >
          System Monitoring
        </button>
      </nav>
      
      <main className="App-content">
        {renderTabContent()}
      </main>
      
      <footer className="App-footer">
        <p>LogicLens v0.1.0 | Backend API: http://localhost:5000/api</p>
      </footer>
    </div>
  );
}

export default App; 