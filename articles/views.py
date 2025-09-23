from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Article, Publisher, CustomUser, Newsletter
from .forms import (
    ArticleForm,
    CustomUserCreationForm,
    PublisherForm,
    NewsletterForm,
)
from .serializers import ArticleSerializer


# ---------------------------
# Role check helpers
# ---------------------------
def is_editor(user):
    return user.is_authenticated and getattr(user, "role", None) == "editor"

def is_journalist(user):
    return user.is_authenticated and getattr(user, "role", None) == "journalist"

def is_reader(user):
    return user.is_authenticated and getattr(user, "role", None) == "reader"

def is_publisher(user):
    return user.is_authenticated and getattr(user, "role", None) == "publisher"


# ---------------------------
# User Registration
# ---------------------------
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})


# ---------------------------
# Homepage
# ---------------------------
def home(request):
    if is_reader(request.user):
        articles = (
            Article.objects.filter(
                approved=True,
                publisher__in=request.user.subscribed_publishers.all(),
            )
            | Article.objects.filter(
                approved=True,
                author__in=request.user.subscribed_journalists.all(),
            )
        ).distinct().order_by("-id")
    else:
        articles = Article.objects.filter(approved=True).order_by("-id")

    return render(request, "homepage.html", {"articles": articles})


# ---------------------------
# Article detail
# ---------------------------
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, "article_detail.html", {"article": article})


# ---------------------------
# Create article (journalists only)
# ---------------------------
@login_required
@user_passes_test(is_journalist)
def create_article(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect("home")
    else:
        form = ArticleForm()
    return render(request, "create_article.html", {"form": form})


# ---------------------------
# Register publisher (publisher role)
# ---------------------------
@login_required
@user_passes_test(is_publisher)
def register_publisher(request):
    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save(commit=False)
            publisher.owner = request.user
            publisher.save()
            return redirect("home")
    else:
        form = PublisherForm()
    return render(request, "register_publisher.html", {"form": form})


# ---------------------------
# Editor dashboard
# ---------------------------
@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    articles = Article.objects.filter(approved=False).order_by("-id")
    return render(request, "editor_dashboard.html", {"articles": articles})


# ---------------------------
# Approve article (editors only)
# ---------------------------
@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()

    # Hook for Twitter/X integration
    try:
        from .utils import post_to_twitter
        post_to_twitter(article)
    except Exception as e:
        print("[Twitter] Post failed:", e)

    return redirect("editor_dashboard")


# ---------------------------
# Update article (editors only)
# ---------------------------
@login_required
@user_passes_test(is_editor)
def update_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect("editor_dashboard")
    else:
        form = ArticleForm(instance=article)
    return render(request, "update_article.html", {"form": form, "article": article})


# ---------------------------
# Delete article (editors only)
# ---------------------------
@login_required
@user_passes_test(is_editor)
def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.delete()
        return redirect("editor_dashboard")
    return render(request, "confirm_delete.html", {"article": article})


# ---------------------------
# Newsletter CRUD (journalists only)
# ---------------------------
@login_required
@user_passes_test(is_journalist)
def newsletter_list(request):
    newsletters = Newsletter.objects.filter(author=request.user)
    return render(request, "newsletters/list.html", {"newsletters": newsletters})

@login_required
@user_passes_test(is_journalist)
def newsletter_create(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            return redirect("newsletter_list")
    else:
        form = NewsletterForm()
    return render(
        request,
        "newsletters/form.html",
        {"form": form, "object_name": "Newsletter", "cancel_url": "newsletter_list"},
    )

@login_required
@user_passes_test(is_journalist)
def newsletter_update(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk, author=request.user)
    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            return redirect("newsletter_list")
    else:
        form = NewsletterForm(instance=newsletter)
    return render(
        request,
        "newsletters/form.html",
        {"form": form, "object_name": "Newsletter", "cancel_url": "newsletter_list"},
    )

@login_required
@user_passes_test(is_journalist)
def newsletter_delete(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk, author=request.user)
    if request.method == "POST":
        newsletter.delete()
        return redirect("newsletter_list")
    return render(request, "newsletters/confirm_delete.html", {"newsletter": newsletter})


# ---------------------------
# API: Subscribed articles
# ---------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_subscribed_articles(request):
    user = request.user
    if is_reader(user):
        articles = (
            Article.objects.filter(
                publisher__in=user.subscribed_publishers.all(), approved=True
            )
            | Article.objects.filter(
                author__in=user.subscribed_journalists.all(), approved=True
            )
        ).distinct().order_by("-id")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)
    return Response({"detail": "Not a reader"}, status=403)


# ---------------------------
# Subscriptions page
# ---------------------------
@login_required
def subscriptions(request):
    publishers = request.user.subscribed_publishers.all()
    journalists = request.user.subscribed_journalists.all()
    return render(
        request,
        "subscriptions.html",
        {"publishers": publishers, "journalists": journalists},
    )


# ---------------------------
# Subscribe / Unsubscribe to publisher
# ---------------------------
@login_required
def subscribe_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    request.user.subscribed_publishers.add(publisher)
    return redirect("subscriptions")

@login_required
def unsubscribe_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, id=publisher_id)
    request.user.subscribed_publishers.remove(publisher)
    return redirect("subscriptions")


# ---------------------------
# Subscribe / Unsubscribe to journalist
# ---------------------------
@login_required
def subscribe_journalist(request, journalist_id):
    journalist = get_object_or_404(CustomUser, id=journalist_id, role="journalist")
    request.user.subscribed_journalists.add(journalist)
    return redirect("subscriptions")

@login_required
def unsubscribe_journalist(request, journalist_id):
    journalist = get_object_or_404(CustomUser, id=journalist_id, role="journalist")
    request.user.subscribed_journalists.remove(journalist)
    return redirect("subscriptions")








