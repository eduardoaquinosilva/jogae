from django.db import models
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class FriendshipManager(models.Manager):
    def get_friends(self, user):
        friend_qs = self.get_queryset().filter(
            (Q(from_user=user) | Q(to_user=user)),
            status='ACCEPTED'
        )
        friends = []
        for friendship in friend_qs:
            if friendship.from_user == user:
                friends.append(friendship.to_user)
            else:
                friends.append(friendship.from_user)
        return friends

class Friendship(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'

    from_user = models.ForeignKey(User, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friendship_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FriendshipManager()

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"Request from {self.from_user} to {self.to_user}: {self.status}"
