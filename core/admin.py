from django.contrib import admin
from .models import AgreementType, Agreement, Photo


@admin.register(AgreementType)
class AgreementTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ['id', 'agreement_type', 'participants', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'agreement_type', 'is_archived', 'created_at']
    search_fields = ['participants', 'agreement_text']
    readonly_fields = ['session_key', 'created_at', 'signed_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('agreement_type', 'participants', 'status')
        }),
        ('Content', {
            'fields': ('agreement_text', 'edited_text')
        }),
        ('Conversation', {
            'fields': ('conversation_history',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('session_key', 'created_at', 'signed_at', 'completed_at', 'is_archived')
        }),
    )


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'agreement', 'uploaded_at']
    list_filter = ['uploaded_at']
    readonly_fields = ['uploaded_at']
    date_hierarchy = 'uploaded_at'