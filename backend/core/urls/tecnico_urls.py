from django.urls import path
from core.views.tecnico_view import TecnicoListCreateView, TecnicoDetailView

urlpatterns = [
    path('tecnicos/', TecnicoListCreateView.as_view(), name='tecnico-list-create'),
    path('tecnicos/<int:pk>/', TecnicoDetailView.as_view(), name='tecnico-detail'),
]
