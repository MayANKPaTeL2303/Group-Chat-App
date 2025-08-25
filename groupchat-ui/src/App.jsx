import React from 'react';
import Navbar from './components/Navbar';
import ProjectDescription from './components/ProjectDescription';
import ChatBox from './components/ChatBox';
import Footer from './components/Footer';
import './home.css';  // Make sure this matches your CSS path

function App() {
  return (
    <>
      <Navbar />
      <div className="flex-container">
        <ProjectDescription />
        <ChatBox />
      </div>
      <Footer />
    </>
  );
}

export default App;
