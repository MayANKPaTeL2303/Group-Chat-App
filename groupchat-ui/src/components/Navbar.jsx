import React from 'react';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <h2 className="nav-logo">GroupChat</h2>
        <ul className="nav-links">
          <li><a href="/">Home</a></li>
          <li><a href="https://mayankpatel2303.github.io/">View My Site</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
