# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Paper

@receiver(post_save, sender=Paper)
def set_paper_number(sender, instance, created, **kwargs):
    if created:
        papers = Paper.objects.filter(assignment=instance.assignment).order_by('paper_id')
        for index, paper in enumerate(papers):
            paper.number = index + 1
            paper.save(update_fields=['number'])

@receiver(post_delete, sender=Paper)
def update_paper_numbers_on_delete(sender, instance, **kwargs):
    papers = Paper.objects.filter(assignment=instance.assignment).order_by('paper_id')
    for index, paper in enumerate(papers):
        paper.number = index + 1
        paper.save(update_fields=['number'])
