from django.contrib import admin
from .models import Note, Tag, Attachment


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'user', 'created_at', 'is_favorited')
    list_filter = ('is_favorited', 'created_at', 'user')
    search_fields = ('content',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('tags',)
    inlines = [AttachmentInline]
    
    def short_content(self, obj):
        return obj.short_content
    short_content.short_description = '内容预览'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'color', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'note', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename',)
    date_hierarchy = 'uploaded_at' 