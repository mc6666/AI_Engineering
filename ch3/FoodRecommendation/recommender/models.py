from django.db import models
from django.contrib.auth.models import User


class YouTuber(models.Model):
    name = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=200)
    youtube_url = models.URLField(blank=True)
    description = models.TextField()
    style_keywords = models.CharField(max_length=300)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class FoodSuggestion(models.Model):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="suggestions"
    )
    session_key = models.CharField(max_length=40, blank=True)
    youtubers = models.ManyToManyField(YouTuber, related_name="suggestions")
    user_query = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        owner = self.user.username if self.user_id else self.session_key[:8]
        return f"{owner} — {self.created_at:%Y-%m-%d %H:%M}"
