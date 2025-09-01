from django.urls import path
from . import views
from trimlyapp.views import aceptar_reserva, rechazar_reserva, eliminar_reserva
from django.contrib.auth.views import LogoutView
from trimlyapp.views import borrar_notificacion
from trimlyapp.views import custom_login

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cliente/', views.cliente_view, name='cliente_view'),
    path('cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('barbero/', views.barbero_view, name='barbero_view'),
    path('cambiar_estado/<int:reserva_id>/<str:estado>/', views.cambiar_estado_reserva, name='cambiar_estado'),
    path('register/', views.register, name='register'),
    path('aceptar/<int:reserva_id>/', aceptar_reserva, name='aceptar_reserva'),
    path('rechazar/<int:reserva_id>/', rechazar_reserva, name='rechazar_reserva'),
    path('eliminar/<int:reserva_id>/', eliminar_reserva, name='eliminar_reserva'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('borrar_notificacion/<int:notificacion_id>/', borrar_notificacion, name='borrar_notificacion'),
    path('accounts/login/', custom_login, name='login'),
    path('cambiar_intervalo/', views.cambiar_intervalo, name='cambiar_intervalo'),
]

