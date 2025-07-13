from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Thread, ChatMessage

User = get_user_model()

@login_required
def chat_room(request, username):
    other_user = get_object_or_404(User, username=username)
    thread, _ = Thread.objects.get_or_create(request.user, other_user)
    messages = ChatMessage.objects.filter(thread=thread).order_by('timestamp')
    context = {
        'thread': thread,
        'other_user': other_user,
        'messagesList': messages
    }
    return render(request, 'chat/chat_room.html', context)

