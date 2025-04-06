from django import forms
from django.utils.translation import gettext_lazy as _
from .models import SportType, Event

class EventFilterForm(forms.Form):
    sport_type = forms.ModelChoiceField(
        queryset=SportType.objects.all(),
        required=False,
        label=_("Вид спорта"),
        empty_label=_("Все виды"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': _('С какой даты')
        }),
        required=False,
        label=_("Дата от")
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': _('По какую дату')
        }),
        required=False,
        label=_("Дата до")
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError(
                _("Дата 'от' должна быть раньше даты 'до'")
            )
        
        return cleaned_data

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'sport_type', 'date', 'location', 'max_participants']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите название мероприятия')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Подробное описание мероприятия')
            }),
            'sport_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }, format='%Y-%m-%dT%H:%M'),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Где будет проходить мероприятие')
            }),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }
        
        labels = {
            'title': _("Название мероприятия"),
            'description': _("Описание"),
            'sport_type': _("Вид спорта"),
            'date': _("Дата и время"),
            'location': _("Место проведения"),
            'max_participants': _("Максимальное количество участников"),
        }
        
        help_texts = {
            'max_participants': _("Укажите 0, если количество участников не ограничено"),
            'date': _("Формат: ДД.ММ.ГГГГ ЧЧ:ММ"),
        }