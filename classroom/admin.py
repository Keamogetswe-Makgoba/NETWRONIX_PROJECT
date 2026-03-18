from django.contrib import admin
from .models import LiveClass

@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'grade', 'is_live', 'created_at')
    search_fields = ('title', 'topic', 'meeting_id')