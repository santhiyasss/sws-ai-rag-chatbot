import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://localhost:8000/api/chat";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! I'm the SWS AI Policy Assistant. Ask me anything about company policies — leave, HR, IT security, and more.",
      sources: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await axios.post(API_URL, { question });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.data.answer,
          sources: res.data.sources || [],
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Sorry, something went wrong. Please try again.",
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-icon">S</div>
            <span>SWS AI Policy Assistant</span>
          </div>
          <span className="badge">RAG Powered</span>
        </div>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message-row ${msg.role}`}>
              {msg.role === "assistant" && <div className="avatar">AI</div>}
              <div className="bubble-wrapper">
                <div className={`bubble ${msg.role}`}>{msg.text}</div>
                {msg.sources?.length > 0 && (
                  <div className="sources">
                    <span className="sources-label">📄 Sources:</span>
                    {msg.sources.map((s, j) => (
                      <span key={j} className="source-chip">
                        {s.replace(".pdf", "")}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === "user" && <div className="avatar user-avatar">You</div>}
            </div>
          ))}
          {loading && (
            <div className="message-row assistant">
              <div className="avatar">AI</div>
              <div className="bubble assistant typing">
                <span /><span /><span />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="input-area">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about leave policy, IT security, HR guidelines..."
            rows={1}
            disabled={loading}
          />
          <button onClick={sendMessage} disabled={loading || !input.trim()}>
            {loading ? "..." : "Send"}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;