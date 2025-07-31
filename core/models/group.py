from django.db import models
from .user import UserAccount
import uuid

class Group(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='owned_groups')
    members = models.ManyToManyField(UserAccount, related_name='groups_in')
    people_count = models.IntegerField()
    duration_days = models.IntegerField()
    preferences = models.TextField(blank=True)
    restrictions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    high_consume = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=10, unique=True, blank=True)
    description = models.TextField( blank=True,
        help_text="Descripción libre del plan del grupo. Por ejemplo: lo que quieren comer cada día o el tipo de evento"
    )

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
