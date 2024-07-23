from django.db import models
from user.models import User

class Assignment(models.Model):
    APA = 'APA'
    CHICAGO = 'Chicago'
    VANCOUVER = 'Vancouver'
    MLA = 'MLA'

    REFERENCE_CHOICES = [
        (APA, 'APA'),
        (CHICAGO, 'Chicago'),
        (VANCOUVER, 'Vancouver'),
        (MLA, 'MLA'),
    ]

    assignment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default='untitled')
    number = models.PositiveIntegerField(editable=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference_type = models.CharField(max_length=10, choices=REFERENCE_CHOICES, default=APA)

    def save(self, *args, **kwargs):
        if self.number is None:
            self.number = Assignment.objects.filter(user=self.user).count() + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        assignments = Assignment.objects.filter(user=user).order_by('assignment_id')
        for index, assignment in enumerate(assignments):
            assignment.number = index + 1
            assignment.save(update_fields=['number'])
