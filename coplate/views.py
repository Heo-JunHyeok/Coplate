from django.shortcuts import render, get_object_or_404
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
from .models import Review, User
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


class ProfileView(DetailView):
    model = User
    template_name = "coplate/profile.html"
    pk_url_kwarg = "user_id"
    context_object_name = "profile_user"
    # default 값인 user는 현재 유저를 참조하는 것으로 사용했기 때문에
    # 충돌하는 것을 방지하기 위해 context_object_name 사용

    # 모델을 User로 설정했기 때문에 템플릿에 review가 넘어가지 않기 때문에
    # context에 review 데이터를 포함시키기 위해 사용
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get("user_id")
        context["user_reviews"] = Review.objects.filter(author__id=user_id).order_by(
            "-dt_created"
        )[:4]
        return context


class UserReviewListView(ListView):
    model = Review
    template_name = "coplate/user_review_list.html"
    context_object_name = "user_reviews"
    paginate_by = 4

    # ListView는 모든 object 값을 가져오기 때문에
    # 원하는 유저의 list만 템플릿에 넘기기 위해 아래 메소드를 오버라이딩
    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return Review.objects.filter(author__id=user_id).order_by("-dt_created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = get_object_or_404(User, id=self.kwargs.get("user_id"))
        return context


class CustomPasswordChangeView(PasswordChangeView):
    def get_success_url(self):
        return reverse("index")
