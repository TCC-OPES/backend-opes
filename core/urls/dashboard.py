from django.urls import path
from core.views.dashboard import DashboardView

urlpatterns = [
    path('resumo/', DashboardView.as_view()),
]