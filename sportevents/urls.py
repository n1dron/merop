from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from events import views as event_views
from users import views as user_views

urlpatterns = [
    # Основные URL
    path('', event_views.home, name='home'),
    path('admin/', admin.site.urls),
    
    # Аутентификация
    path('register/', user_views.register, name='register'),
    path('login/', user_views.user_login, name='login'),
    path('logout/', user_views.user_logout, name='logout'),
    path('profile/', user_views.profile, name='profile'),
    
    # Мероприятия
    path('events/', event_views.event_list, name='event_list'),
    path('events/add/', event_views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', event_views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', event_views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', event_views.EventDeleteView.as_view(), name='event_delete'),
    
    # Команды
    path('teams/', event_views.team_list, name='team_list'),
    path('teams/add/', event_views.TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/', event_views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/edit/', event_views.TeamUpdateView.as_view(), name='team_update'),
    path('teams/<int:pk>/delete/', event_views.TeamDeleteView.as_view(), name='team_delete'),
    path('teams/<int:team_id>/join/', event_views.create_participation_request, name='join_team'),
    
    # Заявки
    path('requests/', event_views.ParticipationRequestList.as_view(), name='request_list'),
    path('requests/<int:pk>/', event_views.ProcessRequestView.as_view(), name='process_request'),
    
    # Панель преподавателя
    path('teacher/', event_views.TeacherDashboardView.as_view(), name='teacher_dashboard'),
    
]

# Добавление обработки статических файлов в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)