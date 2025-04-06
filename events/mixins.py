from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin

class TeacherRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher:
            raise PermissionDenied("Доступ только для преподавателей")
        return super().dispatch(request, *args, **kwargs)