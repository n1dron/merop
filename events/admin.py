from django.contrib import admin
from django.db.models import Count
from .models import SportType, Event, Team, ParticipationRequest

@admin.register(SportType)
class SportTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'participant_count')
    
    def participant_count(self, obj):
        return obj.teams.aggregate(total=Count('members'))['total']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport_type', 'captain')

@admin.register(ParticipationRequest)
class ParticipationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'status', 'created_at')
    list_filter = ('status',)