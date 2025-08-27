import random
import string
import logging
import json
from typing import Dict, List, Optional
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.conf import settings
from django.db import transaction
from django.core.paginator import Paginator
from .models import Room, Message
import time

# Configure logging
logger = logging.getLogger(__name__)

# Constants
ONLINE_USER_TIMEOUT = 300  # 5 minutes
ROOM_CODE_LENGTH = 8
MAX_ROOM_CODE_ATTEMPTS = 10
CACHE_TIMEOUT = 300
ROOMS_PER_PAGE = 10


try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.chains.summarize import load_summarize_chain
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("Langchain dependencies not available. Chat summarization will be disabled.")
    LANGCHAIN_AVAILABLE = False


class OnlineUserTracker:
    #Handles online user tracking with improved error handling and cleanup.
    @staticmethod
    def _get_cache_key(room_code: str) -> str:
        return f'online_users_{room_code}'
    
    @staticmethod
    def mark_user_online(room_code: str, username: str) -> bool:
        """Mark a user as online in a specific room."""
        try:
            if not room_code or not username:
                return False
                
            key = OnlineUserTracker._get_cache_key(room_code)
            online_users = cache.get(key, {})
            online_users[username] = time.time()
            cache.set(key, online_users, timeout=CACHE_TIMEOUT)
            return True
        except Exception as e:
            logger.error(f"Error marking user {username} online in room {room_code}: {e}")
            return False
    
    @staticmethod
    def get_online_users(room_code: str) -> List[str]:
        """Get list of currently online users in a room."""
        try:
            if not room_code:
                return []
                
            key = OnlineUserTracker._get_cache_key(room_code)
            online_users = cache.get(key, {})
            
            if not online_users:
                return []
            
            now = time.time()
            # Remove inactive users
            active_users = {
                username: timestamp 
                for username, timestamp in online_users.items() 
                if now - timestamp < ONLINE_USER_TIMEOUT
            }
            
            # Update cache with cleaned data
            if len(active_users) != len(online_users):
                cache.set(key, active_users, timeout=CACHE_TIMEOUT)
            
            return list(active_users.keys())
        except Exception as e:
            logger.error(f"Error getting online users for room {room_code}: {e}")
            return []
    
    @staticmethod
    def remove_user(room_code: str, username: str) -> bool:
        """Remove a specific user from online tracking."""
        try:
            if not room_code or not username:
                return False
                
            key = OnlineUserTracker._get_cache_key(room_code)
            online_users = cache.get(key, {})
            
            if username in online_users:
                del online_users[username]
                cache.set(key, online_users, timeout=CACHE_TIMEOUT)
            
            return True
        except Exception as e:
            logger.error(f"Error removing user {username} from room {room_code}: {e}")
            return False


class RoomManager:
    """Handles room creation and management."""
    
    @staticmethod
    def generate_unique_code(length: int = ROOM_CODE_LENGTH) -> Optional[str]:
        """Generate a unique room code with retry logic."""
        for attempt in range(MAX_ROOM_CODE_ATTEMPTS):
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=length
            ))
            if not Room.objects.filter(code=code).exists():
                return code
        
        logger.error("Failed to generate unique room code after maximum attempts")
        return None
    
    @staticmethod
    def create_room_with_user(username: str,room_name: str) -> Optional[Room]:
        """Create a new room and add the user to it."""
        try:
            with transaction.atomic():
                code = RoomManager.generate_unique_code()
                if not code:
                    return None
                
                room = Room.objects.create(
                    code=code,
                    name=room_name if room_name else "Untitled Room"
                )
                user, created = User.objects.get_or_create(username=username)
                room.users.add(user)
                
                logger.info(f"Created room {code} with user {username}")
                return room
        except Exception as e:
            logger.error(f"Error creating room for user {username}: {e}")
            return None
    
    @staticmethod
    def add_user_to_room(room_code: str, username: str) -> bool:
        """Add a user to an existing room."""
        try:
            with transaction.atomic():
                room = Room.objects.get(code=room_code)
                user, created = User.objects.get_or_create(username=username)
                
                if not room.users.filter(username=username).exists():
                    room.users.add(user)
                
                logger.info(f"Added user {username} to room {room_code}")
                return True
        except Room.DoesNotExist:
            logger.warning(f"Attempted to add user {username} to non-existent room {room_code}")
            return False
        except Exception as e:
            logger.error(f"Error adding user {username} to room {room_code}: {e}")
            return False


class ChatSummarizer:
    # Handles chat summarization using Langchain and Gemini.
    @staticmethod
    def summarize_room_chat(room_code: str) -> Dict:
        """Summarize chat messages for a room."""
        if not LANGCHAIN_AVAILABLE:
            return {
                'error': 'Chat summarization feature is not available',
                'status': 503
            }
        
        if not room_code:
            return {'error': 'room_code is required', 'status': 400}
        
        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            return {'error': 'Room not found', 'status': 404}
        
        messages = room.messages.order_by('timestamp')
        if not messages.exists():
            return {'error': 'No messages found for this room', 'status': 404}
        
        try:
            # Prepare chat text
            chat_text = "\n".join(
                f"{msg.username}: {msg.content}" 
                for msg in messages
            )
            
            # Create Langchain Document
            document = Document(page_content=chat_text)
            
            # Set up the LLM
            llm = ChatGoogleGenerativeAI(
                google_api_key=settings.GEMINI_API_KEY,
                model="gemini-1.5-flash",
                max_output_tokens=150,
                temperature=0.3,
                top_p=0.95
            )
            
            chain = load_summarize_chain(llm, chain_type="stuff")
            summary = chain.run([document])
            
            logger.info(f"Generated summary for room {room_code}")
            return {'summary': summary.strip(), 'status': 200}
            
        except Exception as e:
            logger.error(f"Error generating summary for room {room_code}: {e}")
            return {'error': 'Failed to generate summary', 'status': 500}


# View Functions
@require_GET
def home(request):
    """Render the home page with available rooms."""
    # Get all public rooms with pagination
    rooms = Room.objects.filter(is_public=True).order_by('-created_at')
    
    # Add online user count to each room
    rooms_with_online = []
    for room in rooms:
        online_users = OnlineUserTracker.get_online_users(room.code)
        rooms_with_online.append({
            'room': room,
            'online_count': len(online_users),
            'online_users': online_users
        })
    
    # Paginate rooms
    paginator = Paginator(rooms_with_online, ROOMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_rooms': rooms.count()
    }
    
    return render(request, 'chat/home.html', context)


@require_GET
def create_room(request):
    """Create a new chat room."""
    username = request.GET.get('username', '').strip()
    room_name = request.GET.get('room_name', '').strip()
    
    if not username:
        return redirect('home')
    
    # Validate username
    if len(username) > 150: 
        return render(request, 'chat/home.html', {
            'error': 'Username too long'
        })
    
    # Validate room name
    if room_name and len(room_name) > 200:
        return render(request, 'chat/home.html', {
            'error': 'Room name too long (max 200 characters)'
        })
    
    room = RoomManager.create_room_with_user(username, room_name)
    if not room:
        return render(request, 'chat/home.html', {
            'error': 'Failed to create room. Please try again.'
        })
    
    return redirect(f'/chat/{room.code}/?username={username}')


@require_http_methods(["GET", "POST"])
def join_room(request):
    if request.method == 'GET':
        return render(request, 'chat/join.html')
    
    code = request.POST.get('room_code', '').strip().upper()
    username = request.POST.get('username', '').strip()
    
    # Validation
    if not code or not username:
        return render(request, 'chat/join.html', {
            'error': 'Room code and username are required'
        })
    
    if len(username) > 150:
        return render(request, 'chat/join.html', {
            'error': 'Username too long'
        })
    
    # Check if room exists and add user
    try:
        room = Room.objects.get(code=code)
    except Room.DoesNotExist:
        return render(request, 'chat/join.html', {
            'error': 'Invalid room code'
        })
    
    if not RoomManager.add_user_to_room(code, username):
        return render(request, 'chat/join.html', {
            'error': 'Failed to join room. Please try again.'
        })
    
    return redirect(f'/chat/{code}/?username={username}')


@require_GET
def chat_room(request, room_code):
    """Render the chat room interface."""
    room_code = room_code.upper().strip()
    username = request.GET.get('username', '').strip()
    
    if not username:
        return redirect('home')
    
    try:
        room = Room.objects.get(code=room_code)
    except Room.DoesNotExist:
        return render(request, 'chat/error.html', {
            'error': 'Room does not exist'
        })
    
    # Ensure user is added to room
    RoomManager.add_user_to_room(room_code, username)
    
    # Mark user as online
    OnlineUserTracker.mark_user_online(room_code, username)
    online_users = OnlineUserTracker.get_online_users(room_code)
    
    context = {
        'room_code': room_code,
        'room_name': room.get_display_name(),
        'username': username,
        'user_count': room.users.count(),
        'online_users': online_users,
        'room_created': room.created_at,
    }
    
    return render(request, 'chat/chatroom.html', context)

@require_GET
def browse_rooms(request):
    """Browse all available public rooms."""
    rooms = Room.objects.filter(is_public=True).order_by('-created_at')
    
    # Add online user count to each room
    rooms_with_online = []
    for room in rooms:
        online_users = OnlineUserTracker.get_online_users(room.code)
        rooms_with_online.append({
            'room': room,
            'online_count': len(online_users),
            'online_users': online_users,
            'message_count': room.messages.count()
        })
    
    # Paginate rooms
    paginator = Paginator(rooms_with_online, ROOMS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_rooms': rooms.count()
    }
    
    return render(request, 'chat/browse_rooms.html', context)

@csrf_exempt
@require_GET
def summarize_chat(request):
    """Generate a summary of chat messages for a room."""
    room_code = request.GET.get('room_code', '').strip()
    
    result = ChatSummarizer.summarize_room_chat(room_code)
    status = result.pop('status', 200)
    
    return JsonResponse(result, status=status)


@csrf_exempt
@require_POST
def update_user_activity(request):
    """Update user's online status."""
    room_code = request.POST.get('room_code', '').strip()
    username = request.POST.get('username', '').strip()
    
    if not room_code or not username:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    success = OnlineUserTracker.mark_user_online(room_code, username)
    
    if success:
        online_users = OnlineUserTracker.get_online_users(room_code)
        return JsonResponse({'online_users': online_users})
    else:
        return JsonResponse({'error': 'Failed to update activity'}, status=500)


@require_GET
def get_room_info(request, room_code):
    """Get basic information about a room."""
    try:
        room = get_object_or_404(Room, code=room_code.upper())
        online_users = OnlineUserTracker.get_online_users(room_code)
        
        return JsonResponse({
            'room_code': room.code,
            'user_count': room.users.count(),
            'online_count': len(online_users),
            'online_users': online_users,
            'created_at': room.created_at.isoformat(),
        })
    except Exception as e:
        logger.error(f"Error getting room info for {room_code}: {e}")
        return JsonResponse({'error': 'Failed to get room information'}, status=500)
    

def _parse_json_request(request) -> tuple:
    """Helper function to parse JSON request body."""
    try:
        data = json.loads(request.body)
        return data, None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return None, JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error parsing request body: {e}")
        return None, JsonResponse({'error': 'Bad request'}, status=400)