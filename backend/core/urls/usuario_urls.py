from django.urls import path
from core.views.usuario_view import UsuarioListCreateView, UsuarioDetailView

urlpatterns = [
    path('usuarios/', UsuarioListCreateView.as_view(), name='usuario-list-create'),
    path('usuarios/<int:pk>/', UsuarioDetailView.as_view(), name='usuario-detail'),
]
