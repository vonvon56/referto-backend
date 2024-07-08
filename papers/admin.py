from django.contrib import admin
from .models import Paper   # 추가


class PaperAdmin(admin.ModelAdmin):
    list_display = ['paper_id', 'pdf', 'assignment']  # 실제 필드명으로 대체
    search_fields = ['assignment_id']
admin.site.register(Paper, PaperAdmin)
