from django.shortcuts import render
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from braces.views import LoginRequiredMixin, UserPassesTestMixin
from allauth.account.models import EmailAddress
from allauth.account.views import PasswordChangeView
from .forms import ReviewForm
from .models import Review
from .functions import confirmation_required_redirect


class IndexView(ListView):
    model = Review
    template_name = "coplate/index.html"
    context_object_name = "reviews"
    paginate_by = 4
    ordering = ["-dt_created"]


class ReviewDetailView(DetailView):
    model = Review
    template_name = "coplate/review_detail.html"
    pk_url_kwarg = "review_id"


class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "coplate/review_form.html"

    # 인증되지 않은 유저 처리 방법
    redirect_unauthenticated_users = True
    raise_exception = confirmation_required_redirect

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})

    # UserPassesTestMixin
    def test_func(self, user):
        return EmailAddress.objects.filter(user=user, verified=True).exists()


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "coplate/review_form.html"
    pk_url_kwarg = "review_id"

    raise_exception = True

    def get_success_url(self):
        return reverse("review-detail", kwargs={"review_id": self.object.id})

    def test_func(self, user):
        review = self.get_object()
        return review.author == user


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = "coplate/review_confirm_delete.html"
    pk_url_kwarg = "review_id"

    raise_exception = True

    def get_success_url(self):
        return reverse("index")

    def test_func(self, user):
        review = self.get_object()
        return review.author == user


class CustomPasswordChangeView(PasswordChangeView):
    def get_success_url(self):
        return reverse("index")
