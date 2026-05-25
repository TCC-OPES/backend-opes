from django.urls import path

from core.views import MetaFinanceiraView

urlpatterns = [
    path('', MetaFinanceiraView.as_view()),
]