from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView, DetailView, CreateView, 
    UpdateView, DeleteView, TemplateView, View
)
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .forms import EventFilterForm, EventForm
from .models import Event, Team, ParticipationRequest
from .mixins import TeacherRequiredMixin


def event_list(request):
    events = Event.objects.all()
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
    teams = Team.objects.all().select_related('sport_type', 'captain').prefetch_related('members')
    
    for team in teams:
        team.spots_left = max(0, team.required_players - team.members.count())
    
    return render(request, 'events/team_list.html', {
        'teams': teams,
        'title': 'Список команд'
    })


def home(request):
    return render(request, 'events/home.html')


@login_required
def create_participation_request(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    
    if ParticipationRequest.objects.filter(user=request.user, team=team).exists():
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
        return ParticipationRequest.objects.filter(status='pending').select_related('user', 'team')


class ProcessRequestView(TeacherRequiredMixin, UpdateView):
    model = ParticipationRequest
    fields = ['status']
    template_name = 'events/process_request.html'
    success_url = reverse_lazy('request_list')
    
    def form_valid(self, form):
        if form.cleaned_data['status'] == 'approved':
            self.object.team.members.add(self.object.user)
        messages.success(self.request, 'Заявка успешно обработана')
        return super().form_valid(form)


class TeamCreateView(TeacherRequiredMixin, CreateView):
    model = Team
    fields = ['name', 'sport_type', 'captain', 'required_players']
    template_name = 'events/team_form.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Команда успешно создана')
        return reverse('team_list')


class TeamUpdateView(TeacherRequiredMixin, UpdateView):
    model = Team
    fields = ['name', 'sport_type', 'captain', 'required_players']
    template_name = 'events/team_form.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Команда успешно обновлена')
        return reverse('team_list')


class TeamDeleteView(TeacherRequiredMixin, DeleteView):
    model = Team
    template_name = 'events/team_confirm_delete.html'
    success_url = reverse_lazy('team_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Подтверждение удаления команды"
        context['member_count'] = self.object.members.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        team = self.get_object()
        messages.success(request, f'Команда "{team.name}" успешно удалена')
        return super().delete(request, *args, **kwargs)


class EventCreateView(TeacherRequiredMixin, CreateView):
    form_class = EventForm
    template_name = 'events/event_form.html'
    
    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, "Мероприятие успешно создано!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('event_detail', kwargs={'pk': self.object.pk})


class EventUpdateView(TeacherRequiredMixin, UpdateView):
    model = Event
    fields = ['title', 'description', 'sport_type', 'date', 'location']
    template_name = 'events/event_form.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Мероприятие успешно обновлено')
        return reverse('event_list')


class EventDeleteView(TeacherRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Мероприятие успешно удалено')
        return super().delete(request, *args, **kwargs)


class TeamDetailView(DetailView):
    model = Team
    template_name = 'events/team_detail.html'
    context_object_name = 'team'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object
        members = team.members.all()
        
        context.update({
            'captain': team.captain,
            'regular_members': members.exclude(id=team.captain.id),
            'spots_left': max(0, team.required_players - members.count())
        })
        return context


@method_decorator(login_required, name='dispatch')
class TeacherDashboardView(TemplateView):
    template_name = 'teacher/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher:
            return redirect('access_denied')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        context.update({
            'upcoming_events': Event.objects.filter(date__gte=today).order_by('date')[:5],
            'pending_requests': ParticipationRequest.objects.filter(
                status='pending'
            ).select_related('user', 'team')[:5],
            'teams_stats': Team.objects.annotate(
                member_count=Count('members')
            ).filter(captain=self.request.user).order_by('-created_at')[:5],
            'stats': {
                'total_teams': Team.objects.filter(captain=self.request.user).count(),
                'active_events': Event.objects.filter(date__gte=today).count(),
                'pending_requests_count': ParticipationRequest.objects.filter(
                    team__captain=self.request.user,
                    status='pending'
                ).count(),
            }
        })
        return context


class BulkApproveView(TeacherRequiredMixin, View):
    def post(self, request):
        selected = request.POST.getlist('selected_requests')
        
        if not selected:
            messages.warning(request, 'Не выбрано ни одной заявки')
            return redirect('request_list')

        ParticipationRequest.objects.filter(id__in=selected).update(status='approved')
        messages.success(request, f'{len(selected)} заявок одобрено')
        return redirect('request_list')