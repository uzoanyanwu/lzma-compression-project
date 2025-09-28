from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_filename = models.CharField(max_length=255)
    original_file_size = models.BigIntegerField()  # Size in bytes
    upload_timestamp = models.DateTimeField(default=timezone.now)
    file_path = models.CharField(max_length=500)  # Path to uploaded file

    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"


class CompressionResult(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE)
    compressed_filename = models.CharField(max_length=255)
    compressed_file_size = models.BigIntegerField()  # Size in bytes
    compression_ratio = models.FloatField()  # Percentage compression
    compression_time = models.FloatField()  # Time in seconds
    download_link = models.CharField(max_length=500)  # URL for download
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Compression of {self.file.original_filename}"

    @property
    def compression_percentage(self):
        """Return compression ratio as percentage"""
        return round((1 - (self.compressed_file_size / self.file.original_file_size)) * 100, 2)

    @property
    def formatted_compression_time(self):
        """Return formatted compression time"""
        if self.compression_time < 60:
            return f"{self.compression_time:.2f} seconds"
        elif self.compression_time < 3600:
            minutes = int(self.compression_time // 60)
            seconds = int(self.compression_time % 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"
        else:
            hours = int(self.compression_time // 3600)
            minutes = int((self.compression_time % 3600) // 60)
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
