import { useState, useEffect } from 'react';


function App() {
  const [message, setMessage] = useState('Loading...');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Test backend connection
    const testBackend = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/test', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include' // Important for cookies, authorization headers with HTTPS
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setMessage('Backend is running!');
        setData(result);
        setError(null);
      } catch (error) {
        let errorMsg = `Error connecting to backend: ${error.message}\n`;
        errorMsg += 'Please make sure the backend server is running on http://localhost:5000';
        setMessage('Backend connection failed');
        setError(errorMsg);
        console.error('Backend connection error:', error);
      }
    };

    testBackend();
  }, []);

  return (
    <div className="container">
      <h1>Ranger Rental - Backend Test</h1>
      <div>
        <p><strong>Status:</strong> {message}</p>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {data && (
          <div>
            <h2>Backend Response:</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
