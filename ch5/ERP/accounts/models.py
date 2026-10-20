from django.conf import settings
from django.db import models


class Function(models.Model):
    """A single menu function that can be granted to a role (e.g. PO_VIEW)."""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    functions = models.ManyToManyField(Function, related_name='roles', blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='roles', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
