from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs

    def get_or_create(self, user1, user2):
        # Ensure user1.id < user2.id to avoid duplicate threads
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        thread, created = self.get_queryset().get_or_create(
            first_person=user1, second_person=user2
        )
        return thread, created

class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_thread_first')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']

class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)