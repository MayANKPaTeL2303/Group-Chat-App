import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Room,Message
from django.conf import settings
from django.core.cache import cache
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document

#Logic to track the online users

def mark_user_online(room_code,username):
    key = f'online_{room_code}'
    online_users = cache.get(key, {})
    online_users[username] = time.time()
    cache.set(key, online_users, timeout=300)  # Store for 5 minutes

def get_online_users(room_code):
    key = f'online_{room_code}'
    online_users = cache.get(key, {})
    now = time.time()
    # Remove users who have been inactive for more than 5 minutes
    online_users = {u: t for u,t in online_users.items() if now - t < 300}
    cache.set(key, online_users, timeout=300)
    return list(online_users.keys())

@csrf_exempt
def summarize_chat(request):
    room_code = request.GET.get('room_code')
    if not room_code:
        return JsonResponse({'error': 'room_code is required'}, status=400)
    
    try: 
        room = Room.objects.get(code=room_code)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'},status=404)
    
    messages = room.messages.order_by('timestamp')
    if not messages.exists():
        return JsonResponse({'error': 'No messages found for this room'}, status=404)



    # #Fetch chat history (Old Logic)
    # messages = Message.objects.filter(room_code=room_code).order_by('timestamp')
    # if not messages.exists():
    #     return JsonResponse({'error': 'No messages found for this room'}, status=404)
    
    chat_text = "\n".join(f"{msg.username}: {msg.content}" for msg in messages)

    try: 
        #Create Langchain Document
        document = Document(page_content=chat_text)
        
        # Set up the LLM
        llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GEMINI_API_KEY,
            model="gemini-1.5-flash",
            max_output_tokens=100,
            temperature=0.2,
            top_p=0.95
        )

        # Load the summarization chain
        chain = load_summarize_chain(llm,chain_type="stuff")

        # Run Summarization
        summary = chain.run([document])

        return JsonResponse({'summary': summary.strip()})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# def generate_code(length=6): -> OLD LOGIC
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_code(length=6):   
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits,k=length))
        if not Room.objects.filter(code=code).exists():
            return code

# rooms = set()  OLD LOGIC -  In-memory storage for room codes

def home(request):
    return render(request, 'chat/home.html')

def create_room(request):
    username = request.GET.get('username', '')
    if(not username):
        return redirect('home')
    
    code = generate_code()
    room = Room.objects.create(code=code)

    # Auto-create user if not exists (for demo purposes)
    user, _ = User.objects.get_or_create(username=username)
    room.users.add(user)

    return redirect(f'/chat/{code}/?username={username}')

def join_room(request):
    if request.method == 'POST':
        code = request.POST.get('room_code')
        username = request.POST.get('username', '')

        try:
            room = Room.objects.get(code=code)
        except Room.DoesNotExist:
            return render(request, 'chat/join.html', {'error': 'Invalid Room Code'})

        user, _ = User.objects.get_or_create(username=username)
        room.users.add(user)

        return redirect(f'/chat/{code}/?username={username}')
    
    return render(request, 'chat/join.html')


def chat_room(request, room_code):

    try:
        room = Room.objects.get(code=room_code)
    except Room.DoesNotExist:
        return HttpResponse("Room does not exist.")

    # if room_code not in rooms: -> OLD LOGIC
    #     return HttpResponse("Room does not exist.")

    username = request.GET.get('username', '')
    if not username:
        return redirect('home')
    
    if not room.users.filter(username=username).exists():
        user, _ = User.objects.get_or_create(username=username)
        room.users.add(user)
    
    #Mark the user as online
    mark_user_online(room_code, username)
    online_users = get_online_users(room_code)

    return render(request, 'chat/chatroom.html', {
        'room_code': room_code,
        'username': username,
        'user_count': room.user_count(),
        'online_users': online_users,
    })

