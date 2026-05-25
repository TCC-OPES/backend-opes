from django.urls import path
from core.views.familia import FamiliaView

urlpatterns = [
    path('', FamiliaView.as_view()),
]