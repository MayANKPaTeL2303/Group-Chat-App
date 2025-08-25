import React, { useState } from 'react';

function ChatBox() {
  const [createName, setCreateName] = useState('');
  const [joinRoomCode, setJoinRoomCode] = useState('');
  const [joinName, setJoinName] = useState('');

  const handleCreateRoom = (e) => {
    e.preventDefault();
    // TODO: Replace with actual room creation logic
    console.log('Create Room, username:', createName);
  };

  const handleJoinRoom = (e) => {
    e.preventDefault();
    // TODO: Replace with actual join room logic
    console.log('Join Room:', joinRoomCode, 'as', joinName);
  };

  return (
    <div className="chat-box">
      <h1 className="heading">🚀 Group Chat</h1>

      <div className="section-block">
        <h2 className="section-title indigo">Create Room</h2>
        <form className="form-block" onSubmit={handleCreateRoom}>
          <input
            type="text"
            name="username"
            placeholder="Enter your name"
            value={createName}
            onChange={(e) => setCreateName(e.target.value)}
            required
          />
          <button type="submit" className="create-btn">Create</button>
        </form>
      </div>

      <div className="section-block">
        <h2 className="section-title green">Join Room</h2>
        <form className="form-block" onSubmit={handleJoinRoom}>
          <input
            type="text"
            name="room_code"
            placeholder="Room Code"
            value={joinRoomCode}
            onChange={(e) => setJoinRoomCode(e.target.value)}
            required
          />
          <input
            type="text"
            name="username"
            placeholder="Enter your name"
            value={joinName}
            onChange={(e) => setJoinName(e.target.value)}
            required
          />
          <button type="submit" className="join-btn">Join</button>
        </form>
      </div>
    </div>
  );
}

export default ChatBox;
