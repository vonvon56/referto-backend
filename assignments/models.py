from django.db import models
from user.models import User

class Assignment(models.Model):
    # 저장되는 값
    APA = 'APA'
    CHICAGO = 'Chicago'
    VANCOUVER = 'Vancouver'
    MLA = 'MLA'
    # 선택지로 제공되는 값
    REFERENCE_CHOICES = [
        (APA, 'APA'),
        (CHICAGO, 'Chicago'),
        (VANCOUVER, 'Vancouver'),
        (MLA, 'MLA'),
    ]

    assignment_id = models.AutoField(primary_key=True)  # 자동 증가 ID 필드
    name = models.CharField(max_length=255, default='untitled')  # 과제 이름 필드
    number = models.PositiveIntegerField(editable=False, null=True)  # 사용자 입력 불가
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와의 관계 설정
    reference_type = models.CharField(max_length=10, choices=REFERENCE_CHOICES, default=APA)  # 참고문헌 형식 필드

    def save(self, *args, **kwargs):
        if self.number is None:
            self.number = Assignment.objects.filter(user=self.user).count() + 1
        super().save(*args, **kwargs)  # 먼저 저장하여 assignment_id 생성

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        assignments = Assignment.objects.filter(user=user).order_by('assignment_id')
        for index, assignment in enumerate(assignments):
            assignment.number = index + 1
            assignment.save(update_fields=['number'])
