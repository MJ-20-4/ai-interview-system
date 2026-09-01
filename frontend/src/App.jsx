import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [backendStatus, setBackendStatus] = useState("Not checked");
  const [loading, setLoading] = useState(false);

  const checkBackend = async () => {
    setLoading(true);

    try {
      const response = await axios.get(`${API_BASE_URL}/health`);

      if (response.data.mongodb_connected) {
        setBackendStatus("Backend and MongoDB are connected.");
      } else {
        setBackendStatus("Backend is running, but MongoDB is unavailable.");
      }
    } catch (error) {
      setBackendStatus(
        "Cannot connect to the backend. Check that FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <section className="card">
        <p className="eyebrow">PG-AGI Assignment</p>

        <h1>AI-Powered Interview System</h1>

        <p className="description">
          A role-based candidate screening platform powered by resume analysis,
          retrieval-augmented generation, and adaptive technical questions.
        </p>

        <button onClick={checkBackend} disabled={loading}>
          {loading ? "Checking..." : "Test Backend Connection"}
        </button>

        <p className="status">{backendStatus}</p>

        <div className="next-steps">
          <h2>Next implementation steps</h2>
          <ol>
            <li>Add resume upload.</li>
            <li>Add role selection.</li>
            <li>Parse PDF and text resumes.</li>
            <li>Ingest role-specific documents into ChromaDB.</li>
            <li>Generate personalized interview questions.</li>
          </ol>
        </div>
      </section>
    </main>
  );
}

export default App;
