from django.contrib import admin
from .models import Assignment   # 추가

from django.contrib import admin
from .models import Assignment

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['assignment_id', 'name', 'user', 'reference_type', 'number']  # 실제 필드명으로 대체
    search_fields = ['assignment_id']

admin.site.register(Assignment, AssignmentAdmin)
