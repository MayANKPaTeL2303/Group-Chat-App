import React, { useEffect, useRef, useState } from "react";

function ChatRoom({ roomCode, username }) {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [summary, setSummary] = useState("");
  const [loadingSummary, setLoadingSummary] = useState(false);
  const chatBoxRef = useRef(null);

  const wsUrl = `ws://${window.location.host}/ws/chat/${roomCode}/`;
  const [chatSocket, setChatSocket] = useState(null);

  // WebSocket connection
  useEffect(() => {
    const socket = new WebSocket(wsUrl);
    setChatSocket(socket);

    socket.onopen = () => console.log("✅ WebSocket connected");
    socket.onerror = (e) => console.error("❌ WebSocket error:", e);
    socket.onclose = (e) => console.warn("⚠️ WebSocket closed:", e);

    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      const timestamp = new Date(data.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });

      setMessages((prev) => [
        ...prev,
        {
          username: data.username,
          message: data.message,
          timestamp,
        },
      ]);
    };

    return () => socket.close();
  }, [wsUrl]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  // Send message
  const sendMessage = () => {
    if (message.trim() && chatSocket) {
      chatSocket.send(JSON.stringify({ message, username }));
      setMessage("");
    }
  };

  // Leave room
  const leaveRoom = () => {
    if (chatSocket) chatSocket.close();
    window.location.href = "/"; // adjust if using React Router
  };

  // Summarize chat
  const summarizeChat = async () => {
    setLoadingSummary(true);
    setSummary("⏳ Generating summary...");

    try {
      const response = await fetch(`/summarize?room_code=${roomCode}`);
      const data = await response.json();

      if (data.summary) {
        setSummary(data.summary);
      } else if (data.error) {
        setSummary(`❌ ${data.error}`);
      }
    } catch (err) {
      setSummary(`❌ Error: ${err.message}`);
    } finally {
      setLoadingSummary(false);
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <nav className="navbar">
        <div className="nav-container">
          <h2 className="nav-logo">GroupChat</h2>
          <ul className="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="https://github.com/MayANKPaTeL2303">GitHub</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
        </div>
      </nav>

      {/* Main Chat */}
      <main className="chat-main">
        <h2 className="chat-header">
          Room <span className="room-code">{roomCode}</span>
        </h2>
        <div className="leave-room-container">
          <button onClick={leaveRoom} className="leave-button">
            Leave Room
          </button>
        </div>

        <div className="chat-content-wrapper">
          {/* Chat Messages */}
          <div className="chat-box-container">
            <div id="chat-box" className="chat-box" ref={chatBoxRef}>
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`bubble-row ${
                    msg.username === username ? "right" : "left"
                  }`}
                >
                  <div
                    className={`bubble ${
                      msg.username === username ? "mine" : "theirs"
                    }`}
                  >
                    <div className="username">{msg.username}</div>
                    <div className="message">{msg.message}</div>
                    <div className="timestamp">{msg.timestamp}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Input Area */}
            <div className="input-area">
              <input
                type="text"
                placeholder="Type your message..."
                className="chat-input"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              />
              <button onClick={sendMessage} className="send-button">
                Send
              </button>
            </div>
          </div>

          {/* Summary Box */}
          <div className="summary-box-container">
            <h3 className="summary-title">Chat Summary</h3>
            <div id="summary-content" className="summary-content">
              {summary ? (
                <p>{summary}</p>
              ) : (
                <p className="placeholder">
                  Click the button below to summarize this chat.
                </p>
              )}
            </div>
            <button
              onClick={summarizeChat}
              className="summary-button"
              disabled={loadingSummary}
            >
              {loadingSummary ? "Summarizing..." : "Summarize Chat"}
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>© 2025 GroupChat App | Built by Mayank Patel</p>
      </footer>
    </div>
  );
}

export default ChatRoom;
