from django.contrib import admin
from django.urls import path, include
from recommender.views import RegisterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("", include("recommender.urls")),
]
