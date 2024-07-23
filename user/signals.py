from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User
from assignments.models import Assignment

@receiver(post_save, sender=User)
def create_assignment_for_new_user(sender, instance, created, **kwargs):
    if created:
        Assignment.objects.create(user=instance)
