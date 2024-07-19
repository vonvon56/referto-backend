from django.db import models
from django.contrib.auth.models import User

class Assignment(models.Model):
    # 저장되는 값
    APA = 'apa'
    CHICAGO = 'chicago'
    VANCOUVER = 'vancouver'
    MLA = 'mla'
    # 선택지로 제공되는 값
    REFERENCE_CHOICES = [
        (APA, 'APA'),
        (CHICAGO, 'Chicago'),
        (VANCOUVER, 'Vancouver'),
        (MLA, 'MLA'),
    ]

    assignment_id = models.AutoField(primary_key=True)  # 자동 증가 ID 필드
    name = models.CharField(max_length=255, default='untitled')  # 과제 이름 필드
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와의 관계 설정
    reference_type = models.CharField(max_length=10, choices=REFERENCE_CHOICES, default=APA)  # 참고문헌 형식 필드
    
    def __str__(self):
        return self.name
