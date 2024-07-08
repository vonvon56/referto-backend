from django.db import models
from django.contrib.auth.models import User

class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)  # 자동 증가 ID 필드
    name = models.CharField(max_length=255)  # 과제 이름 필드
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와의 관계 설정

    def __str__(self):
        return self.name
