from django.urls import path
from . import views

app_name = "recommender"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("suggest/", views.SuggestView.as_view(), name="suggest"),
    path("result/<int:pk>/", views.ResultView.as_view(), name="result"),
    path("history/", views.HistoryView.as_view(), name="history"),
]
