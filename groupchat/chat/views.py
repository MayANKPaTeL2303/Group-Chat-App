import random
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
from django.conf import settings

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document

@csrf_exempt
def summarize_chat(request):
    room_code = request.GET.get('room_code')
    if not room_code:
        return JsonResponse({'error': 'room_code is required'}, status=400)
    
    #Fetch chat history
    messages = Message.objects.filter(room_code=room_code).order_by('timestamp')
    if not messages.exists():
        return JsonResponse({'error': 'No messages found for this room'}, status=404)
    
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

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

rooms = set()  

def home(request):
    return render(request, 'chat/home.html')

def create_room(request):
    code = generate_code()
    rooms.add(code)
    username = request.GET.get('username', '')
    return redirect(f'/chat/{code}/?username={username}')

def join_room(request):
    if request.method == 'POST':
        code = request.POST.get('room_code')
        username = request.POST.get('username', '')
        if code in rooms:
            return redirect(f'/chat/{code}/?username={username}')
        # else:
        return render(request, 'chat/join.html', {'error': 'Invalid Room Code'})
    return render(request, 'chat/join.html')


def chat_room(request, room_code):
    if room_code not in rooms:
        return HttpResponse("Room does not exist.")

    username = request.GET.get('username', '')
    if not username:
        return redirect('home')

    return render(request, 'chat/chatroom.html', {
        'room_code': room_code,
        'username': username
    })

