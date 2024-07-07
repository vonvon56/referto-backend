from django.db import models
from papers.models import Paper

class PaperInfo(models.Model):
    paperInfo_id = models.AutoField(primary_key=True)  # 자동 증가 ID 필드
    reference = models.TextField()  # 인용 필드
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)  # 문서와의 관계 설정

    def __str__(self):
        return f'Info for Paper {self.paper.paper_id}'
