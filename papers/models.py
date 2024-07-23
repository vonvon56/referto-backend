from django.db import models
from assignments.models import Assignment

class Paper(models.Model):
    paper_id = models.AutoField(primary_key=True)  # 자동 증가 ID 필드
    number = models.PositiveIntegerField(editable=False, null=True)  # 사용자 입력 불가
    pdf = models.FileField(upload_to='api/papers/')  # PDF 파일 업로드 필드
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)  # 과제와의 관계 설정
    created_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # 먼저 저장하여 paper_id 생성
        if self.number is None:
            self.number = Paper.objects.filter(assignment=self.assignment).count()
            super().save(update_fields=['number'])

    def __str__(self):
        return f'Paper {self.paper_id} for {self.assignment.name}'
    
    def delete(self, *args, **kwargs):
        assignment = self.assignment
        super().delete(*args, **kwargs)
        papers = Paper.objects.filter(assignment=assignment).order_by('paper_id')
        for index, paper in enumerate(papers):
            paper.number = index + 1
            paper.save(update_fields=['number'])
