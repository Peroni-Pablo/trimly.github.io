from django import forms
from .models import Reservation
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re



class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError("No puedes reservar un turno para una fecha pasada.")
        return date

    def clean_time(self):
        date = self.cleaned_data.get('date')
        time = self.cleaned_data['time']
        now = datetime.datetime.now()
        # Si la fecha es hoy, no permitir horas pasadas
        if date == now.date() and time < now.time():
            raise forms.ValidationError("No puedes reservar un turno para una hora pasada.")
        return time
    
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("La contraseña debe contener al menos un número.")
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("el nombre ya esta en uso")
        return username

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError("No puedes reservar un turno para una fecha pasada.")
        return date

    def clean_time(self):
        date = self.cleaned_data.get('date')
        time = self.cleaned_data['time']
        now = datetime.datetime.now()
        # Si la fecha es hoy, no permitir horas pasadas
        if date == now.date() and time < now.time():
            raise forms.ValidationError("No puedes reservar un turno para una hora pasada.")
        return time
    
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("La contraseña debe contener al menos un número.")
        return password