from django.db import models

class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # 자동 증가 ID 필드
    email = models.EmailField(unique=True)  # 이메일 필드, 고유값
    password = models.CharField(max_length=128)  # 비밀번호 필드

    def __str__(self):
        return self.email
