from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_student = models.BooleanField(default=True)
    is_teacher = models.BooleanField(default=False)
    
    @property
    def is_staff_or_teacher(self):
        return self.is_staff or self.is_teacher
    
    def __str__(self):
        return self.username
    
