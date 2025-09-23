from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article
from django.core.mail import send_mail

def create_roles():
    reader_group, _ = Group.objects.get_or_create(name='Reader')
    editor_group, _ = Group.objects.get_or_create(name='Editor')
    journalist_group, _ = Group.objects.get_or_create(name='Journalist')

    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    reader_group.permissions.set([
        Permission.objects.get(codename='view_article'),
        Permission.objects.get(codename='view_newsletter'),
    ])
    editor_group.permissions.set([
        Permission.objects.get(codename='change_article'),
        Permission.objects.get(codename='delete_article'),
        Permission.objects.get(codename='view_article'),
        Permission.objects.get(codename='change_newsletter'),
        Permission.objects.get(codename='delete_newsletter'),
        Permission.objects.get(codename='view_newsletter'),
    ])
    journalist_group.permissions.set([
        Permission.objects.get(codename='add_article'),
        Permission.objects.get(codename='change_article'),
        Permission.objects.get(codename='delete_article'),
        Permission.objects.get(codename='view_article'),
        Permission.objects.get(codename='add_newsletter'),
        Permission.objects.get(codename='change_newsletter'),
        Permission.objects.get(codename='delete_newsletter'),
        Permission.objects.get(codename='view_newsletter'),
    ])

@receiver(post_save, sender=Article)
def notify_subscribers(sender, instance, created, **kwargs):
    if instance.approved:
        subscribers = instance.author.subscriptions_to_journalists.all()
        for user in subscribers:
            send_mail(
                subject=f"New Article: {instance.title}",
                message=instance.content[:200],
                from_email='news@portal.com',
                recipient_list=[user.email],
            )
