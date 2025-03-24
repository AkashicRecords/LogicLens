import React from 'react';
import './App.css';
import AIAnalysis from './components/AIAnalysis';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Logger Dashboard</h1>
      </header>
      <main>
        <p>Welcome to the AI Logger Dashboard</p>
        <p>Backend is running at http://localhost:5000</p>
        <AIAnalysis />
      </main>
    </div>
  );
}

export default App; 