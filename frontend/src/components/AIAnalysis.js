import React, { useState } from 'react';
import axios from 'axios';
import './AIAnalysis.css';

const AIAnalysis = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/analyze', {
        prompt: input
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
      console.error('AI Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-analysis">
      <h2>AI Analysis</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your prompt here..."
          rows="4"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="result">
          <h3>Analysis Result:</h3>
          <div className="response-content">
            {result.response ? (
              <pre>{result.response}</pre>
            ) : (
              <pre>{JSON.stringify(result, null, 2)}</pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalysis; 