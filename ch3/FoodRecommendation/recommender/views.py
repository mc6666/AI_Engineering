from django.views.generic import TemplateView, View, ListView, CreateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

from .models import YouTuber, FoodSuggestion
from . import services


class IndexView(TemplateView):
    template_name = "recommender/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["youtubers"] = YouTuber.objects.all()
        return ctx


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("recommender:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"歡迎，{self.object.username}！帳號已建立。")
        return response


class SuggestView(View):
    def post(self, request):
        youtuber_ids = request.POST.getlist("youtuber_ids")
        user_query = request.POST.get("user_query", "").strip()

        if not youtuber_ids:
            messages.error(request, "請至少選擇一位 YouTuber。")
            return redirect("recommender:index")
        if not user_query:
            messages.error(request, "請輸入你想吃什麼。")
            return redirect("recommender:index")

        youtubers = YouTuber.objects.filter(pk__in=youtuber_ids)
        if not youtubers.exists():
            messages.error(request, "找不到所選的 YouTuber。")
            return redirect("recommender:index")

        ai_response = services.get_suggestions(list(youtubers), user_query)

        if not request.session.session_key:
            request.session.create()

        suggestion = FoodSuggestion.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            user_query=user_query,
            ai_response=ai_response,
        )
        suggestion.youtubers.set(youtubers)

        return redirect("recommender:result", pk=suggestion.pk)

    def get(self, request):
        return redirect("recommender:index")


class ResultView(TemplateView):
    template_name = "recommender/result.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["suggestion"] = get_object_or_404(FoodSuggestion, pk=self.kwargs["pk"])
        return ctx


class HistoryView(ListView):
    template_name = "recommender/history.html"
    context_object_name = "suggestions"
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return FoodSuggestion.objects.filter(
                user=self.request.user
            ).prefetch_related("youtubers")
        if not self.request.session.session_key:
            return FoodSuggestion.objects.none()
        return FoodSuggestion.objects.filter(
            session_key=self.request.session.session_key
        ).prefetch_related("youtubers")
