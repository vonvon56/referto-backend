from django.db import models
from assignments.models import Assignment

class Paper(models.Model):
    paper_id = models.AutoField(primary_key=True)  # 자동 증가 ID 필드
    pdf = models.FileField(upload_to='papers/')  # PDF 파일 필드
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)  # 과제와의 관계 설정
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Paper {self.paper_id} for {self.assignment.name}'
