# Real-Time Group Chat Application

[![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)](https://www.djangoproject.com/)
[![Channels](https://img.shields.io/badge/Channels-4.3.0-blue.svg)](https://channels.readthedocs.io/)
[![Redis](https://img.shields.io/badge/Redis-Channel%20Layer-red.svg)](https://redis.io/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Real%20Time-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

A real-time group chat web application built with **Django**, **Django Channels**, **WebSockets**, **Redis**, and modern web technologies. This application enables seamless real-time communication with advanced features like AI-powered chat summarization, online user tracking, and responsive design.

## Features

### Core Functionality
- **Real-time messaging** using WebSockets and Django Channels
- **Room-based chat system** with unique room codes
- **User authentication** and session management
- **Message persistence** with SQLite database
- **Online user tracking** with Redis caching
- **Chat history** - last 20 messages loaded on join
- **System notifications** for user join/leave events

### AI-Powered Features
- **Chat Summarization** using Google's Generative AI (Gemini)
- **Intelligent conversation analysis** and insights

### User Experience
- **Modern, responsive UI** with custom CSS styling
- **Clean navigation** with branded header
- **Real-time user presence** indicators
- **Smooth animations** and transitions
- **Mobile-friendly design**

##  Architecture

### Backend Stack
- **Django 5.2.4** - Web framework
- **Django Channels 4.3.0** - WebSocket support
- **Redis** - Channel layer and caching
- **SQLite** - Database (easily configurable for PostgreSQL/MySQL)
- **ASGI** - Asynchronous server gateway interface

### Frontend Stack
- **HTML5** with Django templates
- **Custom CSS** with modern styling
- **JavaScript** for WebSocket client-side handling
- **Responsive design** principles

### AI/ML Stack
- **LangChain 0.3.27** - AI framework
- **Google Generative AI** - Chat summarization
- **LangSmith** - AI observability

## Project Structure

```
Group-Chat-Django-Channels/
├── groupchat/                 # Main Django project
│   ├── groupchat/            # Project settings
│   │   ├── settings.py       # Django configuration
│   │   ├── asgi.py          # ASGI configuration
│   │   ├── urls.py          # Main URL routing
│   │   └── wsgi.py          # WSGI configuration
│   ├── chat/                 # Chat application
│   │   ├── models.py        # Room and Message models
│   │   ├── views.py         # HTTP views and AI features
│   │   ├── consumers.py     # WebSocket consumers
│   │   ├── routing.py       # WebSocket URL routing
│   │   ├── urls.py          # HTTP URL patterns
│   │   ├── templates/       # HTML templates
│   │   │   └── chat/
│   │   │       ├── home.html      # Landing page
│   │   │       └── chatroom.html  # Chat interface
│   │   └── static/          # CSS and static files
│   ├── db.sqlite3           # SQLite database
│   ├── manage.py            # Django management script
│   └── .env                 # Environment variables
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Redis server
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Group-Chat-Django-Channels
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd groupchat
pip install -r ../requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the `groupchat` directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
GOOGLE_API_KEY=your-google-ai-api-key  # For AI features
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

### 6. Start Redis Server

**Option A: Using Docker (Recommended)**
```bash
docker run -p 6379:6379 -d redis:latest
```

**Option B: Native Installation**
- **Windows**: Download from [Redis Windows](https://github.com/microsoftarchive/redis/releases)
- **Linux**: `sudo apt-get install redis-server`

### 7. Run the Application
```bash
# Using Daphne (Production-ready ASGI server)
daphne groupchat.asgi:application

# Or using Django development server (Development only)
python manage.py runserver
```

### 8. Access the Application
Open your browser and navigate to:
- **Development**: `http://127.0.0.1:8000`
- **Daphne**: `http://127.0.0.1:8000`

## How to Use

### Creating a Chat Room
1. Visit the home page
2. Click **"Create Room"**
3. Enter your username
4. A unique room code will be generated automatically
5. Share the room code with others

### Joining a Chat Room
1. Visit the home page
2. Click **"Join Room"**
3. Enter the room code and your username
4. Start chatting in real-time!

### AI Chat Summarization
- Use the summarization endpoint: `/summarize/?room_code=YOUR_ROOM_CODE`
- Get AI-powered insights and summaries of your chat conversations

## Configuration

### Redis Configuration
The application uses Redis for:
- **Channel Layer**: WebSocket message routing
- **User Presence**: Online user tracking
- **Caching**: Performance optimization

Default Redis settings in `settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### Database Configuration
By default, the application uses SQLite. To use PostgreSQL or MySQL:

1. Install the appropriate database adapter
2. Update `DATABASES` in `settings.py`
3. Run migrations

### AI Features Configuration
To enable AI-powered chat summarization:
1. Get a Google AI API key from [Google AI Studio](https://makersuite.google.com/)
2. Add it to your `.env` file as `GOOGLE_API_KEY`
3. The summarization endpoint will be available at `/summarize/`

## Development

### Key Components

#### Models (`chat/models.py`)
- **Room**: Manages chat rooms with unique codes
- **Message**: Stores chat messages with timestamps

#### WebSocket Consumer (`chat/consumers.py`)
- **ChatConsumer**: Handles WebSocket connections
- Real-time message broadcasting
- User join/leave notifications
- Message history loading

#### Views (`chat/views.py`)
- **Home view**: Landing page with room creation/joining
- **Chat room view**: Main chat interface
- **AI summarization**: LangChain-powered chat analysis
- **Online user tracking**: Redis-based presence system

### Adding New Features
1. **Database changes**: Update models, create migrations
2. **WebSocket features**: Modify `ChatConsumer` class
3. **HTTP endpoints**: Add views and URL patterns
4. **Frontend**: Update templates and static files

## Performance & Scalability

### Current Optimizations
- **Redis channel layer** for efficient message routing
- **Connection pooling** for database operations
- **Async/await patterns** for non-blocking operations
- **Message history limiting** (last 20 messages)
- **User presence caching** with TTL

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL/MySQL instead of SQLite
- [ ] Set up Redis with persistence
- [ ] Configure HTTPS/WSS
- [ ] Set up proper logging
- [ ] Use environment variables for secrets
- [ ] Configure static file serving

### Docker Deployment
```dockerfile
# Example Dockerfile structure
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["daphne", "groupchat.asgi:application"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## API Documentation

### WebSocket API
**Connection**: `ws://localhost:8000/ws/chat/{room_code}/?username={username}`

**Message Format**:
```json
{
    "username": "user123",
    "message": "Hello, world!",
    "timestamp": "2024-01-01 12:00:00"
}
```

### HTTP Endpoints
- `GET /` - Home page
- `GET /chat/{room_code}/` - Chat room interface
- `GET /summarize/?room_code={code}` - AI chat summarization


**⭐ If you found this project helpful, please give it a star!*
