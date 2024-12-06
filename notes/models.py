from django.db import models
from papers.models import Paper

class Note(models.Model):
  note_id = models.AutoField(primary_key=True) # 자동 증가 ID 필드
  paper = models.ForeignKey(Paper, on_delete=models.CASCADE) # paper와의 관계 설정
  content = models.TextField(blank=True)
  highlightAreas = models.JSONField()
  quote = models.TextField(blank=True, null=True)
  def __str__(self):
        return f'Note {self.note_id} for Paper {self.paper.paper_id}'