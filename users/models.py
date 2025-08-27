from django.contrib.auth.models import AbstractUser
from django.db import models

class Roles(models.TextChoices):
    CLIENT = "client", "Client"
    WORKER = "worker", "Worker"
    ADMIN = "admin", "Admin"

class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    ANY = "any", "Any"

class User(AbstractUser):
    role = models.CharField(max_length=16, choices=Roles.choices, default=Roles.CLIENT)
    # Worker profiling
    specialty = models.CharField(max_length=64, blank=True, default="")
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.ANY)

    def __str__(self):
        return f"{self.username} ({self.role})"
