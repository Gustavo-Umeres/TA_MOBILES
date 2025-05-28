from django.urls import path
from core.views.solicitud_view import SolicitudListCreateView, SolicitudDetailView

urlpatterns = [
    path('solicitudes/', SolicitudListCreateView.as_view(), name='solicitud-list-create'),
    path('solicitudes/<int:pk>/', SolicitudDetailView.as_view(), name='solicitud-detail'),
]
