from django.urls import path
from . import views

urlpatterns = [
    # Homepage & registration
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    # Articles
    path('articles/create/', views.create_article, name='create_article'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/<int:pk>/edit/', views.update_article, name='update_article'),
    path('articles/<int:pk>/delete/', views.delete_article, name='delete_article'),

    # Publishers
    path('publishers/register/', views.register_publisher, name='register_publisher'),
    path('publishers/<int:publisher_id>/subscribe/', views.subscribe_publisher, name='subscribe_publisher'),
    path('publishers/<int:publisher_id>/unsubscribe/', views.unsubscribe_publisher, name='unsubscribe_publisher'),

    # Journalists (subscriptions)
    path('journalists/<int:journalist_id>/subscribe/', views.subscribe_journalist, name='subscribe_journalist'),
    path('journalists/<int:journalist_id>/unsubscribe/', views.unsubscribe_journalist, name='unsubscribe_journalist'),

    # Editor dashboard & approvals
    path('editor/', views.editor_dashboard, name='editor_dashboard'),
    path('editor/approve/<int:article_id>/', views.approve_article, name='approve_article'),

    # Subscriptions page
    path('subscriptions/', views.subscriptions, name='subscriptions'),

    # Newsletter CRUD (journalists only)
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/create/', views.newsletter_create, name='newsletter_create'),
    path('newsletters/<int:pk>/edit/', views.newsletter_update, name='newsletter_update'),
    path('newsletters/<int:pk>/delete/', views.newsletter_delete, name='newsletter_delete'),

    # API
    path('api/subscribed-articles/', views.get_subscribed_articles, name='get_subscribed_articles'),
]





