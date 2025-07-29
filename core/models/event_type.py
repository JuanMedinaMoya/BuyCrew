from django.db import models

class EventType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    alcoholic = models.BooleanField(default=False)
    beer_friendly = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nam