from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from assignments.models import Assignment

@receiver(post_save, sender=User)
def create_assignment(sender, instance, created, **kwargs):
    if created:
        Assignment.objects.create(user=instance, name='untitled')
