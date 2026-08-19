import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError('');
  };

  const handleAnalyze = async () => {
    if (!file) { setError('Please select a PDF file first!'); return; }
    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('resume', file);
    try {
      const res = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setError('Could not connect to backend. Make sure Flask is running.');
    }
    setLoading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 75) return '#22c55e';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="app">
      <div className="header">
        <h1>AI Resume Analyzer</h1>
        <p>Upload your resume and get instant AI-powered feedback</p>
      </div>

      <div className="upload-box">
        <input type="file" accept=".pdf" onChange={handleFileChange} id="fileInput" />
        <label htmlFor="fileInput" className="file-label">
          {file ? file.name : 'Click to upload your Resume (PDF only)'}
        </label>
        <button onClick={handleAnalyze} disabled={loading} className="analyze-btn">
          {loading ? 'Analyzing...' : 'Analyze Resume'}
        </button>
        {error && <p className="error">{error}</p>}
      </div>

      {result && (
        <div className="results">
          <div className="score-card">
            <h2>ATS Score</h2>
            <div className="score" style={{ color: getScoreColor(result.score) }}>
              {result.score}/100
            </div>
            <p>Word Count: {result.word_count} words</p>
          </div>

          <div className="grid">
            <div className="card">
              <h3>✅ Skills Found ({result.found_skills.length})</h3>
              <div className="tags">
                {result.found_skills.map((s, i) => (
                  <span key={i} className="tag green">{s}</span>
                ))}
              </div>
            </div>

            <div className="card">
              <h3>❌ Skills Missing</h3>
              <div className="tags">
                {result.missing_skills.map((s, i) => (
                  <span key={i} className="tag red">{s}</span>
                ))}
              </div>
            </div>

            <div className="card">
              <h3>📋 Sections Found</h3>
              <div className="tags">
                {result.found_sections.map((s, i) => (
                  <span key={i} className="tag green">{s}</span>
                ))}
              </div>
            </div>

            <div className="card">
              <h3>💡 Suggestions</h3>
              <ul>
                {result.suggestions.length === 0
                  ? <li>Great job! No major issues found.</li>
                  : result.suggestions.map((s, i) => <li key={i}>{s}</li>)
                }
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;