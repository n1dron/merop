from django.contrib import admin
from events import views as event_views
from django.urls import path
from users import views as user_views


urlpatterns = [
    path('', event_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('login/', user_views.user_login, name='login'),
    path('logout/', user_views.user_logout, name='logout'),
    path('events/', event_views.event_list, name='event_list'),
    path('events/<int:pk>/', event_views.event_detail, name='event_detail'),
    path('teams/', event_views.team_list, name='team_list'),
    path('teams/<int:team_id>/join/', event_views.create_participation_request, name='join_team'),
    path('teams/<int:pk>/', event_views.TeamDetailView.as_view(), name='team_detail'),
    path('profile/', user_views.profile, name='profile'),
    path('requests/', event_views.ParticipationRequestList.as_view(), name='request_list'),
    path('requests/<int:pk>/', event_views.ProcessRequestView.as_view(), name='process_request'),
    path('teams/add/', event_views.TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/edit/', event_views.TeamUpdateView.as_view(), name='team_update'),
    path('teams/<int:pk>/delete/', event_views.TeamDeleteView.as_view(), name='team_delete'),
    path('events/add/', event_views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', event_views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', event_views.EventDeleteView.as_view(), name='event_delete'),
    path('teacher/', event_views.TeacherDashboardView.as_view(), name='teacher_dashboard'),
]