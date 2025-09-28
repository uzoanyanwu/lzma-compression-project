from django.contrib import admin
from .models import File, CompressionResult


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'original_file_size', 'upload_timestamp')
    list_filter = ('upload_timestamp', 'user')
    search_fields = ('original_filename', 'user__username')
    readonly_fields = ('upload_timestamp',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(CompressionResult)
class CompressionResultAdmin(admin.ModelAdmin):
    list_display = ('file', 'compressed_filename', 'compression_ratio', 'compression_time', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('file__original_filename', 'compressed_filename')
    readonly_fields = ('timestamp',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('file', 'file__user')
