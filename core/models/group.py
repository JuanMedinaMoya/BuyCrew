from django.db import models
from .user import UserAccount

class Group(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='grupos_creados')
    users = models.ManyToManyField(UserAccount, related_name='grupos')
    people_count = models.IntegerField()
    duration_days = models.IntegerField()
    preferences = models.TextField(blank=True)
    restrictions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
