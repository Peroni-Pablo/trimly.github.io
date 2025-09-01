from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    intervalo_turno = models.PositiveIntegerField(default=30)  # minutos

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Reservation(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    accepted = models.BooleanField(null=True, default=None)  # None=pending, True=accepted, False=rejected

    class Meta:
        unique_together = ('date', 'time')

    def __str__(self):
        return f"{self.client.username} - {self.date} {self.time}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
# Create your models here.

