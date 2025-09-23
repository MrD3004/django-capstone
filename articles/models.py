from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
        ('publisher', 'Publisher'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Readers can subscribe to publishers and journalists
    subscribed_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='subscribed_readers'
    )
    subscribed_journalists = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='followers'
    )

    # Override groups/permissions to avoid clashes with AbstractUser
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    owner = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='owned_publisher',
        limit_choices_to={'role': 'publisher'}
    )
    editors = models.ManyToManyField(
        CustomUser,
        related_name='editor_publishers',
        blank=True,
        limit_choices_to={'role': 'editor'}
    )
    journalists = models.ManyToManyField(
        CustomUser,
        related_name='journalist_publishers',
        blank=True,
        limit_choices_to={'role': 'journalist'}
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'journalist'}
    )
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({'Approved' if self.approved else 'Pending'})"


class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'journalist'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"

    def __str__(self):
        return self.title


