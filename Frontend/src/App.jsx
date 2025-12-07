
// Minimal App Component for testing
function App() {
  return (
    <div style={{
      padding: '40px',
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <h1 style={{ color: '#1976d2' }}>✅ Frontend is Working!</h1>
      <p>If you can see this, React is running correctly.</p>

      <div style={{
        background: '#f5f5f5',
        padding: '20px',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>System Status</h2>
        <ul>
          <li>✅ React: Running</li>
          <li>✅ Vite: Running</li>
          <li>✅ Port 3000: Active</li>
        </ul>
      </div>

      <div style={{
        background: '#e3f2fd',
        padding: '20px',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>Next Steps</h2>
        <ol>
          <li>Make sure backend is running on port 8000</li>
          <li>Check that all dependencies are installed</li>
          <li>Verify API keys are set in Backend/.env</li>
        </ol>
      </div>

      <div style={{ marginTop: '40px', color: '#666', fontSize: '14px' }}>
        <p>Live Data RAG System v1.0.0</p>
        <p>If you see this page, the frontend is working correctly!</p>
      </div>
    </div>
  );
}

export default App;