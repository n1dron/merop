from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class SportType(models.Model):
    name = models.CharField(_("Название вида спорта"), max_length=100)
    
    class Meta:
        verbose_name = _("Вид спорта")
        verbose_name_plural = _("Виды спорта")
    
    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(_("Название мероприятия"), max_length=200)
    description = models.TextField(_("Описание"))
    sport_type = models.ForeignKey(
        SportType, 
        on_delete=models.CASCADE,
        verbose_name=_("Вид спорта")
    )
    date = models.DateTimeField(_("Дата и время проведения"))
    location = models.CharField(_("Место проведения"), max_length=200)
    organizer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='organized_events',
        verbose_name=_("Организатор")
    )
    equipment = models.TextField(_("Необходимое оборудование"), blank=True)
    max_participants = models.PositiveIntegerField(
        _("Максимальное количество участников"),
        default=0,
        help_text=_("0 означает без ограничений")
    )
    max_teams = models.PositiveIntegerField(
        _("Максимальное количество команд"),
        default=0
    )
    results_published = models.BooleanField(
        _("Результаты опубликованы"),
        default=False
    )
    
    class Meta:
        verbose_name = _("Мероприятие")
        verbose_name_plural = _("Мероприятия")
        ordering = ['-date']
    
    def __str__(self):
        return self.title

class Qualification(models.Model):
    name = models.CharField(_("Название квалификации"), max_length=100)
    description = models.TextField(_("Описание"))
    
    class Meta:
        verbose_name = _("Квалификация")
        verbose_name_plural = _("Квалификации")
    
    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(_("Название команды"), max_length=100)
    sport_type = models.ForeignKey(
        SportType, 
        on_delete=models.CASCADE,
        verbose_name=_("Вид спорта")
    )
    captain = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='captained_teams',
        verbose_name=_("Капитан")
    )
    members = models.ManyToManyField(
        User, 
        related_name='teams',
        verbose_name=_("Участники")
    )
    required_players = models.PositiveIntegerField(
        _("Требуемое количество участников"),
        help_text=_("Минимальное количество игроков в команде")
    )
    
    class Meta:
        verbose_name = _("Команда")
        verbose_name_plural = _("Команды")
    
    def __str__(self):
        return self.name

class ParticipationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Ожидает рассмотрения')),
        ('approved', _('Одобрена')),
        ('rejected', _('Отклонена')),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь")
    )
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE,
        verbose_name=_("Команда")
    )
    status = models.CharField(
        _("Статус заявки"),
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Заявка на участие")
        verbose_name_plural = _("Заявки на участие")
    
    def __str__(self):
        return f"{self.user} -> {self.team}"

