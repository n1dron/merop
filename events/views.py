from django.db.models import Q
from .forms import EventFilterForm
from django.shortcuts import render, get_object_or_404
from .models import Event, Team, ParticipationRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .mixins import TeacherRequiredMixin
from django.views.generic import ListView, UpdateView
from django.urls import reverse
from django.urls import reverse_lazy
from django.db.models import Count
from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.views import View
from .models import ParticipationRequest
from django.views.generic import DetailView
from django.views.generic import ListView, UpdateView, CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import Event
from .forms import EventForm
from .mixins import TeacherRequiredMixin
from django.utils import timezone


def event_list(request):
    events = Event.objects.all()
    
    # Фильтрация
    form = EventFilterForm(request.GET)
    if form.is_valid():
        sport_type = form.cleaned_data.get('sport_type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if sport_type:
            events = events.filter(sport_type=sport_type)
        if date_from:
            events = events.filter(date__gte=date_from)
        if date_to:
            events = events.filter(date__lte=date_to)
    
    return render(request, 'events/event_list.html', {
        'events': events,
        'form': form
    })

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})

def team_list(request):
    teams = Team.objects.all()
    return render(request, 'events/team_list.html', {'teams': teams})

def home(request):
    return render(request, 'events/home.html')  

@login_required
def create_participation_request(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    
    # Проверяем, не подавал ли пользователь заявку ранее
    existing_request = ParticipationRequest.objects.filter(
        user=request.user,
        team=team
    ).exists()
    
    if existing_request:
        messages.warning(request, 'Вы уже подавали заявку в эту команду')
    else:
        ParticipationRequest.objects.create(
            user=request.user,
            team=team,
            status='pending'
        )
        messages.success(request, 'Заявка успешно подана')
    
    return redirect('team_list')

class ParticipationRequestList(TeacherRequiredMixin, ListView):
    model = ParticipationRequest
    template_name = 'events/request_list.html'
    context_object_name = 'requests'
    
    def get_queryset(self):
        return ParticipationRequest.objects.filter(status='pending')

class ProcessRequestView(TeacherRequiredMixin, UpdateView):
    model = ParticipationRequest
    fields = ['status']
    template_name = 'events/process_request.html'
    success_url = reverse_lazy('request_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.status == 'approved':
            self.object.team.members.add(self.object.user)
        return response
    
class TeamCreateView(TeacherRequiredMixin, CreateView):
    model = Team
    fields = ['name', 'sport_type', 'captain', 'required_players']
    template_name = 'events/team_form.html'
    
    def get_success_url(self):
        return reverse('team_list')

class TeamUpdateView(TeacherRequiredMixin, UpdateView):
    model = Team
    fields = ['name', 'sport_type', 'captain', 'required_players']
    template_name = 'events/team_form.html'
    
    def get_success_url(self):
        return reverse('team_list')

class TeamDeleteView(TeacherRequiredMixin, DeleteView):
    model = Team
    template_name = 'events/team_confirm_delete.html'
    success_url = reverse_lazy('team_list')


class EventUpdateView(TeacherRequiredMixin, UpdateView):
    model = Event
    fields = ['title', 'description', 'sport_type', 'date', 'location']
    template_name = 'events/event_form.html'
    
    def get_success_url(self):
        return reverse('event_list')

class EventDeleteView(TeacherRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

class EventDashboardView(TeacherRequiredMixin, DetailView):
    model = Event
    template_name = 'events/event_dashboard.html'
    

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['participants'] = self.object.teams.all().annotate(
        num_members=Count('members')
    )  
    return context

class BulkApproveView(TeacherRequiredMixin, View):
    def post(self, request):
        selected = request.POST.getlist('selected_requests')
        
        if not selected:
            # Можно добавить сообщение об ошибке или перенаправление
            return redirect('request_list')  # Или обработка ошибки

        # Обновление статуса выбранных запросов
        ParticipationRequest.objects.filter(id__in=selected).update(status='approved')
        
        return redirect('request_list')

@method_decorator(login_required, name='dispatch')
class TeacherDashboardView(TemplateView):
    template_name = 'teacher/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher:
            return redirect('access_denied')  # Или создайте страницу с ошибкой доступа
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_requests'] = ParticipationRequest.objects.filter(status='pending').count()
        context['active_events'] = Event.objects.filter(date__gte=timezone.now()).count()
        return context
    
class EventCreateView(TeacherRequiredMixin, CreateView):

    model = Event  # Указываем модель, с которой работаем
    form_class = EventForm  # Используем кастомную форму (или можно указать fields)
    template_name = 'events/event_form.html'  # Шаблон для отображения формы
    success_url = reverse_lazy('event_list')  # Куда перенаправить после успешного создания

    def form_valid(self, form):

        form.instance.organizer = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
 
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание нового мероприятия'
        return context
