from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # User 모델을 커스터마이징할 때 필요한 필드들을 설정해요.
    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at')  # created_at과 updated_at을 readonly_fields에 추가

admin.site.register(User, UserAdmin)


# from django.contrib import admin
# from allauth.socialaccount.models import SocialApp

# class SocialAppAdmin(admin.ModelAdmin):
#     list_display = ('name', 'provider', 'client_id', 'secret')
#     list_filter = ('provider',)

# admin.site.unregister(SocialApp)  # 기존 등록을 해제
# admin.site.register(SocialApp, SocialAppAdmin)