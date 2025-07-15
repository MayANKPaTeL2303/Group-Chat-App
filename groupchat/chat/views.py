import random
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

rooms = set()  # simple in-memory store for room codes

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
        else:
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

