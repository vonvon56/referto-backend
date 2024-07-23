from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Assignment

@receiver(post_save, sender=Assignment)
def set_assignment_number(sender, instance, created, **kwargs):
    if created:
        assignments = Assignment.objects.filter(user=instance.user).order_by('assignment_id')
        for index, assignment in enumerate(assignments):
            assignment.number = index + 1
            assignment.save(update_fields=['number'])

@receiver(post_delete, sender=Assignment)
def update_assignment_numbers_on_delete(sender, instance, **kwargs):
    assignments = Assignment.objects.filter(user=instance.user).order_by('assignment_id')
    for index, assignment in enumerate(assignments):
        assignment.number = index + 1
        assignment.save(update_fields=['number'])
