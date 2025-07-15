# 💬 Group Messaging App (Phase 1)

A real-time group chat web application built using **Django**, **Django Channels**, **WebSockets**, **Redis**, and **Tailwind CSS**.

---

## ✅ Phase 1 Overview

### 🚪 Entry Point:
Users are greeted with two options:
1. **Create Room**
2. **Join Room**

### 🛠️ Create Room:
- A unique room code is generated automatically.
- The user is redirected to a new chat room URL containing the code.

### 🔗 Join Room:
- The user enters an existing room code.
- If valid, they are redirected to the existing room.

### 💬 Chat Room:
- Real-time messaging using WebSockets.
- All users sharing the same room code can chat live.
- Built-in username tagging and Tailwind UI for a clean and responsive design.

---

## ⚙️ Tech Stack

- **Backend**: Django + Channels + Redis
- **Frontend**: HTML, Tailwind CSS, WebSockets
- **Real-time**: Django Channels with Redis as channel layer

---

## 🔧 Running Daphne & Redis

### 🟥 1. Start Redis Server  
Make sure Redis is installed and running:

- **Windows (using Docker):**
```bash
docker run -p 6379:6379 redis
