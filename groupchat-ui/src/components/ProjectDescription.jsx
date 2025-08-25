import React from 'react';

function ProjectDescription() {
  return (
    <div className="project-description">
      <h2 className="section-title text-blue-600">💬 About This Project</h2>
      <div className="chat-description">
        <p>
          <strong>Real-Time Group Chat Application</strong><br />
          This is a powerful and responsive chat platform developed using the <em>Django web framework</em> along with <em>WebSockets</em> to deliver seamless real-time communication.
        </p>
        <p>
          Users can <strong>create</strong> a new chat room or <strong>join</strong> an existing one using a unique room code. Once inside a room, messages are broadcast to all participants <strong>instantly</strong>, without refreshing the page.
        </p>
        <p>
          The app uses <strong>Django Channels</strong> with <strong>Redis</strong> as a channel layer, serving as an <em>in-memory message broker</em> to ensure scalability and responsiveness.
        </p>
      </div>
    </div>
  );
}

export default ProjectDescription;
