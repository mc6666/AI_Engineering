from django.contrib import admin
from .models import YouTuber, FoodSuggestion


@admin.register(YouTuber)
class YouTuberAdmin(admin.ModelAdmin):
    list_display = ["name", "channel_name", "youtube_url"]
    search_fields = ["name", "channel_name"]


@admin.register(FoodSuggestion)
class FoodSuggestionAdmin(admin.ModelAdmin):
    list_display = ["session_key", "user_query", "created_at"]
    list_filter = ["created_at"]
    readonly_fields = ["session_key", "youtubers", "user_query", "ai_response", "created_at"]
