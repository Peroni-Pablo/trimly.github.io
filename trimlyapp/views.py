from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Reservation, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import ReservationForm, CustomUserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Notification
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        role = request.POST.get('role')
        clave_barbero = request.POST.get('clave_barbero')
        error_clave = None

        CLAVE_CORRECTA = "PePeRuLo6798"  # Cambia esto por la clave real

        if role == 'barbero' and clave_barbero != CLAVE_CORRECTA:
            error_clave = "Clave de acceso para barberos incorrecta."

        if form.is_valid() and not error_clave:
            user = form.save()
            Profile.objects.create(user=user, role=role)
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'registration/register.html', {'form': form, 'error_clave': error_clave})
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if not username or not password:
            messages.error(request, "Por favor, completa ambos campos.")
        elif not user:
            from django.contrib.auth.models import User
            if not User.objects.filter(username=username).exists():
                messages.error(request, "este usuario no existe")
            else:
                messages.error(request, "contraseña incorrecta")
        else:
            login(request, user)
            # Redirigir según el rol
            try:
                profile = Profile.objects.get(user=user)
                if profile.role == 'barbero':
                    return redirect('barbero_view')
                else:
                    return redirect('cliente_view')
            except Profile.DoesNotExist:
                return redirect('cliente_view')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role == 'cliente':
        return redirect('cliente_view')
    else:
        return redirect('barbero_view')

@login_required
def cliente_view(request):
    notificaciones = Notification.objects.filter(user=request.user, leida=False).order_by('-fecha')
    abrir_panel = request.session.pop('abrir_panel', False)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.client = request.user
            reserva.accepted = None  # Nueva reserva pendiente

            # Obtener el intervalo del barbero 
            barbero_profile = Profile.objects.filter(role='barbero').first()
            if barbero_profile and getattr(barbero_profile, 'intervalo_turno', None):
                intervalo = int(barbero_profile.intervalo_turno)
                if intervalo < 1:
                    intervalo = 30
            else:
                intervalo = 30  # Valor por defecto si no hay barbero
            # Validar intervalo entre reservas
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            dt_nueva = datetime.combine(date, time)
            reservas_existentes = Reservation.objects.filter(date=date)
            conflicto = False
            for r in reservas_existentes:
                dt_existente = datetime.combine(r.date, r.time)
                diff = abs((dt_nueva - dt_existente).total_seconds()) / 60
                if diff < intervalo:
                    conflicto = True
                    break
            if conflicto:
                form.add_error('time', f'No puede haber dos turnos con menos de {intervalo} minutos de diferencia.')
                messages.error(
                    request,
                    f"No se puede hacer una reserva porque hay poco tiempo entre turnos. El intervalo mínimo permitido es de {intervalo} minutos."
                )
            else:
                reserva.save()
                return redirect('cliente_view')
        else:
            # Mostrar mensaje si el error es por horario pasado
            if form.errors.get('time'):
                messages.error(request, "No puedes reservar un turno para una hora pasada.")
    else:
        form = ReservationForm()
    reservations = Reservation.objects.filter(client=request.user)

    return render(request, 'trimlyapp/reservations.html', {
        'reservations': reservations,
        'form': form,
        'notificaciones': notificaciones,
        'abrir_panel': abrir_panel,
    })
    
@login_required
def cancelar_reserva(request, reserva_id):
    Reservation.objects.get(id=reserva_id, client=request.user).delete()
    return redirect('cliente_view')

@login_required
def barbero_view(request):
    profile = Profile.objects.get(user=request.user)
    reservas = Reservation.objects.all()
    intervalo_actual = profile.intervalo_turno if profile.role == 'barbero' else 30
    return render(request, 'trimlyapp/barber_reservations.html', {
        'reservas': reservas,
        'intervalo_actual': intervalo_actual,
    })
@login_required
def cambiar_estado_reserva(request, reserva_id, estado):
    reserva = Reservation.objects.get(id=reserva_id)
    reserva.accepted = True if estado == 'aceptar' else False
    reserva.save()
    return redirect('barbero_view')

@login_required
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reservation, id=reserva_id)
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'barbero':
        messages.error(request, "No tienes permiso para eliminar esta reserva.")
        return redirect('barbero_view')
    Notification.objects.create(
        user=reserva.client,
        mensaje=f"Tu solicitud para el turno del {reserva.date} a las {reserva.time} fue eliminada por el barbero."
    )
    reserva.delete()
    messages.success(request, "Reserva eliminada correctamente.")
    return redirect('barbero_view')

@login_required
def rechazar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reservation, id=reserva_id)
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'barbero':
        messages.error(request, "No tienes permiso para rechazar esta reserva.")
        return redirect('barbero_view')
    # Crear notificación antes de eliminar
    Notification.objects.create(
        user=reserva.client,
        mensaje=f"Tu solicitud para el turno del {reserva.date} a las {reserva.time} fue rechazada por el barbero."
    )
    reserva.delete()
    messages.success(request, "Reserva rechazada y eliminada correctamente.")
    return redirect('barbero_view')

@login_required
def aceptar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reservation, id=reserva_id)
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'barbero':
        messages.error(request, "No tienes permiso para aceptar esta reserva.")
        return redirect('barbero_view')
    reserva.accepted = True
    reserva.save()
    messages.success(request, "Reserva aceptada correctamente.")
    return redirect('barbero_view')
# Create your views here.

from django.http import HttpResponseRedirect

@login_required
def borrar_notificacion(request, notificacion_id):
    notificacion = get_object_or_404(Notification, id=notificacion_id, user=request.user)
    notificacion.leida = True
    notificacion.save()
    # Indica que el panel debe estar abierto tras recargar
    request.session['abrir_panel'] = True
    return redirect('cliente_view')

@login_required
@require_POST
def cambiar_intervalo(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'barbero':
        messages.error(request, "Solo los barberos pueden cambiar el intervalo.")
        return redirect('barbero_view')
    intervalo = int(request.POST.get('intervalo', 30))
    profile.intervalo_turno = intervalo
    profile.save()
    messages.success(request, "Intervalo actualizado correctamente.")
    return redirect('barbero_view')